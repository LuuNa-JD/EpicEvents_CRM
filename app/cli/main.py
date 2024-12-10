import click
from rich.console import Console
from app.cli.auth import auth_group
from app.cli.clients import clients_group
from app.cli.contrats import contrats_group
from app.cli.evenements import evenements_group
from app.cli.collaborateurs import collaborateurs_group

console = Console()


# Groupe principal CLI
class CustomCLI(click.Group):
    def get_command(self, ctx, cmd_name):
        """
        Personnalise le message d'erreur pour une commande inexistante.
        """
        command = super().get_command(ctx, cmd_name)
        if command is None:
            # Afficher uniquement ton message d'erreur
            console.print(f"[bold red]Erreur : La commande '{cmd_name}' n'existe pas.[/bold red]")
            console.print("[yellow]Utilisez '--help' pour afficher les commandes disponibles.[/yellow]\n")
            ctx.exit(1)  # Quitter proprement sans laisser Click afficher autre chose
        return command


@click.group(cls=CustomCLI)
def cli():
    """CLI principal d'EpicEvents."""


# Exemple de sous-commandes
@cli.command()
def example():
    """Une commande d'exemple."""
    console.print("[green]Ceci est une commande d'exemple.[/green]")
# Regroupement des commandes par catégorie


cli.add_command(auth_group)
cli.add_command(clients_group)
cli.add_command(contrats_group)
cli.add_command(evenements_group)
cli.add_command(collaborateurs_group)

if __name__ == "__main__":
    cli()
