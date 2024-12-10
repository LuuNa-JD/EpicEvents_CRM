from app.crud.contrats import (
    create_contrat, update_contrat, get_all_contrats, get_contracts_by_status
)
from app.auth.permissions import (
    gestion_required,
    commercial_required,
    read_only_required
)


@read_only_required
def list_all_contrats(db, token):
    """Récupérer tous les contrats (lecture seule pour tous)."""
    return get_all_contrats(db)


@commercial_required
def create_contrat_for_client(
    db, token, id_client, montant_total, montant_restant, statut
):
    """Créer un contrat pour un client (commercial uniquement)."""
    return create_contrat(
        db, id_client, montant_total, montant_restant, statut
    )


@commercial_required
def update_client_contract(db, token, contrat_id, **updates):
    """Mettre à jour un contrat des clients dont le commercial est
    responsable."""
    return update_contrat(db, contrat_id, **updates)


@gestion_required
def update_any_contract(db, token, contrat_id, **updates):
    """Mettre à jour n'importe quel contrat (équipe gestion)."""
    return update_contrat(db, contrat_id, **updates)


@commercial_required
def filter_contracts_by_status(db, token, statut: bool):
    """Filtrer les contrats non signés ou non payés."""
    return get_contracts_by_status(db, statut)
