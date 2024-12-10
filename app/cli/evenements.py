import click
from rich.console import Console
from rich.table import Table
from app.services.evenement_service import (
    list_all_evenements,
    create_event_for_client,
    update_event_by_support,
    list_events_for_support
)
from app.db.session import SessionLocal

console = Console()


@click.group(name="evenements", help="Commandes pour gérer les événements.")
def evenements_group():
    pass


@evenements_group.command(name="list")
@click.option("--token", prompt="Token JWT", help="Token JWT de l'utilisateur")
def list_evenements(token):
    """Afficher tous les événements."""
    with SessionLocal() as db:
        evenements = list_all_evenements(db, token)
        table = Table(title="Liste des Événements")
        table.add_column("ID", justify="center")
        table.add_column("Contrat ID", justify="center")
        table.add_column("Date Début", justify="center")
        table.add_column("Date Fin", justify="center")
        table.add_column("Lieu", justify="left")
        table.add_column("Participants", justify="center")

        for event in evenements:
            table.add_row(
                str(event.id),
                str(event.id_contrat),
                str(event.date_debut),
                str(event.date_fin),
                event.lieu,
                str(event.nombre_participants)
            )
        console.print(table)


@evenements_group.command(name="create")
@click.option("--id-contrat", prompt="ID Contrat", type=int, help="ID du contrat associé")
@click.option("--id-support", prompt="ID Support", type=int, help="ID du support associé")
@click.option("--date-debut", prompt="Date de début (YYYY-MM-DD)", help="Date de début")
@click.option("--date-fin", prompt="Date de fin (YYYY-MM-DD)", help="Date de fin")
@click.option("--lieu", prompt="Lieu", help="Lieu de l'événement")
@click.option("--participants", prompt="Nombre de participants", type=int, help="Nombre de participants")
@click.option("--notes", prompt="Notes", help="Notes supplémentaires")
@click.option("--token", prompt="Token JWT", help="Token JWT de l'utilisateur")
def create_event(id_contrat, id_support, date_debut, date_fin, lieu, participants, notes, token):
    """Créer un nouvel événement."""
    with SessionLocal() as db:
        try:
            create_event_for_client(db, token, id_contrat, id_support, date_debut, date_fin, lieu, participants, notes)
            console.print("[bold green]Événement créé avec succès ![/bold green]")
        except Exception as e:
            console.print(f"[bold red]Erreur : {e}[/bold red]")


@evenements_group.command(name="update")
@click.option("--id", prompt="ID Événement", type=int, help="ID de l'événement à modifier")
@click.option("--lieu", help="Nouveau lieu")
@click.option("--participants", type=int, help="Nouveau nombre de participants")
@click.option("--token", prompt="Token JWT", help="Token JWT de l'utilisateur")
def update_event(id, lieu, participants, token):
    """Mettre à jour un événement."""
    updates = {"lieu": lieu, "nombre_participants": participants}
    updates = {k: v for k, v in updates.items() if v is not None}

    with SessionLocal() as db:
        try:
            update_event_by_support(db, token, id, **updates)
            console.print(f"[bold green]Événement ID {id} mis à jour avec succès ![/bold green]")
        except Exception as e:
            console.print(f"[bold red]Erreur : {e}[/bold red]")
