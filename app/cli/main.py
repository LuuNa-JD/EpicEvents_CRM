import click
from rich.console import Console
from app.cli.auth import auth_group
from app.cli.clients import clients_group
from app.cli.contrats import contrats_group
from app.cli.evenements import evenements_group
from app.cli.collaborateurs import collaborateurs_group
from app.auth.jwt_utils import decode_token
from app.utils.file_utils import load_token
from app.utils.config import get_role_commands
import os


console = Console()
ROLE_COMMANDS = get_role_commands()


def get_user_role():
    """Récupère le rôle de l'utilisateur connecté à partir du token."""
    token = load_token()
    if not token:
        return None  # Aucune connexion

    payload = decode_token(token)
    if not payload:
        return None  # Token invalide ou expiré
    return payload.get("role")


class CustomCLI(click.Group):
    def get_command(self, ctx, cmd_name):
        """
        Filtrer les commandes disponibles en fonction du rôle.
        """
        role = get_user_role()
        command = super().get_command(ctx, cmd_name)

        if command is None:
            console.print(
                f"[bold red]Erreur : La commande '{cmd_name}' "
                f"n'existe pas.[/bold red]"
            )
            ctx.exit(1)

        if role:
            allowed_cmds = ROLE_COMMANDS.get(role, [])

            if (cmd_name not in allowed_cmds and
                    not any(cmd_name.startswith(ac) for ac in allowed_cmds)):
                console.print(
                    f"[bold red]Accès refusé : La commande '{cmd_name}' "
                    "n'est pas disponible pour votre rôle.[/bold red]"
                )
                ctx.exit(1)

        return command


@click.command(name="clear", help="Nettoie l'affichage du terminal.")
def clear_console():
    """Efface l'affichage du terminal."""
    os.system("clear" if os.name == "posix" else "cls")


@click.group(cls=CustomCLI)
def cli():
    """CLI principal d'EpicEvents."""


cli.add_command(auth_group)
cli.add_command(clients_group)
cli.add_command(contrats_group)
cli.add_command(evenements_group)
cli.add_command(collaborateurs_group)
cli.add_command(clear_console)


@cli.command()
def example():
    """Une commande d'exemple."""
    console.print("[green]Ceci est une commande d'exemple.[/green]")


if __name__ == "__main__":
    cli()
