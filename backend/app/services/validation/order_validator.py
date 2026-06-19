from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Customer, Product
from app.schemas import NLUResult, ParsedLineItem, ValidationIssue, ValidationResult


async def validate_order(
    db: AsyncSession,
    customer_id: str,
    nlu_result: NLUResult,
) -> ValidationResult:
    issues: list[ValidationIssue] = []
    total = 0.0

    customer = (
        await db.execute(select(Customer).where(Customer.id == customer_id))
    ).scalar_one_or_none()
    if not customer:
        return ValidationResult(valid=False, issues=[ValidationIssue(code="CUSTOMER_NOT_FOUND", message="Customer not found")])

    for item in nlu_result.items:
        if not item.product_id:
            issues.append(
                ValidationIssue(
                    code="UNMATCHED_PRODUCT",
                    message=f"Could not match: {item.raw_text}",
                    field="product",
                )
            )
            continue

        product = (
            await db.execute(select(Product).where(Product.id == item.product_id))
        ).scalar_one_or_none()
        if not product:
            issues.append(
                ValidationIssue(code="PRODUCT_NOT_FOUND", message=f"Product missing: {item.product_name}", product_id=item.product_id)
            )
            continue

        if item.quantity < product.min_qty:
            issues.append(
                ValidationIssue(
                    code="MIN_QTY",
                    message=f"{product.name} minimum order is {product.min_qty} {product.unit}",
                    product_id=product.id,
                    field="quantity",
                )
            )

        if item.quantity > product.stock:
            issues.append(
                ValidationIssue(
                    code="OUT_OF_STOCK",
                    message=f"{product.name} only {product.stock} {product.unit} in stock",
                    product_id=product.id,
                    field="stock",
                )
            )

        total += item.quantity * product.price

    remaining_credit = customer.credit_limit - customer.credit_used
    if total > remaining_credit:
        issues.append(
            ValidationIssue(
                code="CREDIT_LIMIT",
                message=f"Order total ₹{total:.2f} exceeds available credit ₹{remaining_credit:.2f}",
                field="credit",
            )
        )

    return ValidationResult(valid=len(issues) == 0, issues=issues, total_amount=total)
