import re
from typing import AsyncGenerator


LANG_HINTS = {
    "hi": re.compile(r"[\u0900-\u097F]"),
    "ta": re.compile(r"[\u0B80-\u0BFF]"),
}


def detect_language(text: str, fallback: str = "en") -> str:
    if LANG_HINTS["hi"].search(text):
        return "hi" if not LANG_HINTS["ta"].search(text) else "mixed"
    if LANG_HINTS["ta"].search(text):
        return "ta"
    return fallback


class StreamingSTT:
    """CPU-friendly STT adapter. Production: plug faster-whisper or Vosk."""

    async def transcribe_stream(self, audio_chunks: AsyncGenerator[bytes, None], language: str = "en"):
        buffer = b""
        async for chunk in audio_chunks:
            buffer += chunk
            yield {"text": "", "is_final": False, "language": language}

        yield {"text": "", "is_final": True, "language": language}

    def normalize_transcript(self, text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()
