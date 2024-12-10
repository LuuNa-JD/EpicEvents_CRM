from sqlalchemy.orm import Session
from app.db.models.collaborateur import Collaborateur


def create_collaborateur(
    db: Session,
    nom: str,
    prenom: str,
    email: str,
    departement: str,
    login: str,
    password: str
):
    """Créer un nouveau collaborateur."""
    collaborateur = Collaborateur(
        nom=nom,
        prenom=prenom,
        email=email,
        departement=departement,
        login=login,
        password_hash=Collaborateur.set_password(password)
    )
    db.add(collaborateur)
    db.commit()
    db.refresh(collaborateur)
    return collaborateur


def get_collaborateur(db: Session, collaborateur_id: int):
    """Récupérer un collaborateur par ID."""
    return db.query(Collaborateur) \
             .filter(Collaborateur.id == collaborateur_id) \
             .first()


def get_all_collaborateurs(db: Session):
    """Récupérer tous les collaborateurs."""
    return db.query(Collaborateur).all()


def update_collaborateur(db: Session, collaborateur_id: int, **updates):
    """Mettre à jour un collaborateur."""
    collaborateur = db.query(Collaborateur) \
                      .filter(Collaborateur.id == collaborateur_id) \
                      .first()
    if collaborateur:
        for key, value in updates.items():
            setattr(collaborateur, key, value)
        db.commit()
        db.refresh(collaborateur)
    return collaborateur


def delete_collaborateur(db: Session, collaborateur_id: int):
    """Supprimer un collaborateur."""
    collaborateur = db.query(Collaborateur) \
                      .filter(Collaborateur.id == collaborateur_id) \
                      .first()
    if collaborateur:
        db.delete(collaborateur)
        db.commit()
    return collaborateur
