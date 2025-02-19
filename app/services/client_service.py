from app.crud.clients import create_client, update_client, get_client
from app.auth.permissions import commercial_required, read_only_required
from app.auth.jwt_utils import decode_token
from rich.console import Console
from sqlalchemy.orm import joinedload
from app.db.models.client import Client

console = Console()


@read_only_required
def list_all_clients(db, token, all_clients: bool = False):
    """Récupérer les clients en fonction du rôle."""
    payload = decode_token(token)
    if not payload:
        console.print("[bold red] Erreur : Token invalide ou expiré.[/bold red]")
        return []

    user_id = payload.get("user_id")
    role = payload.get("role")

    # Récupérer les clients selon le rôle
    if role == "commercial" and not all_clients:
        return db.query(Client).filter(Client.id_commercial == user_id).all()

    if role in ["gestion", "support"] and not all_clients:
        console.print("[bold red] Accès interdit : Vous ne pouvez pas accéder à 'MES CLIENTS'.[/bold red]")
        return []

    return db.query(Client).all()


@read_only_required
def get_client_details(db, client_id, user_id, role):
    """
    Récupère tous les détails d'un client, y compris :
    - Le commercial associé
    - Les contrats liés
    - Toutes les informations du client
    """
    client = (
        db.query(Client)
        .options(
            joinedload(Client.commercial),
            joinedload(Client.contrats)
        )
        .filter(Client.id == client_id)
        .first()
    )

    if not client:
        raise ValueError("Client introuvable.")

    if role not in ["commercial", "gestion", "support"]:
        raise PermissionError("Accès refusé : Vous ne pouvez pas voir les détails de ce client.")

    return client


@commercial_required
def create_client_for_commercial(
    db, user_id, nom_complet, email, telephone, entreprise
):
    """Créer un client (commercial uniquement)."""
    client = create_client(
        db, nom_complet, email, telephone, entreprise, user_id
    )
    console.print(f"[bold cyan]Vérification : Client lié à Commercial ID {client.id_commercial}[/bold cyan]")
    return client


@commercial_required
def update_client_by_commercial(db, token, client_id, **updates):
    """
    Mettre à jour un client (seulement si le commercial est propriétaire).
    """
    payload = decode_token(token)
    user_id = payload.get("user_id")

    client = get_client(db, client_id)
    if not client:
        raise ValueError("Client introuvable.")
    # Vérification d'accès
    if int(client.id_commercial) != int(user_id):
        raise PermissionError(
            "Accès refusé : Vous ne pouvez modifier que vos propres clients."
        )

    return update_client(db, client_id, **updates)
