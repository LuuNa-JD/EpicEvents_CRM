from app.db.session import SessionLocal
from app.db.models.collaborateur import Collaborateur
from app.db.models.client import Client
from app.db.models.contrat import Contrat
from app.db.models.evenement import Evenement
from datetime import datetime
import logging

logging.getLogger('passlib').setLevel(logging.ERROR)


def seed_data():
    db = SessionLocal()
    try:
        # Collaborateurs
        admin = Collaborateur(
            nom="Admin",
            prenom="John",
            email="admin@example.com",
            departement="gestion",
            login="admin",
            password_hash=Collaborateur.set_password("admin123")
        )
        commercial = Collaborateur(
            nom="Smith",
            prenom="Anna",
            email="anna.smith@example.com",
            departement="commercial",
            login="anna",
            password_hash=Collaborateur.set_password("password123")
        )
        support = Collaborateur(
            nom="Doe",
            prenom="Jane",
            email="jane.doe@example.com",
            departement="support",
            login="jane",
            password_hash=Collaborateur.set_password("support123")
        )

        db.add_all([admin, commercial, support])
        db.commit()

        # Clients
        client1 = Client(
            nom_complet="Kevin Casey",
            email="kevin@startup.io",
            telephone="+678 123 456 78",
            nom_entreprise="Cool Startup LLC",
            id_commercial=commercial.id
        )
        client2 = Client(
            nom_complet="Alice Cooper",
            email="alice@enterprise.com",
            telephone="+123 456 789",
            nom_entreprise="Enterprise Solutions",
            id_commercial=commercial.id
        )

        db.add_all([client1, client2])
        db.commit()

        # Contrats
        contrat1 = Contrat(
            id_client=client1.id,
            montant_total=10000.00,
            montant_restant=5000.00,
            statut=False
        )
        contrat2 = Contrat(
            id_client=client2.id,
            montant_total=20000.00,
            montant_restant=15000.00,
            statut=True
        )

        db.add_all([contrat1, contrat2])
        db.commit()

        # Événements
        evenement1 = Evenement(
            id_contrat=contrat1.id,
            id_support=support.id,
            date_debut=datetime(2023, 6, 4, 13, 0),
            date_fin=datetime(2023, 6, 5, 2, 0),
            lieu="53 Rue du Château, 41120 Candé-sur-Beuvron, France",
            nombre_participants=75,
            notes="Wedding starts at 3PM, by the river. Catering is organized."
        )
        evenement2 = Evenement(
            id_contrat=contrat2.id,
            id_support=support.id,
            date_debut=datetime(2023, 7, 1, 14, 0),
            date_fin=datetime(2023, 7, 2, 22, 0),
            lieu="123 Main Street, Cityville, USA",
            nombre_participants=120,
            notes="Corporate event with keynote speakers and a gala dinner."
        )

        db.add_all([evenement1, evenement2])
        db.commit()

        print("Données de seed ajoutées avec succès.")
    except Exception as e:
        print(f"Erreur lors de l'insertion des données : {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
