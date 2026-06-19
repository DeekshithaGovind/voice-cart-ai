import asyncio
import tempfile
from pathlib import Path

import edge_tts

VOICES = {
    "en": "en-IN-NeerjaNeural",
    "hi": "hi-IN-SwaraNeural",
    "ta": "ta-IN-PallaviNeural",
    "mixed": "en-IN-NeerjaNeural",
}


def build_confirmation_script(language: str, customer_name: str, items: list[dict], total: float) -> str:
    if language == "hi":
        lines = [f"नमस्ते {customer_name}।", "आपका ऑर्डर कन्फर्म है।"]
        for item in items:
            lines.append(f"{item['quantity']} {item['unit']} {item['name']}")
        lines.append(f"कुल राशि {total:.0f} रुपये। धन्यवाद।")
        return " ".join(lines)
    if language == "ta":
        lines = [f"வணக்கம் {customer_name}.", "உங்கள் ஆர்டர் உறுதி செய்யப்பட்டது."]
        for item in items:
            lines.append(f"{item['quantity']} {item['unit']} {item['name']}")
        lines.append(f"மொத்த தொகை {total:.0f} ரூபாய். நன்றி.")
        return " ".join(lines)

    lines = [f"Hello {customer_name}.", "Your order is confirmed."]
    for item in items:
        lines.append(f"{item['quantity']} {item['unit']} of {item['name']}")
    lines.append(f"Total amount {total:.0f} rupees. Thank you.")
    return " ".join(lines)


async def synthesize_confirmation(language: str, text: str) -> bytes | None:
    voice = VOICES.get(language, VOICES["en"])
    try:
        communicate = edge_tts.Communicate(text, voice)
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            path = Path(tmp.name)
        await communicate.save(str(path))
        data = path.read_bytes()
        path.unlink(missing_ok=True)
        return data
    except Exception:
        return None
