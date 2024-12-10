import sys
import click
from rich.console import Console
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from app.cli.main import cli
from app.db.session import SessionLocal
from app.db.base import Base
from sqlalchemy.exc import SQLAlchemyError

console = Console()
# Style pour le prompt interactif
prompt_style = Style.from_dict({
    'prompt': '#00CFFF bold',
})


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
    Affiche un message d'accueil élégant.
    """
    console.print(
        """
[bold cyan]
######################################
#   Bienvenue sur EpicEvents CRM CLI  #
######################################
[/bold cyan]
"""
    )
    console.print(
        "Tapez [green]--help[/green] pour voir les commandes disponibles.\n"
    )
    console.print(
        "Pour quitter en mode interactif, tapez [yellow]'exit'[/yellow] ou "
        "[yellow]'quit'[/yellow].\n"
    )


def interactive_menu():
    """
    Lance un menu interactif avec un prompt en boucle.
    """
    display_welcome_message()

    session = PromptSession()
    while True:
        try:
            # Prompt interactif stylisé
            command = session.prompt(
                [('class:prompt', 'epic_events> ')],
                style=prompt_style
            ).strip()

            if command.lower() in ["exit", "quit"]:
                console.print("[bold green]À bientôt ! 👋[/bold green]")
                break  # Sort de la boucle

            elif command:
                # Exécute la commande avec Click
                cli.main(standalone_mode=False, args=command.split())
        except KeyboardInterrupt:
            console.print(
                "\n[bold yellow]Interrompu par l'utilisateur. "
                "À bientôt ![/bold yellow]"
            )
            break
        except click.exceptions.ClickException as e:
            console.print(f"[bold red]{e}[/bold red]")
        except Exception as e:
            console.print(f"[bold red]Erreur inattendue : {e}[/bold red]")


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
