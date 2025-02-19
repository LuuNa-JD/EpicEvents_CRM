from sqlalchemy.orm import Session
from app.db.models.collaborateur import Collaborateur
from app.db.models.collaborateur import Departement


def create_collaborateur(
    db: Session,
    nom: str,
    prenom: str,
    email: str,
    departement_id: int,
    login: str,
    password: str
):
    """Créer un nouveau collaborateur."""

    departement = db.query(Departement) \
                    .filter(Departement.id == departement_id) \
                    .first()
    if not departement:
        raise ValueError(
            f"Erreur : Aucun département avec l'ID {departement_id}."
        )

    collaborateur = Collaborateur(
        nom=nom,
        prenom=prenom,
        email=email,
        departement_id=departement.id,
        login=login,
        password_hash=Collaborateur.set_password(password)
    )

    db.add(collaborateur)
    db.commit()
    db.refresh(collaborateur)
    return collaborateur


def authentifier_collaborateur_from_crud(
    db: Session, login: str, password: str
):
    """Authentifie un collaborateur via son login et mot de passe."""
    collaborateur = (
        db.query(Collaborateur)
        .filter(Collaborateur.login == login)
        .first()
    )
    if collaborateur and collaborateur.verify_password(password):
        return collaborateur
    return None


def get_collaborateur(db: Session, collaborateur_id: int):
    """Récupérer un collaborateur par ID."""
    return db.query(Collaborateur) \
             .filter(Collaborateur.id == collaborateur_id) \
             .first()


def get_support(db: Session, support_id: int):
    """Récupérer un support par ID."""
    return db.query(Collaborateur) \
             .filter(Collaborateur.id == support_id) \
             .filter(Collaborateur.departement.has(nom="support")) \
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
