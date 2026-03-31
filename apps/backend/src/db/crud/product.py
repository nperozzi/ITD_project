from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models.product import Product
from db.models.tag import Tag


def create_product(
    db: Session,
    sku: str,
    name: str,
    attributes_json: dict[str, Any],
    price: float,
) -> Product:
    product = Product(
        sku = sku,
        name = name,
        attributes_json = attributes_json,
        price = price,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


def get_product(db: Session, product_id: int) -> Product | None:
    return db.get(Product, product_id)


def get_all_products(db: Session):
    products = select(Product)
    return db.scalars(products).all()


def get_tags_for_product(db: Session, product_id: int) -> list[Tag]:
    stmt = select(Tag).where(Tag.product_id == product_id)
    return db.scalars(stmt).all()


def update_product(db: Session, product_id: int, **kwargs: Any) -> Product | None:
    product = db.get(Product, product_id)

    if not product:
        return None

    for key, value in kwargs.items():
        if hasattr(product, key):
            setattr(product, key, value)

    db.commit()
    db.refresh(product)

    return product


def delete_product(db: Session, product_id: int) -> bool:
    product = db.get(Product, product_id)

    if not product:
        return False

    db.delete(product)
    db.commit()

    return True
