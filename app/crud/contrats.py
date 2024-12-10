from sqlalchemy.orm import Session
from app.db.models.contrat import Contrat


def create_contrat(
    db: Session, client_id: int, montant_total: float,
    montant_restant: float, statut: bool
):
    """Créer un nouveau contrat."""
    contrat = Contrat(
        id_client=client_id,
        montant_total=montant_total,
        montant_restant=montant_restant,
        statut=statut
    )
    db.add(contrat)
    db.commit()
    db.refresh(contrat)
    return contrat


def get_contrat(db: Session, contrat_id: int):
    """Récupérer un contrat par ID."""
    return db.query(Contrat).filter(Contrat.id == contrat_id).first()


def get_contracts_by_status(db: Session, statut: bool):
    """Filtrer les contrats par statut."""
    return db.query(Contrat).filter(Contrat.statut == statut).all()


def get_all_contrats(db: Session):
    """Récupérer tous les contrats."""
    return db.query(Contrat).all()


def update_contrat(db: Session, contrat_id: int, **updates):
    """Mettre à jour un contrat."""
    contrat = db.query(Contrat).filter(Contrat.id == contrat_id).first()
    if contrat:
        for key, value in updates.items():
            setattr(contrat, key, value)
        db.commit()
        db.refresh(contrat)
    return contrat


def delete_contrat(db: Session, contrat_id: int):
    """Supprimer un contrat."""
    contrat = db.query(Contrat).filter(Contrat.id == contrat_id).first()
    if contrat:
        db.delete(contrat)
        db.commit()
    return contrat
