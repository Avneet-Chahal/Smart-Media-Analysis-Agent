"""
Text cleaning and normalization module for educational content.
Strips noisy OCR artifacts while preserving mathematical symbols and formula structures.
"""

import re

class ContentCleaner:
    """Cleans and normalizes text extracted from PDFs, transcripts, and documents."""

    @staticmethod
    def clean_text(raw_text: str) -> str:
        if not raw_text:
            return ""

        text = raw_text

        # 1. Fix broken hyphenated words at line breaks (e.g., "opti-\nmization" -> "optimization")
        text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)

        # 2. Normalize multiple newlines and carriage returns
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        # 3. Strip non-printable ASCII control characters (keep tabs, newlines, and standard unicode)
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)

        # 4. Collapse consecutive spaces and tabs while keeping paragraph structure
        text = re.sub(r'[ \t]+', ' ', text)

        # 5. Collapse 3+ consecutive newlines into double newlines (paragraphs)
        text = re.sub(r'\n{3,}', '\n\n', text)

        # 6. Strip leading and trailing whitespace
        return text.strip()
