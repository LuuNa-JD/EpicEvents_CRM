from app.crud.collaborateurs import (
    create_collaborateur,
    update_collaborateur,
    delete_collaborateur,
    get_all_collaborateurs,
    get_collaborateur
)
from app.db.models.collaborateur import Collaborateur
from app.auth.permissions import gestion_required
from app.db.models.collaborateur import Departement


@gestion_required
def create_new_collaborateur(
    db, token, nom, prenom, email, departement_id, login, password
):
    """Créer un nouveau collaborateur (équipe gestion)."""

    # Vérifier si le département existe bien
    departement = (
        db.query(Departement)
        .filter(Departement.id == departement_id)
        .first()
    )

    if not departement:
        raise ValueError(
            f"❌ Erreur : Aucun département avec l'ID {departement_id}."
        )

    return create_collaborateur(
        db, nom, prenom, email, departement.id, login, password
    )


@gestion_required
def all_collaborateurs(db):
    """Récupérer tous les collaborateurs."""
    return get_all_collaborateurs(db)


def get_collaborateur_by_id(db, collaborateur_id):
    """Récupérer un collaborateur par ID."""
    return get_collaborateur(db, collaborateur_id)


def list_supports(db):
    """Récupérer tous les supports."""
    return (
        db.query(Collaborateur)
        .filter(Collaborateur.departement.has(nom="support"))
        .all()
    )


@gestion_required
def update_existing_collaborateur(db, token, collaborateur_id, **updates):
    """Mettre à jour un collaborateur (équipe gestion)."""
    return update_collaborateur(db, collaborateur_id, **updates)


@gestion_required
def delete_collaborateur_service(db, token, collaborateur_id):
    """Supprimer un collaborateur (équipe gestion)."""
    return delete_collaborateur(db, collaborateur_id)
