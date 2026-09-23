"""
Video processing module for recorded educational lectures, tutorials, and screen casts.

Pipeline:
    Video file
        ↓
    FFmpeg
        ↓
    16 kHz mono WAV audio
        ↓
    Azure Speech via AudioProcessor
        ↓
    Real timestamped transcript
        ↓
    Video transcript chunks
        ↓
    RAG / Azure AI Search
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional

from backend.processing.base import (
    NormalizedContentItem,
    MultimodalProcessingResult,
    ContentValidationError
)
from backend.rag.cleaner import ContentCleaner
from backend.utils.helpers import format_timestamp
from backend.processing.audio_processor import AudioProcessor


class VideoProcessor:
    """
    Specialized processor for educational video files.

    Supported formats:
        .mp4
        .mov
        .avi
        .mkv
        .webm
    """

    SUPPORTED_EXTENSIONS = {
        ".mp4",
        ".mov",
        ".avi",
        ".mkv",
        ".webm"
    }

    MAX_FILE_SIZE_BYTES = 500 * 1024 * 1024  # 500 MB

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------

    @classmethod
    def validate_file(cls, file_path: str) -> bool:
        """
        Validate video file existence, size and extension.
        """

        if not os.path.exists(file_path):
            raise ContentValidationError(
                f"Video file not found: {file_path}"
            )

        file_size = os.path.getsize(file_path)

        if file_size == 0:
            raise ContentValidationError(
                f"Video file '{Path(file_path).name}' is empty."
            )

        if file_size > cls.MAX_FILE_SIZE_BYTES:
            raise ContentValidationError(
                f"Video file exceeds maximum size of 500MB "
                f"({file_size / (1024 * 1024):.1f}MB)."
            )

        extension = Path(file_path).suffix.lower()

        if extension not in cls.SUPPORTED_EXTENSIONS:
            raise ContentValidationError(
                f"Unsupported video format '{extension}'. "
                f"Supported formats: "
                f"{', '.join(sorted(cls.SUPPORTED_EXTENSIONS))}"
            )

        return True

    # ---------------------------------------------------------
    # MAIN PROCESSOR
    # ---------------------------------------------------------

    @classmethod
    def process(cls, file_path: str) -> Dict[str, Any]:
        """
        Process a video and generate a REAL timestamped transcript.

        Video
            ↓
        FFmpeg audio extraction
            ↓
        WAV
            ↓
        Azure Speech
            ↓
        Timestamped transcript
        """

        filename = Path(file_path).name

        # -----------------------------------------------------
        # 1. Validate
        # -----------------------------------------------------

        try:
            cls.validate_file(file_path)

        except ContentValidationError as error:
            return cls._create_error_result(
                filename,
                str(error)
            )

        except Exception as error:
            return cls._create_error_result(
                filename,
                f"Video validation failed: {str(error)}"
            )

        # -----------------------------------------------------
        # 2. Check FFmpeg
        # -----------------------------------------------------

        ffmpeg_path = shutil.which("ffmpeg")
        ffprobe_path = shutil.which("ffprobe")

        if not ffmpeg_path:
            return cls._create_error_result(
                filename,
                (
                    "FFmpeg was not found on the system. "
                    "Please install FFmpeg and add C:\\ffmpeg\\bin "
                    "to the Windows PATH."
                )
            )

        if not ffprobe_path:
            return cls._create_error_result(
                filename,
                (
                    "FFprobe was not found on the system. "
                    "Please make sure C:\\ffmpeg\\bin is added "
                    "to the Windows PATH."
                )
            )

        # -----------------------------------------------------
        # 3. Get REAL video duration
        # -----------------------------------------------------

        duration = cls._get_video_duration(
            file_path,
            ffprobe_path
        )

        # -----------------------------------------------------
        # 4. Extract audio from video
        # -----------------------------------------------------

        temporary_wav = None

        try:

            temporary_wav = cls._extract_audio(
                file_path,
                ffmpeg_path
            )

            # -------------------------------------------------
            # 5. Send extracted WAV to Azure Speech
            #
            # This reuses the SAME AudioProcessor that already
            # works successfully for your Heart Lecture.wav.
            # -------------------------------------------------

            speech_result = AudioProcessor.process(
                temporary_wav
            )

            if not speech_result:
                return cls._create_error_result(
                    filename,
                    "Azure Speech returned no processing result."
                )

            if not speech_result.get("success", False):
                return cls._create_error_result(
                    filename,
                    speech_result.get(
                        "error_message",
                        "Azure Speech failed to process the video audio."
                    )
                )

            audio_chunks = speech_result.get(
                "chunks",
                []
            )

            # -------------------------------------------------
            # 6. Convert AUDIO chunks to VIDEO chunks
            # -------------------------------------------------

            video_chunks: List[Dict[str, Any]] = []
            full_text_lines: List[str] = []

            for idx, chunk in enumerate(audio_chunks):

                text = ContentCleaner.clean_text(
                    chunk.get("content", "")
                )

                if not text:
                    continue

                start_time = float(
                    chunk.get(
                        "timestamp_start",
                        0.0
                    ) or 0.0
                )

                end_time = float(
                    chunk.get(
                        "timestamp_end",
                        start_time
                    ) or start_time
                )

                formatted_time = (
                    f"{format_timestamp(start_time)} - "
                    f"{format_timestamp(end_time)}"
                )

                section_name = (
                    f"Video Transcript Segment {len(video_chunks) + 1}"
                )

                # ---------------------------------------------
                # Full transcript
                # ---------------------------------------------

                full_text_lines.append(
                    f"[{formatted_time}] "
                    f"({section_name}): {text}"
                )

                # ---------------------------------------------
                # Video chunk
                # ---------------------------------------------

                video_chunks.append({
                    "chunk_index": len(video_chunks),

                    "content": text,

                    "media_type": "video",

                    "content_type": "video",

                    "page_number": None,

                    "timestamp_start": start_time,

                    "timestamp_end": end_time,

                    "topic_section": section_name,

                    "metadata": {
                        "timestamp": format_timestamp(
                            start_time
                        ),

                        "timestamp_start": start_time,

                        "timestamp_end": end_time,

                        "section": section_name,

                        "duration": round(
                            max(
                                0.0,
                                end_time - start_time
                            ),
                            2
                        ),

                        "timestamp_formatted": formatted_time,

                        "source": filename,

                        "transcription_source": (
                            "Azure Speech"
                        )
                    }
                })

            # -------------------------------------------------
            # 7. Handle no speech
            # -------------------------------------------------

            if not video_chunks:

                return cls._create_error_result(
                    filename,
                    (
                        "The video was processed successfully, "
                        "but no speech was recognized."
                    )
                )

            # -------------------------------------------------
            # 8. Use actual duration
            # -------------------------------------------------

            if duration is None or duration <= 0:

                duration = max(
                    chunk["timestamp_end"]
                    for chunk in video_chunks
                )

            # -------------------------------------------------
            # 9. Return final result
            # -------------------------------------------------

            return {
                "source": filename,

                "content_type": "video",

                "success": True,

                "page_count": None,

                "duration_seconds": round(
                    duration,
                    2
                ),

                "full_text": "\n".join(
                    full_text_lines
                ),

                "chunks": video_chunks
            }

        except Exception as error:

            print(
                f"[VideoProcessor] Error processing "
                f"{filename}: {error}"
            )

            return cls._create_error_result(
                filename,
                f"Video processing failed: {str(error)}"
            )

        finally:

            # -------------------------------------------------
            # 10. Delete temporary WAV
            # -------------------------------------------------

            if temporary_wav:

                try:

                    if os.path.exists(
                        temporary_wav
                    ):
                        os.remove(
                            temporary_wav
                        )

                except Exception as cleanup_error:

                    print(
                        "[VideoProcessor] "
                        f"Temporary WAV cleanup failed: "
                        f"{cleanup_error}"
                    )

    # ---------------------------------------------------------
    # FFMPEG AUDIO EXTRACTION
    # ---------------------------------------------------------

    @classmethod
    def _extract_audio(
        cls,
        video_path: str,
        ffmpeg_path: str
    ) -> str:
        """
        Extract audio from video using FFmpeg.

        Output:
            PCM signed 16-bit
            16 kHz
            Mono
            WAV

        This format is ideal for Azure Speech.
        """

        temporary_file = tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        )

        wav_path = temporary_file.name

        temporary_file.close()

        command = [
            ffmpeg_path,

            "-y",

            "-i",
            video_path,

            # Ignore video stream
            "-vn",

            # Mono
            "-ac",
            "1",

            # 16 kHz
            "-ar",
            "16000",

            # PCM 16-bit
            "-c:a",
            "pcm_s16le",

            wav_path
        ]

        print(
            "[VideoProcessor] Extracting audio using FFmpeg..."
        )

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:

            try:
                if os.path.exists(wav_path):
                    os.remove(wav_path)
            except Exception:
                pass

            error_output = (
                result.stderr.strip()
                or "Unknown FFmpeg error."
            )

            raise RuntimeError(
                f"FFmpeg audio extraction failed: "
                f"{error_output[-1500:]}"
            )

        if not os.path.exists(wav_path):

            raise RuntimeError(
                "FFmpeg completed but did not create "
                "the extracted WAV file."
            )

        if os.path.getsize(wav_path) == 0:

            raise RuntimeError(
                "FFmpeg created an empty WAV file. "
                "The video may not contain an audio track."
            )

        print(
            "[VideoProcessor] Audio extraction successful."
        )

        return wav_path

    # ---------------------------------------------------------
    # VIDEO DURATION
    # ---------------------------------------------------------

    @classmethod
    def _get_video_duration(
        cls,
        file_path: str,
        ffprobe_path: str
    ) -> Optional[float]:
        """
        Get the REAL video duration using FFprobe.
        """

        command = [
            ffprobe_path,

            "-v",
            "error",

            "-show_entries",
            "format=duration",

            "-of",
            "default=noprint_wrappers=1:nokey=1",

            file_path
        ]

        try:

            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if result.returncode != 0:
                return None

            duration_text = result.stdout.strip()

            if not duration_text:
                return None

            duration = float(
                duration_text
            )

            if duration <= 0:
                return None

            return duration

        except Exception as error:

            print(
                "[VideoProcessor] "
                f"Could not determine video duration: "
                f"{error}"
            )

            return None

    # ---------------------------------------------------------
    # NORMALIZED PROCESSING
    # ---------------------------------------------------------

    @classmethod
    def process_normalized(
        cls,
        file_path: str
    ) -> MultimodalProcessingResult:
        """
        Process video and return strongly typed
        MultimodalProcessingResult.
        """

        raw = cls.process(
            file_path
        )

        items = []

        for chunk in raw.get(
            "chunks",
            []
        ):

            metadata = chunk.get(
                "metadata",
                {}
            )

            items.append(
                NormalizedContentItem(

                    source=raw.get(
                        "source",
                        Path(file_path).name
                    ),

                    content_type="video",

                    text=chunk.get(
                        "content",
                        ""
                    ),

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
                        )
                    }
                )
            )

        return MultimodalProcessingResult(

            source=Path(file_path).name,

            content_type="video",

            success=raw.get(
                "success",
                True
            ),

            page_count=None,

            duration_seconds=raw.get(
                "duration_seconds"
            ),

            full_text=raw.get(
                "full_text",
                ""
            ),

            items=items,

            error_message=raw.get(
                "error_message"
            )
        )

    # ---------------------------------------------------------
    # ERROR RESULT
    # ---------------------------------------------------------

    @classmethod
    def _create_error_result(
        cls,
        filename: str,
        error_msg: str
    ) -> Dict[str, Any]:
        """
        Create standardized video processing error.
        """

        return {

            "source": filename,

            "content_type": "video",

            "success": False,

            "page_count": None,

            "duration_seconds": 0.0,

            "full_text": "",

            "error_message": error_msg,

            "chunks": [{
                "chunk_index": 0,

                "content": (
                    f"[Error Processing Video "
                    f"{filename}]: {error_msg}"
                ),

                "media_type": "video",

                "content_type": "video",

                "page_number": None,

                "timestamp_start": 0.0,

                "timestamp_end": 0.0,

                "topic_section": "Processing Error",

                "metadata": {
                    "error": error_msg
                }
            }]
        }