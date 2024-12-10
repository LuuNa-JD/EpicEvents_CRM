from app.crud.clients import create_client, update_client, get_all_clients
from app.auth.permissions import commercial_required, read_only_required
from app.auth.jwt_utils import decode_token


@read_only_required
def list_all_clients(db, token):
    """Récupérer tous les clients (lecture seule pour tous les rôles)."""
    return get_all_clients(db)


@commercial_required
def create_client_for_commercial(
    db, token, nom_complet, email, telephone, entreprise
):
    """Créer un client (commercial uniquement)."""
    payload = decode_token(token)
    id_commercial = payload.get("id")
    return create_client(
        db, nom_complet, email, telephone, entreprise, id_commercial
    )


@commercial_required
def update_client_by_commercial(db, token, client_id, **updates):
    """Mettre à jour un client (commercial responsable uniquement)."""
    return update_client(db, client_id, **updates)
