import asyncio
import io
import tempfile
from pathlib import Path

from app.config import settings

_model = None
_model_lock = asyncio.Lock()


def _get_model():
    global _model
    if _model is None:
        from faster_whisper import WhisperModel

        _model = WhisperModel(settings.whisper_model, device="cpu", compute_type="int8")
    return _model


async def transcribe_audio_bytes(audio_bytes: bytes, language: str | None = None) -> dict:
    """Transcribe audio using faster-whisper in CPU mode."""
    try:
        from faster_whisper import WhisperModel  # noqa: F401
    except ImportError:
        return {"text": "", "language": language or "en", "error": "faster-whisper not installed"}

    suffix = ".webm"
    if audio_bytes[:4] == b"RIFF":
        suffix = ".wav"
    elif audio_bytes[:3] == b"ID3" or audio_bytes[:2] == b"\xff\xfb":
        suffix = ".mp3"

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(audio_bytes)
        path = Path(tmp.name)

    try:
        def _run():
            model = _get_model()
            segments, info = model.transcribe(
                str(path),
                language=None if language in (None, "mixed", "auto") else language,
                beam_size=1,
                vad_filter=True,
            )
            text = " ".join(seg.text.strip() for seg in segments).strip()
            return text, info

        text, info = await asyncio.to_thread(_run)
        detected = info.language or language or "en"
        return {"text": text, "language": detected, "confidence": info.language_probability}
    except Exception as exc:
        return {"text": "", "language": language or "en", "error": str(exc)}
    finally:
        path.unlink(missing_ok=True)
