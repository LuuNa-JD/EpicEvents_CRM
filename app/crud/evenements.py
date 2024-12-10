from sqlalchemy.orm import Session
from app.db.models.evenement import Evenement


def create_evenement(
    db: Session,
    contrat_id: int,
    support_id: int,
    date_debut,
    date_fin,
    lieu: str,
    participants: int,
    notes: str
):
    """Créer un nouvel événement."""
    evenement = Evenement(
        id_contrat=contrat_id,
        id_support=support_id,
        date_debut=date_debut,
        date_fin=date_fin,
        lieu=lieu,
        nombre_participants=participants,
        notes=notes
    )
    db.add(evenement)
    db.commit()
    db.refresh(evenement)
    return evenement


def get_evenement(db: Session, evenement_id: int):
    """Récupérer un événement par ID."""
    return db.query(Evenement).filter(Evenement.id == evenement_id).first()


def get_evenements_by_support(db: Session, support_id: int):
    """Filtrer les événements attribués au support."""
    return db.query(Evenement).filter(Evenement.id_support == support_id).all()


def get_all_evenements(db: Session):
    """Récupérer tous les événements."""
    return db.query(Evenement).all()


def update_evenement(db: Session, evenement_id: int, **updates):
    """Mettre à jour un événement."""
    evenement = db.query(Evenement).filter(
        Evenement.id == evenement_id
    ).first()
    if evenement:
        for key, value in updates.items():
            setattr(evenement, key, value)
        db.commit()
        db.refresh(evenement)
    return evenement


def delete_evenement(db: Session, evenement_id: int):
    """Supprimer un événement."""
    evenement = db.query(Evenement).filter(
        Evenement.id == evenement_id
    ).first()
    if evenement:
        db.delete(evenement)
        db.commit()
    return evenement
