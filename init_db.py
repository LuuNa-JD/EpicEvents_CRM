from app.db.base import Base
from app.db.session import engine
from app.db.models import collaborateur, client, contrat, evenement # noqa


def init_db():
    """Crée les tables dans la base de données."""
    print("Création des tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables créées avec succès.")


if __name__ == "__main__":
    init_db()
