import json
from typing import Any

import httpx

from app.config import settings
from app.models import Product
from app.schemas import ParsedLineItem
from app.services.nlu.tier1_matcher import extract_quantity


class Tier3LLMFallback:
    def __init__(self) -> None:
        self.enabled = settings.enable_tier3_llm

    async def parse_unmatched(
        self,
        items: list[ParsedLineItem],
        products: list[Product],
        language: str = "en",
    ) -> list[ParsedLineItem]:
        if not self.enabled:
            return items

        unresolved = [i for i in items if not i.product_id]
        if not unresolved:
            return items

        catalog = [
            {"id": p.id, "name": p.name, "aliases": p.aliases or [], "unit": p.unit}
            for p in products[:50]
        ]
        prompt = (
            "Extract grocery order items as JSON array with fields: product_id, quantity, product_name. "
            f"Catalog: {json.dumps(catalog)}. "
            f"Language: {language}. "
            f"Phrases: {[i.raw_text for i in unresolved]}. "
            "Return ONLY valid JSON array."
        )

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    f"{settings.ollama_base_url}/api/generate",
                    json={"model": settings.ollama_model, "prompt": prompt, "stream": False},
                )
                if resp.status_code != 200:
                    return items
                text = resp.json().get("response", "")
                start = text.find("[")
                end = text.rfind("]") + 1
                if start < 0 or end <= start:
                    return items
                parsed = json.loads(text[start:end])
        except Exception:
            return items

        product_map = {p.id: p for p in products}
        resolved_map: dict[str, ParsedLineItem] = {i.raw_text: i for i in items}

        for entry, raw_item in zip(parsed, unresolved):
            pid = entry.get("product_id")
            product = product_map.get(pid)
            if not product:
                continue
            qty = float(entry.get("quantity", 1))
            resolved_map[raw_item.raw_text] = ParsedLineItem(
                raw_text=raw_item.raw_text,
                product_id=product.id,
                product_name=product.name,
                quantity=qty,
                unit=product.unit,
                confidence=0.6,
                nlu_tier=3,
            )

        return list(resolved_map.values())
