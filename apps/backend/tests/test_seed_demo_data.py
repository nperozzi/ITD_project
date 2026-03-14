from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.base import Base
from db.models import Gateway, Product, Promotion, ShelfLocation, Store, Tag, TagPayload
from seeds.demo_data import seed_demo_data


def make_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    return Session()


def test_seed_demo_data_creates_full_demo_dataset():
    db = make_session()

    seed_demo_data(db)

    assert db.query(Store).count() == 2
    assert db.query(Gateway).count() == 3
    assert db.query(ShelfLocation).count() == 3
    assert db.query(Product).count() == 3
    assert db.query(Tag).count() == 3
    assert db.query(Promotion).count() == 2
    assert db.query(TagPayload).count() == 2


def test_seed_demo_data_is_idempotent():
    db = make_session()

    seed_demo_data(db)
    seed_demo_data(db)

    assert db.query(Store).count() == 2
    assert db.query(Gateway).count() == 3
    assert db.query(ShelfLocation).count() == 3
    assert db.query(Product).count() == 3
    assert db.query(Tag).count() == 3
    assert db.query(Promotion).count() == 2
    assert db.query(TagPayload).count() == 2
