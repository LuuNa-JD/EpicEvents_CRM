from app.auth.login import login
from app.db.session import SessionLocal
from app.auth.jwt_utils import decode_token
from app.utils.file_utils import load_token, delete_token
import click
from rich.console import Console

console = Console()


@click.group(name="auth", help="Commandes pour l'authentification.")
def auth_group():
    """Groupe des commandes pour gérer l'authentification."""
    pass


@auth_group.command(name="login")
@click.option(
    "--username", prompt="Votre login", help="Login de l'utilisateur"
)
@click.option(
    "--password",
    prompt="Votre mot de passe",
    hide_input=True,
    help="Mot de passe de l'utilisateur"
)
def user_login(username, password):
    """
    Commande pour se connecter en utilisant la fonction login existante.
    """
    with SessionLocal() as db:
        token = login(db, username, password)  # Appelle la fonction login
        if token:
            console.print("[bold green]Connexion réussie ![/bold green]")
            console.print("[yellow]Votre token JWT a été sauvegardé.[/yellow]")
        else:
            console.print(
                "[bold red]Échec de la connexion. Identifiants "
                "invalides.[/bold red]"
            )


@auth_group.command(name="status")
def user_status():
    """
    Vérifie si l'utilisateur est connecté et affiche son rôle.
    """
    token = load_token()  # Charge le token sauvegardé localement
    if not token:
        console.print("[bold red]Vous n'êtes pas connecté.[/bold red]")
        return

    payload = decode_token(token)  # Décodage du token
    if payload:
        user_id = payload.get("user_id")
        role = payload.get("role")
        nom = payload.get("nom")
        prenom = payload.get("prenom")
        console.print("[bold green]Vous êtes connecté.[/bold green]")
        console.print(f"ID Utilisateur : [cyan]{user_id}[/cyan]")
        console.print(f"Nom : [yellow]{nom}[/yellow]")
        console.print(f"Prénom : [yellow]{prenom}[/yellow]")

        console.print(f"Rôle : [yellow]{role}[/yellow]")
    else:
        console.print("[bold red]Token invalide ou expiré.[/bold red]")


@auth_group.command(
    name="logout",
    help="Déconnecter l'utilisateur en supprimant le token JWT."
)
def logout():
    """
    Déconnecte l'utilisateur en supprimant le token stocké localement.
    """
    console.print("[bold cyan]Tentative de déconnexion...[/bold cyan]")

    if delete_token():
        console.print("[bold green]Déconnexion réussie. Votre token a été "
                      "supprimé.[/bold green]")
    else:
        console.print("[bold yellow]Aucun token trouvé. Vous êtes déjà "
                      "déconnecté.[/bold yellow]")
