import pytest
from app.crud.evenements import (
    create_evenement,
    get_evenement,
    update_evenement,
    delete_evenement,
)
from app.db.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


def test_create_evenement(db):
    evenement = create_evenement(
        db, 1, 1, datetime.now(), datetime.now(), "Lieu", 100, "Notes"
    )
    assert evenement.id is not None
    assert evenement.lieu == "Lieu"


def test_get_evenement(db):
    evenement = create_evenement(
        db, 1, 1, datetime.now(), datetime.now(), "Lieu A", 50, "Notes A"
    )
    retrieved = get_evenement(db, evenement.id)
    assert retrieved.lieu == "Lieu A"


def test_update_evenement(db):
    evenement = create_evenement(
        db, 1, 1, datetime.now(), datetime.now(), "Lieu B", 60, "Notes B"
    )
    updated = update_evenement(db, evenement.id, lieu="Lieu C")
    assert updated.lieu == "Lieu C"


def test_delete_evenement(db):
    evenement = create_evenement(
        db, 1, 1, datetime.now(), datetime.now(), "Lieu D", 70, "Notes D"
    )
    delete_evenement(db, evenement.id)
    assert get_evenement(db, evenement.id) is None
