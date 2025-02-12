import click
from rich.console import Console
from app.services.collaborateur_service import (
    create_new_collaborateur,
    update_existing_collaborateur,
    delete_collaborateur_service
)
from app.db.session import SessionLocal

console = Console()


@click.group(
    name="collaborateurs",
    help="Commandes pour gérer les collaborateurs (équipe gestion)."
)
def collaborateurs_group():
    pass


@collaborateurs_group.command(name="create")
@click.option("--nom", prompt="Nom", help="Nom du collaborateur")
@click.option("--prenom", prompt="Prénom", help="Prénom du collaborateur")
@click.option("--email", prompt="Email", help="Email du collaborateur")
@click.option(
    "--departement", prompt="Département", help="Département du collaborateur"
)
@click.option("--login", prompt="Login", help="Login du collaborateur")
@click.option(
    "--password", prompt="Mot de passe", hide_input=True, help="Mot de passe"
)
@click.option("--token", prompt="Token JWT", help="Token JWT de l'utilisateur")
def create_collaborateur(
    nom, prenom, email, departement, login, password, token
):
    """Créer un nouveau collaborateur."""
    with SessionLocal() as db:
        try:
            create_new_collaborateur(
                db, token, nom, prenom, email, departement, login, password
            )
            console.print(
                f"[bold green]Collaborateur {nom} "
                "créé avec succès ![/bold green]"
            )
        except Exception as e:
            console.print(f"[bold red]Erreur : {e}[/bold red]")


@collaborateurs_group.command(name="update")
@click.option(
    "--id", prompt="ID Collaborateur", type=int,
    help="ID du collaborateur à modifier"
)
@click.option("--nom", help="Nouveau nom")
@click.option("--prenom", help="Nouveau prénom")
@click.option("--email", help="Nouvel email")
@click.option("--departement", help="Nouveau département")
@click.option("--login", help="Nouveau login")
@click.option("--password", help="Nouveau mot de passe", hide_input=True)
@click.option("--token", prompt="Token JWT", help="Token JWT de l'utilisateur")
def update_collaborateur(
    id, nom, prenom, email, departement, login, password, token
):
    """Mettre à jour un collaborateur."""
    updates = {
        k: v
        for k, v in locals().items()
        if k not in ["id", "token"] and v
    }

    with SessionLocal() as db:
        try:
            update_existing_collaborateur(db, token, id, **updates)
            console.print(
                f"[bold green]Collaborateur ID {id} "
                "mis à jour avec succès ![/bold green]"
            )
        except Exception as e:
            console.print(f"[bold red]Erreur : {e}[/bold red]")


@collaborateurs_group.command(name="delete")
@click.option(
    "--id", prompt="ID Collaborateur", type=int,
    help="ID du collaborateur à supprimer"
)
@click.option("--token", prompt="Token JWT", help="Token JWT de l'utilisateur")
def delete_collaborateur(id, token):
    """Supprimer un collaborateur."""
    with SessionLocal() as db:
        try:
            delete_collaborateur_service(db, token, id)
            console.print(
                f"[bold green]Collaborateur ID {id} "
                "supprimé avec succès ![/bold green]"
            )
        except Exception as e:
            console.print(f"[bold red]Erreur : {e}[/bold red]")
