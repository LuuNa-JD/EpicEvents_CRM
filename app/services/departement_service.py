

from app.db.models.collaborateur import Departement
from sqlalchemy.orm import Session
from typing import List


def get_all_departements(db: Session) -> List[Departement]:
    """
    Récupère tous les départements de la base de données.
    """
    return db.query(Departement).all()
