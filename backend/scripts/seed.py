import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from app.database import SessionLocal, init_db
from app.models import Customer, Product


PRODUCTS = [
    {"sku": "RICE-001", "name": "Basmati Rice", "name_hi": "बासमती चावल", "name_ta": "பாஸ்மதி அரிசி", "category": "grains", "unit": "kg", "price": 85, "stock": 500, "min_qty": 5, "aliases": ["basmati", "chawal", "rice"], "synonyms": ["basmati chawal", "premium rice"]},
    {"sku": "ATTA-001", "name": "Whole Wheat Atta", "name_hi": "गेहूं का आटा", "name_ta": "கோதுமை மாவு", "category": "grains", "unit": "kg", "price": 42, "stock": 300, "min_qty": 5, "aliases": ["atta", "flour", "gehu atta"], "synonyms": ["wheat flour"]},
    {"sku": "DAL-001", "name": "Toor Dal", "name_hi": "अरहर दाल", "name_ta": "துவரம் பருப்பு", "category": "pulses", "unit": "kg", "price": 120, "stock": 200, "min_qty": 2, "aliases": ["toor", "arhar dal", "thuvaram paruppu"], "synonyms": ["pigeon pea"]},
    {"sku": "OIL-001", "name": "Sunflower Oil", "name_hi": "सूरजमुखी तेल", "name_ta": "சூரியகாந்தி எண்ணெய்", "category": "oil", "unit": "ltr", "price": 145, "stock": 150, "min_qty": 1, "aliases": ["oil", "tel", "ennai", "sunflower"], "synonyms": ["cooking oil"]},
    {"sku": "SUG-001", "name": "White Sugar", "name_hi": "चीनी", "name_ta": "சர்க்கரை", "category": "essentials", "unit": "kg", "price": 48, "stock": 400, "min_qty": 2, "aliases": ["sugar", "cheeni", "sakkarai"], "synonyms": []},
    {"sku": "MLK-001", "name": "Toned Milk", "name_hi": "टोन्ड दूध", "name_ta": "டோன்டு பால்", "category": "dairy", "unit": "ltr", "price": 58, "stock": 100, "min_qty": 2, "aliases": ["milk", "doodh", "paal"], "synonyms": []},
    {"sku": "ONI-001", "name": "Red Onion", "name_hi": "प्याज", "name_ta": "வெங்காயம்", "category": "vegetables", "unit": "kg", "price": 35, "stock": 250, "min_qty": 5, "aliases": ["onion", "pyaz", "vengayam"], "synonyms": []},
    {"sku": "POT-001", "name": "Potato", "name_hi": "आलू", "name_ta": "உருளைக்கிழங்கு", "category": "vegetables", "unit": "kg", "price": 28, "stock": 300, "min_qty": 5, "aliases": ["potato", "aloo", "urulai"], "synonyms": []},
    {"sku": "TEA-001", "name": "Premium Tea", "name_hi": "चाय", "name_ta": "தேநீர்", "category": "beverages", "unit": "kg", "price": 420, "stock": 80, "min_qty": 0.5, "aliases": ["tea", "chai"], "synonyms": ["black tea"]},
    {"sku": "DET-001", "name": "Detergent Powder", "name_hi": "डिटर्जेंट", "name_ta": "சோப்பு தூள்", "category": "household", "unit": "kg", "price": 95, "stock": 120, "min_qty": 1, "aliases": ["detergent", "washing powder"], "synonyms": []},
]

CUSTOMERS = [
    {"name": "Rajesh Kumar", "phone": "+919876543210", "language": "hi", "credit_limit": 100000, "credit_used": 12000, "preferred_products": ["Basmati Rice", "Toor Dal"], "aliases": {"chawal": "Basmati Rice"}},
    {"name": "Priya Menon", "phone": "+919123456789", "language": "en", "credit_limit": 75000, "credit_used": 8000, "preferred_products": ["Sunflower Oil", "Toned Milk"], "aliases": {}},
    {"name": "Murugan S", "phone": "+919988776655", "language": "ta", "credit_limit": 60000, "credit_used": 5000, "preferred_products": ["Basmati Rice", "Red Onion"], "aliases": {"arisi": "Basmati Rice"}},
    {"name": "Anita Sharma", "phone": "+919811223344", "language": "mixed", "credit_limit": 90000, "credit_used": 15000, "preferred_products": ["Whole Wheat Atta", "White Sugar"], "aliases": {}},
]


async def seed() -> None:
    await init_db()
    async with SessionLocal() as db:
        existing = (await db.execute(select(Product))).scalars().first()
        if existing:
            print("Database already seeded.")
            return

        for p in PRODUCTS:
            db.add(Product(**p))
        for c in CUSTOMERS:
            db.add(Customer(**c))
        await db.commit()
        print(f"Seeded {len(PRODUCTS)} products and {len(CUSTOMERS)} customers.")


if __name__ == "__main__":
    asyncio.run(seed())
