"""
Audio processing module for educational lectures, podcasts, and recordings.

Uses Azure Speech-to-Text to create real timestamped transcripts.
The resulting transcript segments are normalized into the same structure
used by the PDF/video RAG pipeline.
"""

import os
import time
import threading
from pathlib import Path
from typing import List, Dict, Any, Optional

import azure.cognitiveservices.speech as speechsdk

from backend.processing.base import (
    NormalizedContentItem,
    MultimodalProcessingResult,
    ContentValidationError,
)
from backend.rag.cleaner import ContentCleaner
from backend.utils.helpers import format_timestamp


class AudioProcessor:
    """
    Processes educational audio files using Azure Speech-to-Text.

    Supported:
        .mp3
        .wav
        .m4a
        .aac
        .flac
        .ogg
    """

    SUPPORTED_EXTENSIONS = {
        ".mp3",
        ".wav",
        ".m4a",
        ".aac",
        ".flac",
        ".ogg",
    }

    MAX_FILE_SIZE_BYTES = 200 * 1024 * 1024  # 200 MB

    @classmethod
    def validate_file(cls, file_path: str) -> bool:
        """
        Validate audio file existence, size, extension and basic headers.
        """

        if not os.path.exists(file_path):
            raise ContentValidationError(
                f"Audio file not found: {file_path}"
            )

        file_size = os.path.getsize(file_path)

        if file_size == 0:
            raise ContentValidationError(
                f"Audio file '{Path(file_path).name}' is empty."
            )

        if file_size > cls.MAX_FILE_SIZE_BYTES:
            raise ContentValidationError(
                f"Audio file exceeds maximum size of 200MB "
                f"({file_size / (1024 * 1024):.1f}MB)."
            )

        ext = Path(file_path).suffix.lower()

        if ext not in cls.SUPPORTED_EXTENSIONS:
            raise ContentValidationError(
                f"Unsupported audio format '{ext}'. "
                f"Supported formats: {', '.join(sorted(cls.SUPPORTED_EXTENSIONS))}"
            )

        # Basic binary signature validation
        with open(file_path, "rb") as f:
            header = f.read(32)

        if ext == ".wav" and not header.startswith(b"RIFF"):
            raise ContentValidationError(
                "Invalid WAV file: missing RIFF header."
            )

        if ext == ".flac" and not header.startswith(b"fLaC"):
            raise ContentValidationError(
                "Invalid FLAC file: missing fLaC header."
            )

        if ext == ".ogg" and not header.startswith(b"OggS"):
            raise ContentValidationError(
                "Invalid OGG file: missing OggS header."
            )

        return True

    @classmethod
    def process(cls, file_path: str) -> Dict[str, Any]:
        """
        Transcribe audio using Azure Speech-to-Text and return
        timestamped educational chunks.
        """

        filename = Path(file_path).name

        # ---------------------------------------------------------
        # 1. Validate
        # ---------------------------------------------------------

        try:
            cls.validate_file(file_path)

        except ContentValidationError as exc:
            return cls._create_error_result(filename, str(exc))

        except Exception as exc:
            return cls._create_error_result(
                filename,
                f"Audio validation failed: {exc}",
            )

        # ---------------------------------------------------------
        # 2. Load Azure Speech configuration
        # ---------------------------------------------------------

        speech_key = os.getenv("SPEECH_KEY")
        speech_endpoint = os.getenv("SPEECH_ENDPOINT")
        speech_region = os.getenv("SPEECH_REGION")
        speech_language = os.getenv(
            "SPEECH_LANGUAGE",
            "en-US",
        )

        if not speech_key:
            return cls._create_error_result(
                filename,
                "SPEECH_KEY is missing from .env",
            )

        if not speech_endpoint and not speech_region:
            return cls._create_error_result(
                filename,
                "SPEECH_ENDPOINT or SPEECH_REGION is missing from .env",
            )

        # ---------------------------------------------------------
        # 3. Create Speech configuration
        # ---------------------------------------------------------

        try:

            speech_config = speechsdk.SpeechConfig(
                subscription=speech_key,
                region=speech_region,
            )

            speech_config.speech_recognition_language = speech_language

            # Request detailed timing information.
            speech_config.set_property(
                speechsdk.PropertyId.SpeechServiceResponse_RequestWordLevelTimestamps,
                "true",
            )

            audio_config = speechsdk.audio.AudioConfig(
                filename=file_path
            )

            recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config,
                audio_config=audio_config,
            )

        except Exception as exc:
            return cls._create_error_result(
                filename,
                f"Failed to initialize Azure Speech: {exc}",
            )

        # ---------------------------------------------------------
        # 4. Collect real transcript segments
        # ---------------------------------------------------------

        segments: List[Dict[str, Any]] = []
        done = threading.Event()
        error_message: List[str] = []

        def recognized_callback(evt):
            """
            Called whenever Azure produces a final recognized utterance.
            """

            try:
                result = evt.result

                if result.reason != speechsdk.ResultReason.RecognizedSpeech:
                    return

                text = (result.text or "").strip()

                if not text:
                    return

                # Azure timestamps are in 100-nanosecond ticks.
                start_seconds = result.offset / 10_000_000
                duration_seconds = result.duration / 10_000_000
                end_seconds = start_seconds + duration_seconds

                segments.append(
                    {
                        "start": round(start_seconds, 2),
                        "end": round(end_seconds, 2),
                        "text": text,
                    }
                )

            except Exception as exc:
                error_message.append(
                    f"Failed to process recognition result: {exc}"
                )

        def canceled_callback(evt):
            """
            Called if Azure cancels recognition.
            """

            try:
                details = evt.cancellation_details

                if details.reason == speechsdk.CancellationReason.Error:
                    error_message.append(
                        f"Azure Speech error: {details.error_details}"
                    )
                else:
                    error_message.append(
                        f"Azure Speech recognition canceled: {details.reason}"
                    )

            except Exception as exc:
                error_message.append(
                    f"Speech cancellation error: {exc}"
                )

            finally:
                done.set()

        def session_stopped_callback(evt):
            """
            Called when the audio file has finished processing.
            """

            done.set()

        # ---------------------------------------------------------
        # 5. Connect Azure events
        # ---------------------------------------------------------

        recognizer.recognized.connect(recognized_callback)
        recognizer.canceled.connect(canceled_callback)
        recognizer.session_stopped.connect(session_stopped_callback)

        # ---------------------------------------------------------
        # 6. Start continuous recognition
        # ---------------------------------------------------------

        try:

            recognizer.start_continuous_recognition()

            # Maximum processing wait.
            # 1 hour prevents the backend from hanging forever.
            max_wait_seconds = 3600

            start_wait = time.time()

            while not done.is_set():

                if time.time() - start_wait > max_wait_seconds:
                    error_message.append(
                        "Audio transcription timed out."
                    )
                    break

                time.sleep(0.25)

            recognizer.stop_continuous_recognition()

        except Exception as exc:

            try:
                recognizer.stop_continuous_recognition()
            except Exception:
                pass

            return cls._create_error_result(
                filename,
                f"Azure Speech transcription failed: {exc}",
            )

        # ---------------------------------------------------------
        # 7. Handle Azure errors
        # ---------------------------------------------------------

        if error_message and not segments:
            return cls._create_error_result(
                filename,
                error_message[0],
            )

        if not segments:
            return cls._create_error_result(
                filename,
                "No speech could be recognized in this audio file.",
            )

        # ---------------------------------------------------------
        # 8. Sort transcript segments
        # ---------------------------------------------------------

        segments.sort(
            key=lambda item: item["start"]
        )

        # ---------------------------------------------------------
        # 9. Convert transcript into application chunks
        # ---------------------------------------------------------

        chunks: List[Dict[str, Any]] = []
        full_text_lines: List[str] = []

        for idx, segment in enumerate(segments):

            start_time = float(segment["start"])
            end_time = float(segment["end"])

            text = ContentCleaner.clean_text(
                segment["text"]
            )

            if not text:
                continue

            formatted_time = (
                f"{format_timestamp(start_time)} - "
                f"{format_timestamp(end_time)}"
            )

            full_text_lines.append(
                f"[{formatted_time}] {text}"
            )

            chunks.append(
                {
                    "chunk_index": idx,
                    "content": text,
                    "media_type": "audio",
                    "content_type": "audio",
                    "page_number": None,
                    "timestamp_start": start_time,
                    "timestamp_end": end_time,
                    "topic_section": f"Audio Segment {idx + 1}",
                    "metadata": {
                        "timestamp": format_timestamp(start_time),
                        "timestamp_start": start_time,
                        "timestamp_end": end_time,
                        "section": f"Audio Segment {idx + 1}",
                        "duration": round(
                            end_time - start_time,
                            2,
                        ),
                        "timestamp_formatted": formatted_time,
                    },
                }
            )

        # ---------------------------------------------------------
        # 10. Calculate duration from actual transcript
        # ---------------------------------------------------------

        duration_seconds = 0.0

        if chunks:
            duration_seconds = max(
                chunk["timestamp_end"]
                for chunk in chunks
            )

        # ---------------------------------------------------------
        # 11. Return standardized result
        # ---------------------------------------------------------

        return {
            "source": filename,
            "content_type": "audio",
            "success": True,
            "page_count": None,
            "duration_seconds": round(
                duration_seconds,
                2,
            ),
            "full_text": "\n".join(full_text_lines),
            "chunks": chunks,
            "error_message": (
                error_message[0]
                if error_message
                else None
            ),
        }

    @classmethod
    def process_normalized(
        cls,
        file_path: str,
    ) -> MultimodalProcessingResult:
        """
        Convert the transcription result into the standardized
        MultimodalProcessingResult used by the application.
        """

        raw = cls.process(file_path)

        items: List[NormalizedContentItem] = []

        for chunk in raw.get("chunks", []):

            metadata = chunk.get(
                "metadata",
                {},
            )

            items.append(
                NormalizedContentItem(
                    source=raw.get(
                        "source",
                        Path(file_path).name,
                    ),
                    content_type="audio",
                    text=chunk["content"],
                    metadata={
                        "timestamp": metadata.get(
                            "timestamp"
                        ),
                        "timestamp_start": metadata.get(
                            "timestamp_start"
                        ),
                        "timestamp_end": metadata.get(
                            "timestamp_end"
                        ),
                        "section": metadata.get(
                            "section"
                        ),
                        "duration": metadata.get(
                            "duration"
                        ),
                    },
                )
            )

        return MultimodalProcessingResult(
            source=Path(file_path).name,
            content_type="audio",
            success=raw.get(
                "success",
                False,
            ),
            page_count=None,
            duration_seconds=raw.get(
                "duration_seconds"
            ),
            full_text=raw.get(
                "full_text",
                "",
            ),
            items=items,
            error_message=raw.get(
                "error_message"
            ),
        )

    @classmethod
    def _create_error_result(
        cls,
        filename: str,
        error_msg: str,
    ) -> Dict[str, Any]:
        """
        Return a clean processing failure instead of inventing
        transcript content.
        """

        return {
            "source": filename,
            "content_type": "audio",
            "success": False,
            "page_count": None,
            "duration_seconds": 0.0,
            "full_text": "",
            "error_message": error_msg,
            "chunks": [],
        }