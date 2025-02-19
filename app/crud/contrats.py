from sqlalchemy.orm import Session
from app.db.models.contrat import Contrat


def create_contrat(db: Session, id_client: int, montant_total: float):
    """Créer un contrat pour un client donné."""
    contrat = Contrat(
        id_client=id_client,
        montant_total=montant_total,
        montant_restant=montant_total,
        statut=False
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
    """Mettre à jour un contrat sans modifier un contrat signé."""
    contrat = db.query(Contrat).filter(Contrat.id == contrat_id).first()
    if contrat:
        # Empêcher la modification d'un contrat signé
        if contrat.statut and "montant_total" in updates:
            raise ValueError(
                "Impossible de modifier le montant d'un contrat signé."
            )

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
