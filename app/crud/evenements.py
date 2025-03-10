from sqlalchemy.orm import Session
from app.db.models.evenement import Evenement
from app.db.models.contrat import Contrat


def create_evenement(
    db: Session,
    contrat_id: int,
    support_id: int,
    date_debut,
    date_fin,
    lieu,
    participants,
    notes
):
    """Créer un événement uniquement si le contrat est signé."""
    contrat = db.query(Contrat).filter(Contrat.id == contrat_id).first()
    if not contrat or not contrat.statut:
        raise ValueError(
            "Impossible de créer un événement pour un contrat non signé."
        )

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


def get_evenement_for_support(db: Session, evenement_id: int, support_id: int):
    """Récupérer un événement par ID pour un support."""
    return db.query(Evenement).filter(
                Evenement.id == evenement_id,
                Evenement.id_support == support_id
            ).first()


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
