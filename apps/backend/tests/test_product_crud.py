from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.base import Base
from db.crud.product import (
    create_product,
    delete_product,
    get_all_products,
    get_product,
    update_product,
)
from db.models.shelfLocation import ShelfLocation  # noqa: F401
from db.models.tag import Tag  # noqa: F401


def make_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    return Session()


def test_create_and_get_product():
    db = make_session()
    product = create_product(
        db,
        sku="SKU-001",
        name="Arabica Beans",
        attributes_json={"origin": "Brazil", "weight_g": 1000},
        price=22.9,
    )
    assert product.id is not None
    fetched = get_product(db, product.id)
    assert fetched is not None
    assert fetched.sku == "SKU-001"
    assert fetched.name == "Arabica Beans"
    assert fetched.attributes_json == {"origin": "Brazil", "weight_g": 1000}
    assert fetched.price == 22.9


def test_get_all_products():
    db = make_session()
    create_product(db, "SKU-A", "A", {"k": "a"}, 1.0)
    create_product(db, "SKU-B", "B", {"k": "b"}, 2.0)
    products = get_all_products(db)
    assert len(products) == 2
    assert {p.sku for p in products} == {"SKU-A", "SKU-B"}


def test_update_product():
    db = make_session()
    product = create_product(db, "SKU-OLD", "Old", {"color": "green"}, 3.5)
    updated = update_product(
        db,
        product.id,
        sku="SKU-NEW",
        name="New",
        attributes_json={"color": "yellow"},
        price=4.25,
    )
    assert updated is not None
    assert updated.sku == "SKU-NEW"
    assert updated.name == "New"
    assert updated.attributes_json == {"color": "yellow"}
    assert updated.price == 4.25


def test_update_product_ignores_unknown_fields():
    db = make_session()
    product = create_product(db, "SKU-1", "One", {"size": "S"}, 1.5)
    updated = update_product(db, product.id, not_a_field="ignored")
    assert updated is not None
    assert updated.sku == "SKU-1"
    assert not hasattr(updated, "not_a_field")


def test_update_unknown_product_returns_none():
    db = make_session()
    assert update_product(db, 999, name="X") is None


def test_delete_product():
    db = make_session()
    product = create_product(db, "SKU-DEL", "ToDelete", {"x": 1}, 9.9)
    assert delete_product(db, product.id) is True
    assert get_product(db, product.id) is None


def test_delete_unknown_product_returns_false():
    db = make_session()
    assert delete_product(db, 999) is False
