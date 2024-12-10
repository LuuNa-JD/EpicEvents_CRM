import click
from rich.console import Console
from rich.table import Table
from app.services.contrat_service import (
    list_all_contrats,
    create_contrat_for_client,
    update_client_contract,
    filter_contracts_by_status
)
from app.db.session import SessionLocal

console = Console()


@click.group(name="contrats", help="Commandes pour gérer les contrats.")
def contrats_group():
    pass


@contrats_group.command(name="list")
@click.option("--token", prompt="Token JWT", help="Token JWT de l'utilisateur")
def list_contrats(token):
    """Afficher tous les contrats."""
    with SessionLocal() as db:
        contrats = list_all_contrats(db, token)
        table = Table(title="Liste des Contrats")
        table.add_column("ID", justify="center")
        table.add_column("Client", justify="left")
        table.add_column("Montant Total", justify="right")
        table.add_column("Montant Restant", justify="right")
        table.add_column("Statut", justify="center")

        for contrat in contrats:
            statut = "Signé" if contrat.statut else "Non signé"
            table.add_row(
                str(contrat.id),
                contrat.client.nom_complet,
                f"{contrat.montant_total:.2f}€",
                f"{contrat.montant_restant:.2f}€",
                statut
            )
        console.print(table)


@contrats_group.command(name="create")
@click.option("--id-client", prompt="ID Client", help="ID du client associé")
@click.option("--montant-total", prompt="Montant Total", type=float, help="Montant total du contrat")
@click.option("--montant-restant", prompt="Montant Restant", type=float, help="Montant restant à payer")
@click.option("--statut", prompt="Statut (True/False)", type=bool, help="Statut du contrat (signé ou non)")
@click.option("--token", prompt="Token JWT", help="Token JWT de l'utilisateur")
def create_contrat(id_client, montant_total, montant_restant, statut, token):
    """Créer un nouveau contrat."""
    with SessionLocal() as db:
        try:
            create_contrat_for_client(db, token, id_client, montant_total, montant_restant, statut)
            console.print("[bold green]Contrat créé avec succès ![/bold green]")
        except Exception as e:
            console.print(f"[bold red]Erreur : {e}[/bold red]")

@contrats_group.command(name="update")
@click.option("--id", prompt="ID Contrat", type=int, help="ID du contrat à modifier")
@click.option("--montant-total", type=float, help="Nouveau montant total")
@click.option("--montant-restant", type=float, help="Nouveau montant restant")
@click.option("--statut", type=bool, help="Nouveau statut (True/False)")
@click.option("--token", prompt="Token JWT", help="Token JWT de l'utilisateur")
def update_contrat(id, montant_total, montant_restant, statut, token):
    """Mettre à jour un contrat."""
    updates = {
        "montant_total": montant_total,
        "montant_restant": montant_restant,
        "statut": statut
    }
    updates = {k: v for k, v in updates.items() if v is not None}

    with SessionLocal() as db:
        try:
            update_client_contract(db, token, id, **updates)
            console.print(f"[bold green]Contrat ID {id} mis à jour avec succès ![/bold green]")
        except Exception as e:
            console.print(f"[bold red]Erreur : {e}[/bold red]")


@contrats_group.command(name="filter")
@click.option("--statut", type=bool, help="Statut du contrat (True: signé, False: non signé)")
@click.option("--token", prompt="Token JWT", help="Token JWT de l'utilisateur")
def filter_contrats(statut, token):
    """Filtrer les contrats par statut."""
    with SessionLocal() as db:
        contrats = filter_contracts_by_status(db, token, statut)
        statut_str = "Signés" if statut else "Non signés"
        console.print(f"[bold cyan]Contrats {statut_str} :[/bold cyan]")
        for contrat in contrats:
            console.print(f"- ID {contrat.id} | Client : {contrat.client.nom_complet} | Montant Restant : {contrat.montant_restant}€")
