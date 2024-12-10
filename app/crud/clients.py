from sqlalchemy.orm import Session
from app.db.models.client import Client


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


def get_client(db: Session, client_id: int):
    """Récupérer un client par ID."""
    return db.query(Client).filter(Client.id == client_id).first()


def get_all_clients(db: Session):
    """Récupérer tous les clients."""
    return db.query(Client).all()


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
