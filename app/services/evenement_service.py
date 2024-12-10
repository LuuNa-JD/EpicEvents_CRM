from app.crud.evenements import (
    create_evenement,
    update_evenement,
    get_all_evenements,
    get_evenements_by_support
)
from app.auth.jwt_utils import decode_token
from app.auth.permissions import (
    gestion_required,
    commercial_required,
    support_required,
    read_only_required
)


@read_only_required
def list_all_evenements(db, token):
    """Récupérer tous les événements (lecture seule pour tous)."""
    return get_all_evenements(db)


@commercial_required
def create_event_for_client(
    db, token, id_contrat, id_support, date_debut, date_fin, lieu,
    participants, notes
):
    """Créer un événement pour un client (commercial uniquement)."""
    return create_evenement(
        db, id_contrat, id_support, date_debut, date_fin, lieu,
        participants, notes
    )


@support_required
def list_events_for_support(db, token):
    """Filtrer les événements attribués au support."""
    payload = decode_token(token)
    id_support = payload.get("id")
    return get_evenements_by_support(db, id_support)


@support_required
def update_event_by_support(db, token, event_id, **updates):
    """Mettre à jour les événements attribués au support."""
    return update_evenement(db, event_id, **updates)


@gestion_required
def assign_support_to_event(db, token, event_id, id_support):
    """Associer un support à un événement (équipe gestion uniquement)."""
    return update_evenement(db, event_id, id_support=id_support)
