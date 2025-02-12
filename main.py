import sys
import click
from rich.console import Console
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from app.cli.main import cli
from app.db.session import SessionLocal
from app.db.base import Base
from sqlalchemy.exc import SQLAlchemyError
from rich.markup import escape
from app.utils.file_utils import load_token
from app.auth.jwt_utils import decode_token
from app.utils.config import get_role_commands, get_command_description

console = Console()
ROLE_COMMANDS = get_role_commands()

prompt_style = Style.from_dict({
    'prompt': '#00CFFF bold',
})


def get_user_role():
    """Récupère le rôle de l'utilisateur connecté à partir du token."""
    token = load_token()
    if not token:
        return None  # Aucune connexion

    payload = decode_token(token)
    if not payload:
        return None  # Token invalide ou expiré
    return payload.get("role")


def init_database():
    """
    Initialise la base de données avec les tables nécessaires.
    """
    console.print("[cyan]Initialisation de la base de données...[/cyan]")
    from app.db.models import collaborateur, client, contrat, evenement # noqa

    try:
        with SessionLocal() as db:
            Base.metadata.create_all(bind=db.get_bind())
        console.print(
            "[bold green]Base de données initialisée avec succès !"
            "[/bold green]"
        )
    except SQLAlchemyError as e:
        console.print(
            f"[bold red]Erreur lors de l'initialisation : {e}[/bold red]"
        )
        sys.exit(1)


def display_welcome_message():
    """
    Affiche un message d'accueil élégant et la liste des commandes autorisées.
    """
    role = get_user_role()
    allowed_commands = ROLE_COMMANDS.get(role, [])

    console.print(
        """
[bold cyan]
######################################
#   Bienvenue sur EpicEvents CRM CLI  #
######################################
[/bold cyan]
"""
    )

    if role:
        console.print(f"[bold cyan]🎭 Rôle détecté : {role}[/bold cyan]\n")

        if allowed_commands:
            console.print("[bold green]Commandes disponibles :[/bold green]\n")
            table = "\n".join([f"  🔹 [yellow]{cmd}[/yellow] - {get_command_description(cmd)}" for cmd in allowed_commands])
            console.print(table)
        else:
            console.print("[bold red]Aucune commande disponible pour votre rôle.[/bold red]\n")
    else:
        console.print("[bold red]Vous devez être connecté pour voir les commandes disponibles.[/bold red]\n")


@cli.command(name="help", help="Affiche la liste des commandes disponibles avec leur description.")
def custom_help():
    """
    Affiche la liste détaillée des commandes en fonction du rôle de l'utilisateur.
    """
    role = get_user_role()
    if not role:
        console.print("[bold red]Vous devez être connecté pour voir les commandes disponibles.[/bold red]")
        return

    allowed_commands = ROLE_COMMANDS.get(role, [])
    if allowed_commands:
        console.print(f"[bold cyan]🎭 Rôle détecté : {role}[/bold cyan]\n")
        console.print("[bold green]Commandes disponibles :[/bold green]\n")
        table = "\n".join([f"  🔹[yellow]{cmd}[/yellow] - {get_command_description(cmd)}" for cmd in allowed_commands])
        console.print(table)
    else:
        console.print("[bold red]Aucune commande disponible pour votre rôle.[/bold red]\n")


def interactive_menu():
    """
    Lance un menu interactif avec un prompt en boucle.
    """
    display_welcome_message()

    session = PromptSession()
    while True:
        try:
            command = session.prompt(
                [('class:prompt', 'epic_events> ')],
                style=prompt_style
            ).strip()

            if command.lower() in ["exit", "quit"]:
                console.print("[bold green]👋 À bientôt ![/bold green]")
                break  # Sort de la boucle

            elif command:
                cli.main(standalone_mode=False, args=command.split())
        except KeyboardInterrupt:
            console.print("\n[bold yellow]⚠️ Interrompu par l'utilisateur. À bientôt ![/bold yellow]")
            break
        except click.exceptions.ClickException as e:
            console.print(f"[bold red]{e}[/bold red]")
        except Exception as e:
            console.print(f"[bold red]Erreur inattendue : {escape(str(e))}[/bold red]")


def main():
    """
    Point d'entrée principal.
    """
    if "--init-db" in sys.argv:
        init_database()
        sys.exit(0)

    if len(sys.argv) > 1:
        cli()
    else:
        interactive_menu()


if __name__ == "__main__":
    main()
