from app.db.session import SessionLocal
from app.db.models.collaborateur import Collaborateur, Departement
from app.db.models.client import Client
from app.db.models.contrat import Contrat
from app.db.models.evenement import Evenement
from datetime import datetime
import logging

logging.getLogger('passlib').setLevel(logging.ERROR)


def seed_departements():
    """
    Ajoute les départements dans la base de données s'ils n'existent pas déjà.
    """
    with SessionLocal() as db:
        departements = ["gestion", "support", "commercial"]
        for departement in departements:
            if not db.query(Departement).filter(
                Departement.nom == departement
            ).first():
                db.add(Departement(nom=departement))
        db.commit()
        print("Départements ajoutés avec succès.")


def seed_data():
    """Ajoute des utilisateurs, clients, contrats et événements en base."""
    db = SessionLocal()
    try:
        # Récupérer les IDs des départements
        gestion_id = db.query(Departement).filter(
            Departement.nom == "gestion"
        ).first().id
        support_id = db.query(Departement).filter(
            Departement.nom == "support"
        ).first().id
        commercial_id = db.query(Departement).filter(
            Departement.nom == "commercial"
        ).first().id

        # Création des collaborateurs
        admin1 = Collaborateur(
            nom="Jean",
            prenom="Patrick",
            email="admin@example.com",
            departement_id=gestion_id,  # Assignation correcte du département
            login="admin",
            password_hash=Collaborateur.set_password("admin123")
        )
        admin2 = Collaborateur(
            nom="Robert",
            prenom="John",
            email="admin2@gmail.com",
            departement_id=gestion_id,
            login="admin2",
            password_hash=Collaborateur.set_password("admin123")
        )
        commercial1 = Collaborateur(
            nom="Dion",
            prenom="Celine",
            email="celine.dion@gmail.com",
            departement_id=commercial_id,
            login="celine",
            password_hash=Collaborateur.set_password("password123")
        )
        commercial2 = Collaborateur(
            nom="Jackson",
            prenom="Michael",
            email="michael.jackson@gmail.com",
            departement_id=commercial_id,
            login="michael",
            password_hash=Collaborateur.set_password("password123")
        )
        support1 = Collaborateur(
            nom="Crusoé",
            prenom="Robinson",
            email="robinson.crusoé@gmail.com",
            departement_id=support_id,
            login="robinson",
            password_hash=Collaborateur.set_password("support123")
        )
        support2 = Collaborateur(
            nom="Hemingway",
            prenom="Ernest",
            email="ernest.hemingway@gmail.com",
            departement_id=support_id,
            login="ernest",
            password_hash=Collaborateur.set_password("support123")
        )

        db.add_all([
            admin1, admin2, commercial1, support1, commercial2, support2
        ])
        db.commit()
        print("Collaborateurs ajoutés avec succès.")

        # Récupérer les IDs après insertion
        commercial_id = [commercial1.id, commercial2.id]
        support_id = [support1.id, support2.id]

        # Création des clients
        client1 = Client(
            nom_complet="Kevin Casey",
            email="kevin@startup.io",
            telephone="0685457415",
            nom_entreprise="Cool Startup LLC",
            id_commercial=commercial_id[0]
        )
        client2 = Client(
            nom_complet="Alice Cooper",
            email="alice@enterprise.com",
            telephone="0742159654",
            nom_entreprise="Enterprise Solutions",
            id_commercial=commercial_id[1]
        )
        client3 = Client(
            nom_complet="John Doe",
            email="john@gmail.com",
            telephone="0698321478",
            nom_entreprise="Doe & Partners",
            id_commercial=commercial_id[0]
        )

        db.add_all([client1, client2, client3])
        db.commit()
        print("Clients ajoutés avec succès.")

        # Récupérer les IDs après insertion
        client1_id = client1.id
        client2_id = client2.id
        client3_id = client3.id

        # Création des contrats
        contrat1 = Contrat(
            id_client=client1_id,
            montant_total=10000.00,
            montant_restant=5000.00,
            statut=False
        )
        contrat2 = Contrat(
            id_client=client2_id,
            montant_total=20000.00,
            montant_restant=15000.00,
            statut=True
        )
        contrat3 = Contrat(
            id_client=client3_id,
            montant_total=15000.00,
            montant_restant=10000.00,
            statut=False
        )

        db.add_all([contrat1, contrat2, contrat3])
        db.commit()
        print("Contrats ajoutés avec succès.")

        # Récupérer les IDs après insertion
        contrat1_id = contrat1.id
        contrat2_id = contrat2.id
        contrat3_id = contrat3.id

        # Création des événements
        evenement1 = Evenement(
            id_contrat=contrat1_id,
            id_support=support_id[0],
            date_debut=datetime(2023, 6, 4, 13, 0),
            date_fin=datetime(2023, 6, 5, 2, 0),
            lieu="53 Rue du Château, 41120 Candé-sur-Beuvron, France",
            nombre_participants=75,
            notes=(
                "Le mariage commence à 15h, au bord de la rivière. "
                "La restauration est organisée."
            )
        )
        evenement2 = Evenement(
            id_contrat=contrat2_id,
            id_support=support_id[1],
            date_debut=datetime(2023, 7, 1, 14, 0),
            date_fin=datetime(2023, 7, 2, 22, 0),
            lieu="123 Main Street, Cityville, USA",
            nombre_participants=120,
            notes=(
                "Réunion annuelle d'entreprise avec conférenciers invités "
                "et cérémonie de remise de prix."
            )
        )
        evenement3 = Evenement(
            id_contrat=contrat3_id,
            id_support=support_id[1],
            date_debut=datetime(2023, 8, 15, 10, 0),
            date_fin=datetime(2023, 8, 16, 18, 0),
            lieu="Plaza Mayor, 28012 Madrid, Spain",
            nombre_participants=50,
            notes=(
                "Événement de lancement de produit avec couverture presse "
                "et musique live."
            )
        )

        db.add_all([evenement1, evenement2, evenement3])
        db.commit()
        print("Événements ajoutés avec succès.")

    except Exception as e:
        db.rollback()
        print(f"Erreur lors de l'insertion des données : {e}")

    finally:
        db.close()


if __name__ == "__main__":
    seed_departements()
    seed_data()
