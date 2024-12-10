import pytest
from app.crud.collaborateurs import (
    create_collaborateur,
    get_collaborateur,
    update_collaborateur,
    delete_collaborateur
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


def test_create_collaborateur(db):
    collaborateur = create_collaborateur(
        db,
        "Martin",
        "Paul",
        "paul@test.com",
        "gestion",
        "pmartin",
        "password123"
    )
    assert collaborateur.id is not None
    assert collaborateur.nom == "Martin"
    assert collaborateur.verify_password("password123")
    assert not collaborateur.verify_password("wrongpassword")


def test_get_collaborateur(db):
    collaborateur = create_collaborateur(
        db, "Doe", "Jane", "jane@test.com", "support", "jdoe", "pass123"
    )
    retrieved = get_collaborateur(db, collaborateur.id)
    assert retrieved.nom == "Doe"


def test_update_collaborateur(db):
    collaborateur = create_collaborateur(
        db, "Smith", "Anna", "anna@test.com", "commercial", "asmith", "pass456"
    )
    updated = update_collaborateur(db, collaborateur.id, departement="support")
    assert updated.departement == "support"


def test_delete_collaborateur(db):
    collaborateur = create_collaborateur(
        db, "Brown", "Tom", "tom@test.com", "gestion", "tbrown", "pass789"
    )
    delete_collaborateur(db, collaborateur.id)
    assert get_collaborateur(db, collaborateur.id) is None
