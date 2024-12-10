from app.db.session import SessionLocal, engine # noqa
from app.db.base import Base
from app.db.models import Client, Collaborateur, Contrat, Evenement # noqa


def reset_database():
    print("Réinitialisation de la base de données...")

    # Suppression et recréation des tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    print("Base de données réinitialisée avec succès !")


if __name__ == "__main__":
    reset_database()
