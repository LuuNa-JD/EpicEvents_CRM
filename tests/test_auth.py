import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models.collaborateur import Collaborateur
from app.auth.login import authentifier_collaborateur, login
from app.auth.jwt_utils import decode_token
from app.db.base import Base
from datetime import datetime, timedelta
import jwt
from app.core.config import settings


# Configuration de la base de données pour les tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


# Fixure pour initialiser la base de données de test
@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)  # Création des tables
    db = TestingSessionLocal()
    yield db  # Session test
    db.close()
    Base.metadata.drop_all(bind=engine)  # Nettoyage des tables après test


def test_authentification_reussie(db):
    password = "securepass"
    collaborateur = Collaborateur(
        nom="Martin",
        prenom="Paul",
        email="paul@test.com",
        departement="commercial",
        login="pmartin",
        password_hash=Collaborateur.set_password(password)
    )
    db.add(collaborateur)
    db.commit()
    utilisateur = authentifier_collaborateur(db, "pmartin", password)
    assert utilisateur is not None


def test_authentification_echouee(db):
    password = "securepass"
    collaborateur = Collaborateur(
        nom="Martin",
        prenom="Paul",
        email="paul@test.com",
        departement="commercial",
        login="pmartin",
        password_hash=Collaborateur.set_password(password)
    )
    db.add(collaborateur)
    db.commit()
    utilisateur = authentifier_collaborateur(db, "pmartin", "wrongpass")
    assert utilisateur is None


def test_jwt_generation_apres_authentification(db):
    password = "securepass"
    collaborateur = Collaborateur(
        nom="Martin",
        prenom="Paul",
        email="paul@test.com",
        departement="gestion",
        login="pmartin",
        password_hash=Collaborateur.set_password(password)
    )
    db.add(collaborateur)
    db.commit()

    token = login(db, "pmartin", password)  # Utilise la fonction de login
    assert token is not None

    decoded_token = decode_token(token)  # Décoder le JWT
    assert decoded_token["user_id"] == collaborateur.id
    assert decoded_token["role"] == "gestion"
    assert "exp" in decoded_token  # Vérifie l'expiration


def test_jwt_decodage_valide():
    payload = {
        "user_id": 1,
        "role": "commercial",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    decoded = decode_token(token)
    assert decoded["user_id"] == 1
    assert decoded["role"] == "commercial"


def test_jwt_expiration():
    payload = {
        "user_id": 1,
        "role": "commercial",
        "exp": datetime.utcnow() - timedelta(seconds=1)  # Token expiré
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    decoded = decode_token(token)
    assert decoded is None  # JWT expiré, devrait retourner None


def test_jwt_invalide():
    token = "invalid.token.here"

    decoded = decode_token(token)
    assert decoded is None  # JWT invalide, devrait retourner None


def test_login_avec_jwt(db):
    password = "mypassword"
    collaborateur = Collaborateur(
        nom="Doe",
        prenom="Jane",
        email="jane@test.com",
        departement="support",
        login="jdoe",
        password_hash=Collaborateur.set_password(password)
    )
    db.add(collaborateur)
    db.commit()

    from app.auth.login import login
    token = login(db, "jdoe", password)
    assert token is not None

    decoded_token = decode_token(token)
    assert decoded_token["user_id"] == collaborateur.id
    assert decoded_token["role"] == "support"
