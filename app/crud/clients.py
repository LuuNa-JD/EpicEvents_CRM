from sqlalchemy.orm import Session
from app.db.models.client import Client
from sqlalchemy.orm import load_only
from rich.console import Console

console = Console()


def create_client(
    db: Session, nom_complet: str, email: str, telephone: str,
    entreprise: str, commercial_id: int
):
    """Créer un nouveau client."""
    client = Client(
        nom_complet=nom_complet,
        email=email,
        telephone=telephone,
        nom_entreprise=entreprise,
        id_commercial=commercial_id
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def get_client(db, client_id):
    """Récupérer un client en s'assurant que id_commercial est bien chargé."""
    client = (
        db.query(Client)
        .options(
            load_only(Client.id, Client.nom_complet, Client.id_commercial)
        )
        .filter(Client.id == client_id)
        .first()
    )
    return client


def get_clients_by_commercial(db: Session, commercial_id: int):
    """Récupérer des clients pour un commercial."""
    return db.query(Client).filter(Client.id_commercial == commercial_id).all()


def get_all_clients(
    db: Session, user_id: int, role: str, all_clients: bool = False
):
    """Récupérer tous les clients en fonction du rôle de l'utilisateur."""
    if role == "commercial" and not all_clients:
        return db.query(Client).filter(Client.id_commercial == user_id).all()
    return db.query(Client).all()


def get_client_id(db, client_id):
    """Récupérer un client par ID."""
    return db.query(Client).filter(Client.id == client_id).first()


def update_client(db: Session, client_id: int, **updates):
    """Mettre à jour les informations d'un client."""
    client = db.query(Client).filter(Client.id == client_id).first()
    if client:
        for key, value in updates.items():
            setattr(client, key, value)
        db.commit()
        db.refresh(client)
    return client


def delete_client(db: Session, client_id: int):
    """Supprimer un client."""
    client = db.query(Client).filter(Client.id == client_id).first()
    if client:
        db.delete(client)
        db.commit()
    return client
