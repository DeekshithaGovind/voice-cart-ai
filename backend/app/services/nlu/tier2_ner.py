import re
from typing import Any

from app.models import Product
from app.schemas import ParsedLineItem
from app.services.nlu.tier1_matcher import extract_quantity


ENTITY_PATTERNS = {
    "quantity": re.compile(r"\d+(?:\.\d+)?|\b(one|two|three|four|five|dozen|half)\b", re.I),
    "product_hint": re.compile(r"\b(rice|atta|dal|oil|sugar|salt|milk|bread|tea|coffee|soap|shampoo|detergent|onion|potato|tomato|chana|moong|besan|ghee|paneer|curd|biscuit|noodles)\b", re.I),
}

HI_TA_PRODUCT_HINTS = {
    "chawal": "rice", "chaval": "rice", "arisi": "rice",
    "atta": "atta", "maida": "atta",
    "tel": "oil", "teliy": "oil", "ennai": "oil",
    "cheeni": "sugar", "sakkarai": "sugar",
    "namak": "salt", "uppu": "salt",
    "doodh": "milk", "paal": "milk",
    "pyaz": "onion", "vengayam": "onion",
    "aloo": "potato", "urulai": "potato",
}


class Tier2NERMatcher:
    def __init__(self) -> None:
        self.synonym_map: dict[str, Product] = {}

    def load_products(self, products: list[Product]) -> None:
        self.synonym_map.clear()
        for p in products:
            keys = {p.name.lower(), p.sku.lower()}
            if p.name_hi:
                keys.add(p.name_hi.lower())
            if p.name_ta:
                keys.add(p.name_ta.lower())
            for alias in (p.aliases or []):
                keys.add(alias.lower())
            for syn in (p.synonyms or []):
                keys.add(syn.lower())
            for key in keys:
                self.synonym_map[key] = p

    def _normalize_mixed(self, text: str) -> str:
        lower = text.lower()
        for hint, canonical in HI_TA_PRODUCT_HINTS.items():
            lower = re.sub(rf"\b{re.escape(hint)}\b", canonical, lower)
        return lower

    def _find_product_by_entities(self, text: str) -> Product | None:
        normalized = self._normalize_mixed(text)
        tokens = re.findall(r"[a-zA-Z\u0900-\u097F\u0B80-\u0BFF]+", normalized)
        for i in range(len(tokens), 0, -1):
            for start in range(len(tokens) - i + 1):
                phrase = " ".join(tokens[start : start + i]).lower()
                if phrase in self.synonym_map:
                    return self.synonym_map[phrase]
        for token in tokens:
            if token.lower() in self.synonym_map:
                return self.synonym_map[token.lower()]
        hint = ENTITY_PATTERNS["product_hint"].search(normalized)
        if hint:
            word = hint.group(1).lower()
            for key, product in self.synonym_map.items():
                if word in key or key in word:
                    return product
        return None

    def parse_unmatched(self, items: list[ParsedLineItem], language: str = "en") -> list[ParsedLineItem]:
        resolved: list[ParsedLineItem] = []
        for item in items:
            if item.product_id:
                resolved.append(item)
                continue

            product = self._find_product_by_entities(item.raw_text)
            if product:
                qty, unit, _ = extract_quantity(item.raw_text)
                resolved.append(
                    ParsedLineItem(
                        raw_text=item.raw_text,
                        product_id=product.id,
                        product_name=product.name,
                        quantity=qty,
                        unit=unit or product.unit,
                        confidence=0.75,
                        nlu_tier=2,
                    )
                )
            else:
                resolved.append(item)
        return resolved
