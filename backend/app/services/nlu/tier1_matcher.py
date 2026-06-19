import re
from dataclasses import dataclass, field

from rapidfuzz import fuzz, process

from app.models import Product
from app.schemas import ParsedLineItem


QUANTITY_PATTERNS = [
    (re.compile(r"(\d+(?:\.\d+)?)\s*(kg|kilo|kilogram|g|gram|grams|ltr|liter|litre|packet|pack|pcs|piece|pieces|dozen|box|bottle|tin|bag|sack|crate)", re.I), 1),
    (re.compile(r"(\d+(?:\.\d+)?)\s*(किलो|ग्राम|लीटर|पैक|डिब्बा|बोतल)", re.I), 1),
    (re.compile(r"(\d+(?:\.\d+)?)\s*(கிலோ|கிராம்|லிட்டர்|பாக்கெட்|பெட்டி|பாட்டில்)", re.I), 1),
    (re.compile(r"(\d+(?:\.\d+)?)\s*$"), 1),
    (re.compile(r"^(one|two|three|four|five|six|seven|eight|nine|ten|half|dozen)\b", re.I), 0),
]

WORD_TO_NUM = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "half": 0.5, "dozen": 12,
    "एक": 1, "दो": 2, "तीन": 3, "चार": 4, "पांच": 5,
    "ஒன்று": 1, "இரண்டு": 2, "மூன்று": 3, "நான்கு": 4, "ஐந்து": 5,
}


@dataclass
class ProductTrie:
    entries: list[tuple[str, Product, str]] = field(default_factory=list)

    def build(self, products: list[Product]) -> None:
        self.entries.clear()
        for p in products:
            names = [p.name.lower()]
            if p.name_hi:
                names.append(p.name_hi.lower())
            if p.name_ta:
                names.append(p.name_ta.lower())
            for alias in (p.aliases or []):
                names.append(alias.lower())
            for syn in (p.synonyms or []):
                names.append(syn.lower())
            for name in names:
                self.entries.append((name, p, name))

    def keyword_match(self, text: str, threshold: int = 82) -> list[tuple[Product, str, float]]:
        text_lower = text.lower().strip()
        if not text_lower:
            return []
        choices = [e[0] for e in self.entries]
        matches = process.extract(text_lower, choices, scorer=fuzz.token_set_ratio, limit=5)
        results = []
        seen = set()
        for match_text, score, idx in matches:
            if score < threshold:
                continue
            _, product, alias = self.entries[idx]
            if product.id in seen:
                continue
            seen.add(product.id)
            results.append((product, alias, score / 100.0))
        return results


def extract_quantity(text: str) -> tuple[float, str, str]:
    text = text.strip()
    for pattern, group_idx in QUANTITY_PATTERNS:
        m = pattern.search(text)
        if m:
            if group_idx == 0:
                word = m.group(1).lower()
                qty = WORD_TO_NUM.get(word, 1.0)
                remainder = text[m.end():].strip()
                return qty, "", remainder
            qty = float(m.group(1))
            unit = m.group(2) if m.lastindex and m.lastindex >= 2 else ""
            remainder = (text[: m.start()] + " " + text[m.end() :]).strip()
            return qty, unit, remainder

    return 1.0, "", text


def split_order_segments(transcript: str) -> list[str]:
    parts = re.split(r"[,;]|(?:\band\b)|(?:\baur\b)|(?:\bமற்றும்\b)", transcript, flags=re.I)
    return [p.strip() for p in parts if p.strip()]


class Tier1Matcher:
    def __init__(self) -> None:
        self.trie = ProductTrie()

    def load_products(self, products: list[Product]) -> None:
        self.trie.build(products)

    def parse(self, transcript: str, language: str = "en") -> list[ParsedLineItem]:
        items: list[ParsedLineItem] = []
        unmatched: list[str] = []

        for segment in split_order_segments(transcript):
            qty, unit, product_text = extract_quantity(segment)
            if not product_text:
                continue

            matches = self.trie.keyword_match(product_text, threshold=78)
            if matches:
                product, alias, confidence = matches[0]
                items.append(
                    ParsedLineItem(
                        raw_text=segment,
                        product_id=product.id,
                        product_name=product.name,
                        quantity=qty,
                        unit=unit or product.unit,
                        confidence=confidence,
                        nlu_tier=1,
                        matched_alias=alias,
                    )
                )
            else:
                unmatched.append(segment)
                items.append(
                    ParsedLineItem(
                        raw_text=segment,
                        quantity=qty,
                        unit=unit,
                        confidence=0.0,
                        nlu_tier=1,
                    )
                )

        return items
