from sqlalchemy.orm import Session
from app.crud.collaborateurs import authentifier_collaborateur_from_crud
from app.auth.jwt_utils import generate_token
from app.utils.file_utils import save_token


def authentifier_collaborateur(db: Session, login: str, password: str):
    """Authentifie un collaborateur via son login et mot de passe."""
    collaborateur = authentifier_collaborateur_from_crud(db, login, password)
    if collaborateur:
        return collaborateur
    return None


def login(db: Session, login: str, password: str):
    """Authentifie un utilisateur et retourne un JWT."""
    collaborateur = authentifier_collaborateur(db, login, password)
    if collaborateur:
        role = collaborateur.departement.nom
        token = generate_token(
            user_id=collaborateur.id,
            role=role,
            nom=collaborateur.nom,
            prenom=collaborateur.prenom
        )
        save_token(token)
        print("Authentification réussie. Votre jeton a été sauvegardé.")
        return token
    else:
        print("Erreur : Login ou mot de passe incorrect.")
        return None
