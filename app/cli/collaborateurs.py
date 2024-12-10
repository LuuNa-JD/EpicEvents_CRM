import click
from rich.console import Console
from app.services.collaborateur_service import create_new_collaborateur
from app.db.session import SessionLocal

console = Console()

@click.group(name="collaborateurs", help="Commandes pour gérer les collaborateurs (équipe gestion).")
def collaborateurs_group():
    pass

@collaborateurs_group.command(name="create")
@click.option("--nom", prompt="Nom", help="Nom du collaborateur")
@click.option("--prenom", prompt="Prénom", help="Prénom du collaborateur")
@click.option("--email", prompt="Email", help="Email du collaborateur")
@click.option("--departement", prompt="Département", help="Département du collaborateur")
@click.option("--login", prompt="Login", help="Login du collaborateur")
@click.option("--password", prompt="Mot de passe", hide_input=True, help="Mot de passe")
@click.option("--token", prompt="Token JWT", help="Token JWT de l'utilisateur")
def create_collaborateur(nom, prenom, email, departement, login, password, token):
    """Créer un nouveau collaborateur."""
    with SessionLocal() as db:
        try:
            create_new_collaborateur(db, token, nom, prenom, email, departement, login, password)
            console.print(f"[bold green]Collaborateur {nom} créé avec succès ![/bold green]")
        except Exception as e:
            console.print(f"[bold red]Erreur : {e}[/bold red]")
