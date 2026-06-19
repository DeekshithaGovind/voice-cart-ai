from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Product
from app.schemas import NLUResult, ParsedLineItem
from app.services.nlu.tier1_matcher import Tier1Matcher
from app.services.nlu.tier2_ner import Tier2NERMatcher
from app.services.nlu.tier3_llm import Tier3LLMFallback


class NLUCascade:
    def __init__(self) -> None:
        self.tier1 = Tier1Matcher()
        self.tier2 = Tier2NERMatcher()
        self.tier3 = Tier3LLMFallback()
        self._loaded = False

    async def load_catalog(self, db: AsyncSession) -> None:
        result = await db.execute(select(Product).where(Product.active.is_(True)))
        products = list(result.scalars().all())
        self.tier1.load_products(products)
        self.tier2.load_products(products)
        self._products = products
        self._loaded = True

    async def parse(self, db: AsyncSession, transcript: str, language: str = "en") -> NLUResult:
        if not self._loaded:
            await self.load_catalog(db)

        tier1_items = self.tier1.parse(transcript, language)
        tier_used = 1

        if any(not i.product_id for i in tier1_items):
            tier2_items = self.tier2.parse_unmatched(tier1_items, language)
            if any(i.product_id and i.nlu_tier == 2 for i in tier2_items):
                tier_used = 2
            tier1_items = tier2_items

        if any(not i.product_id for i in tier1_items):
            tier3_items = await self.tier3.parse_unmatched(tier1_items, self._products, language)
            if any(i.product_id and i.nlu_tier == 3 for i in tier3_items):
                tier_used = 3
            tier1_items = tier3_items

        unmatched = [i.raw_text for i in tier1_items if not i.product_id]
        matched = [i for i in tier1_items if i.product_id]

        return NLUResult(
            items=matched if matched else tier1_items,
            tier_used=tier_used,
            language=language,
            raw_transcript=transcript,
            unmatched=unmatched,
        )
