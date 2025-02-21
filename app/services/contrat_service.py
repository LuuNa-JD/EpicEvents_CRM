from app.crud.contrats import (
    create_contrat, update_contrat, get_all_contrats
)
from app.auth.permissions import (
    gestion_required,
    commercial_required,
    read_only_required
)
from app.crud.clients import get_client
from app.db.models import Contrat, Client


@read_only_required
def list_all_contrats(db):
    """Récupérer tous les contrats (lecture seule pour tous)."""
    return get_all_contrats(db)


@gestion_required
def create_new_contrat(db, token, id_client, montant_total):
    """Créer un contrat en s'assurant que le client et son
    commercial existent."""

    # Vérifier si le client existe
    client = get_client(db, id_client)
    if not client:
        raise ValueError("Erreur : Client introuvable.")

    # Vérifier si le client est bien attribué à un commercial
    if not client.id_commercial:
        raise ValueError(
            "Erreur : Ce client n'est pas assigné à un commercial."
        )

    contrat = create_contrat(
        db,
        id_client=client.id,
        montant_total=montant_total,  # Contrat non signé par défaut
    )
    return contrat


@commercial_required
def list_contrats_by_commercial(db, user_id):
    """Lister les contrats des clients dont le commercial est responsable."""
    return db.query(Contrat).join(Client).filter(
        Client.id_commercial == user_id
    )


@commercial_required
def get_signed_contrats_for_commercial(db, user_id):
    """Récupérer les contrats signés pour un commercial."""
    return db.query(Contrat).join(Client).filter(
        Client.id_commercial == user_id,
        Contrat.statut
    ).all()


@gestion_required
def update_client_contrat(db, token, contrat_id, **updates):
    """
    Met à jour un contrat (Gestion uniquement).
    """
    return update_contrat(db, contrat_id, **updates)


@commercial_required
def update_contrat_commercial_service(db, token, contrat_id, **updates):
    """
    Permet à un commercial de modifier UNIQUEMENT ses propres contrats.
    """
    return update_contrat(db, contrat_id, **updates)
