from sqlalchemy.orm import Session
from app.db.models.collaborateur import Collaborateur
from app.auth.jwt_utils import generate_token
from app.utils.file_utils import save_token


def authentifier_collaborateur(db: Session, login: str, password: str):
    """Authentifie un collaborateur via son login et mot de passe."""
    collaborateur = (
        db.query(Collaborateur)
        .filter(Collaborateur.login == login)
        .first()
    )
    if collaborateur and collaborateur.verify_password(password):
        return collaborateur
    return None


def login(db: Session, login: str, password: str):
    """Authentifie un utilisateur et retourne un JWT."""
    collaborateur = authentifier_collaborateur(db, login, password)
    if collaborateur:
        token = generate_token(
            user_id=collaborateur.id,
            role=collaborateur.departement
        )
        save_token(token)
        print("Authentification réussie. Votre jeton a été sauvegardé.")
        return token
    else:
        print("Erreur : Login ou mot de passe incorrect.")
        return None
