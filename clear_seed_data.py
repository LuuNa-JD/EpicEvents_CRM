from app.db.session import SessionLocal
from app.db.models.collaborateur import Collaborateur, Departement
from app.db.models.client import Client
from app.db.models.contrat import Contrat
from app.db.models.evenement import Evenement


def clear_seed_data():
    db = SessionLocal()
    try:
        print("Suppression des données de seed...")

        db.query(Evenement).delete()
        db.query(Contrat).delete()
        db.query(Client).delete()
        db.query(Collaborateur).delete()
        db.query(Departement).delete()

        db.commit()
        print("Données de seed supprimées avec succès.")
    except Exception as e:
        print(f"Erreur lors de la suppression des données : {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    clear_seed_data()
