from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Product
from app.schemas import NLUResult, ValidationResult


async def build_validation_details(
    db: AsyncSession,
    nlu_result: NLUResult,
    validation: ValidationResult,
    confirmation_status: str = "pending",
) -> dict[str, Any]:
    product_matches = []
    quantity_validation = []
    stock_validation = []

    issue_codes = {(i.product_id, i.field): i for i in validation.issues}

    for item in nlu_result.items:
        matched = item.product_id is not None
        product_matches.append(
            {
                "raw_text": item.raw_text,
                "product_name": item.product_name,
                "matched": matched,
                "confidence": item.confidence,
                "nlu_tier": item.nlu_tier,
                "quantity": item.quantity,
            }
        )

        if not item.product_id:
            quantity_validation.append(
                {"product_name": item.raw_text, "requested": item.quantity, "min_qty": None, "passed": False}
            )
            stock_validation.append(
                {"product_name": item.raw_text, "requested": item.quantity, "stock": None, "passed": False}
            )
            continue

        product = (
            await db.execute(select(Product).where(Product.id == item.product_id))
        ).scalar_one_or_none()
        if not product:
            continue

        qty_issue = issue_codes.get((product.id, "quantity"))
        stock_issue = issue_codes.get((product.id, "stock"))

        quantity_validation.append(
            {
                "product_name": product.name,
                "requested": item.quantity,
                "min_qty": product.min_qty,
                "passed": qty_issue is None,
                "message": qty_issue.message if qty_issue else None,
            }
        )
        stock_validation.append(
            {
                "product_name": product.name,
                "requested": item.quantity,
                "stock": product.stock,
                "passed": stock_issue is None,
                "message": stock_issue.message if stock_issue else None,
            }
        )

    return {
        "product_matches": product_matches,
        "quantity_validation": quantity_validation,
        "stock_validation": stock_validation,
        "confirmation_status": confirmation_status,
        "valid": validation.valid,
        "issues": [i.model_dump() for i in validation.issues],
    }
