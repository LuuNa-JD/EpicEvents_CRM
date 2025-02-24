import os
import json
from dotenv import load_dotenv
from rich.console import Console
import click

console = Console()

load_dotenv()


def get_role_commands():
    """
    Charge ROLE_COMMANDS depuis .env et le convertit en dictionnaire Python.
    """
    role_commands_json = os.getenv("ROLE_COMMANDS")
    if role_commands_json:
        return json.loads(role_commands_json)
    return {}


class CustomGroup(click.Group):
    """Gère les erreurs pour les sous-commandes."""
    def get_command(self, ctx, cmd_name):
        """Intercepter les erreurs sur les sous-commandes."""
        command = super().get_command(ctx, cmd_name)
        if command is None:
            console.print(
                f"[bold red]Erreur : La sous-commande '{cmd_name}' "
                f"n'existe pas.[/bold red]"
            )
            ctx.exit(1)
        return command
