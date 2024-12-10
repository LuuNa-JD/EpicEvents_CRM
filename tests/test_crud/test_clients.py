import pytest
from app.crud.clients import (
    create_client,
    get_client,
    get_all_clients,
    update_client,
    delete_client,
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


def test_create_client(db):
    client = create_client(
        db, "Jean Dupont", "jean@test.com", "0606060606", "Entreprise X", 1
    )
    assert client.id is not None
    assert client.nom_complet == "Jean Dupont"


def test_get_client(db):
    client = create_client(
        db, "Alice Smith", "alice@startup.com", "0123456789", "Startup Y", 1
    )
    retrieved_client = get_client(db, client.id)
    assert retrieved_client.nom_complet == "Alice Smith"


def test_get_all_clients(db):
    create_client(
        db, "Client 1", "client1@test.com", "0601010101", "Company A", 1
    )
    create_client(
        db, "Client 2", "client2@test.com", "0602020202", "Company B", 1
    )
    clients = get_all_clients(db)
    assert len(clients) == 2


def test_update_client(db):
    client = create_client(
        db, "Bob", "bob@company.com", "0987654321", "Company Z", 1
    )
    updated_client = update_client(db, client.id, nom_complet="Bob Updated")
    assert updated_client.nom_complet == "Bob Updated"


def test_delete_client(db):
    client = create_client(
        db, "John Doe", "john@xyz.com", "123456789", "XYZ Corp", 1
    )
    deleted_client = delete_client(db, client.id)
    assert deleted_client is not None
    assert get_client(db, client.id) is None
