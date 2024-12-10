import pytest
from app.crud.contrats import (
    create_contrat,
    get_contrat,
    update_contrat,
    delete_contrat,
)
from app.db.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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


def test_create_contrat(db):
    contrat = create_contrat(db, 1, 10000, 5000, False)
    assert contrat.id is not None
    assert contrat.montant_total == 10000


def test_get_contrat(db):
    contrat = create_contrat(db, 1, 20000, 10000, True)
    retrieved = get_contrat(db, contrat.id)
    assert retrieved.montant_total == 20000


def test_update_contrat(db):
    contrat = create_contrat(db, 1, 15000, 7500, False)
    updated = update_contrat(db, contrat.id, statut=True)
    assert updated.statut is True


def test_delete_contrat(db):
    contrat = create_contrat(db, 1, 8000, 4000, False)
    delete_contrat(db, contrat.id)
    assert get_contrat(db, contrat.id) is None
