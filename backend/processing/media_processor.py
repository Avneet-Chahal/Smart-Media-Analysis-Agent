import os
from pathlib import Path
from typing import List, Dict, Any
from backend.processing.audio_processor import AudioProcessor
from backend.processing.video_processor import VideoProcessor


class MediaProcessor:
    """Specialized audio & video lecture processor routing to specialized processors."""

    @classmethod
    def process(cls, file_path: str, media_type: str = "video") -> Dict[str, Any]:
        if media_type == "audio" or Path(file_path).suffix.lower() in AudioProcessor.SUPPORTED_EXTENSIONS:
            return AudioProcessor.process(file_path)
        else:
            return VideoProcessor.process(file_path)

