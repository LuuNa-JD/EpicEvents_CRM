from app.crud.evenements import (
    create_evenement,
    update_evenement,
    get_all_evenements,
    get_evenement,
    get_evenements_by_support
)
from app.crud.collaborateurs import get_support
from app.auth.jwt_utils import decode_token
from app.auth.permissions import (
    gestion_required,
    commercial_required,
    support_required,
    read_only_required
)
from app.db.models.contrat import Contrat
from app.db.models.evenement import Evenement


@read_only_required
def list_all_evenements(db, token):
    """Récupérer tous les événements (lecture seule pour tous)."""
    return get_all_evenements(db)


@commercial_required
def create_event_for_client(
    db, token, id_contrat, date_debut, date_fin, lieu, participants, notes
):
    """Créer un événement pour un client (commercial uniquement)."""
    payload = decode_token(token)
    user_id = payload.get("user_id")

    contrat = db.query(Contrat).filter(Contrat.id == id_contrat).first()
    if not contrat or not contrat.statut:
        raise ValueError(
            "Impossible de créer un événement pour un contrat non signé."
        )
    if contrat.client.id_commercial != user_id:
        raise ValueError(
            "Vous ne pouvez créer un événement que pour vos propres clients."
        )

    return create_evenement(
        db, id_contrat, None, date_debut, date_fin, lieu, participants, notes
    )


@gestion_required
def assign_support(db, token, evenement_id: int, support_id: int):
    """Assigner un support à un événement (Gestion uniquement)."""
    evenement = get_evenement(db, evenement_id)
    support = get_support(db, support_id)

    if not evenement:
        raise ValueError("Aucun événement trouvé avec cet ID.")
    if evenement.id_support:
        raise ValueError("Cet événement a déjà un support assigné.")
    if not support:
        raise ValueError("Le support sélectionné n'existe pas ou n'est pas dans le bon département.")

    evenement.id_support = support_id
    db.commit()
    db.refresh(evenement)
    return evenement


@support_required
def list_events_for_support(db, token):
    """Filtrer les événements attribués au support connecté."""
    payload = decode_token(token)
    id_support = payload.get("user_id")

    if not id_support:
        raise ValueError(
            "Erreur : Impossible de récupérer l'ID du support depuis le token."
        )

    return get_evenements_by_support(db, id_support)


@gestion_required
def get_unassigned_evenements(db):
    """Retourne la liste des événements sans support attribué."""
    return db.query(Evenement).filter(Evenement.id_support is None).all()


@support_required
def update_event_by_support(db, token, event_id, **updates):
    """Mettre à jour les événements attribués au support."""
    return update_evenement(db, event_id, **updates)


@gestion_required
def assign_support_to_event(db, token, event_id, id_support):
    """Associer un support à un événement (équipe gestion uniquement)."""
    return update_evenement(db, event_id, id_support=id_support)
