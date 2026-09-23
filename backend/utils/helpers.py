import os
from pathlib import Path
from typing import Optional

def format_timestamp(seconds: Optional[float]) -> str:
    """Formats float seconds into MM:SS or HH:MM:SS string."""
    if seconds is None:
        return "00:00"
    total_secs = int(seconds)
    hrs = total_secs // 3600
    mins = (total_secs % 3600) // 60
    secs = total_secs % 60
    if hrs > 0:
        return f"{hrs:02d}:{mins:02d}:{secs:02d}"
    return f"{mins:02d}:{secs:02d}"

def detect_media_type(filename: str) -> str:
    """Categorizes file into 'pdf', 'audio', 'video', 'document', or 'unknown'."""
    ext = Path(filename).suffix.lower()
    if ext in [".pdf"]:
        return "pdf"
    elif ext in [".docx", ".doc", ".txt", ".md", ".rtf"]:
        return "document"
    elif ext in [".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"]:
        return "audio"
    elif ext in [".mp4", ".mov", ".mkv", ".webm", ".avi"]:
        return "video"
    return "unknown"

def get_file_size(file_path: str) -> int:
    """Returns file size in bytes safely."""
    try:
        return os.path.getsize(file_path)
    except Exception:
        return 0
