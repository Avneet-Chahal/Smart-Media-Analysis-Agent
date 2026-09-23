import re
from typing import List

class SemanticChunker:
    """Splits educational text into overlapping, coherent paragraphs or sentence chunks."""

    @staticmethod
    def chunk_text(text: str, max_chars: int = 800, overlap: int = 100) -> List[str]:
        if not text or not text.strip():
            return []

        if len(text) <= max_chars:
            return [text.strip()]

        paragraphs = text.split("\n\n")
        chunks: List[str] = []
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if len(current_chunk) + len(para) + 2 <= max_chars:
                current_chunk = f"{current_chunk}\n\n{para}".strip()
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                if len(para) > max_chars:
                    # Break long paragraphs at sentence boundaries
                    sentences = re.split(r'(?<=[.?!])\s+', para)
                    sub_chunk = ""
                    for sent in sentences:
                        if len(sub_chunk) + len(sent) + 1 <= max_chars:
                            sub_chunk = f"{sub_chunk} {sent}".strip()
                        else:
                            if sub_chunk:
                                chunks.append(sub_chunk)
                            sub_chunk = sent
                    if sub_chunk:
                        current_chunk = sub_chunk
                else:
                    current_chunk = para

        if current_chunk:
            chunks.append(current_chunk)

        return chunks
