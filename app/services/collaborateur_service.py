from app.crud.collaborateurs import (
    create_collaborateur, update_collaborateur, delete_collaborateur
)
from app.auth.permissions import gestion_required


@gestion_required
def create_new_collaborateur(
    db, token, nom, prenom, email, departement, login, password
):
    """Créer un nouveau collaborateur (équipe gestion)."""
    return create_collaborateur(
        db, nom, prenom, email, departement, login, password
    )


@gestion_required
def update_existing_collaborateur(db, token, collaborateur_id, **updates):
    """Mettre à jour un collaborateur (équipe gestion)."""
    return update_collaborateur(db, collaborateur_id, **updates)


@gestion_required
def delete_collaborateur_service(db, token, collaborateur_id):
    """Supprimer un collaborateur (équipe gestion)."""
    return delete_collaborateur(db, collaborateur_id)
