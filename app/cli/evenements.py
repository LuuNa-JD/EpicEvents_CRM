import click
from rich.console import Console
from rich.table import Table
from app.services.evenement_service import (
    list_all_evenements,
    create_event_for_client,
    assign_support,
    list_events_for_support,
    get_unassigned_evenements,
)
from app.services.contrat_service import get_signed_contrats_for_commercial
from app.crud.collaborateurs import get_support
from app.crud.evenements import (
    get_evenements_by_support,
    get_evenement_for_support,
    get_evenement
)
from app.services.collaborateur_service import list_supports
from app.db.session import SessionLocal
from app.utils.config import CustomGroup
from app.auth.permissions import role_required
from app.utils.file_utils import load_token
from app.auth.jwt_utils import decode_token
from datetime import datetime


console = Console()


@click.group(
    name="evenements",
    no_args_is_help=False,
    invoke_without_command=True,
    cls=CustomGroup
)
@click.pass_context
def evenements_group(ctx):
    """Commandes pour gérer les évenements."""
    if ctx.invoked_subcommand is None:
        console.print("[bold yellow]❗ Utilisez 'help' pour voir les commandes disponibles.[/bold yellow]")
        ctx.exit(1)


@evenements_group.command(name="create")
@role_required(["commercial"])
def create_evenement():
    """
    Créer un nouvel événement (Commercial uniquement).
    """
    token = load_token()
    if not token:
        console.print("[bold red]Erreur : Vous devez être connecté pour cette commande.[/bold red]")
        return

    payload = decode_token(token)
    if not payload:
        console.print("[bold red]Erreur : Token invalide ou expiré. Veuillez vous reconnecter.[/bold red]")
        return

    user_id = payload.get("user_id")  # ID du commercial connecté

    with SessionLocal() as db:
        # Récupérer les contrats signés du commercial
        contrats = get_signed_contrats_for_commercial(db, user_id)

        if not contrats:
            console.print("[bold red]Aucun contrat signé disponible pour vos clients.[/bold red]")
            return

        console.print("\n[bold cyan]Contrats signés disponibles :[/bold cyan]")
        for contrat in contrats:
            console.print(f"   🔹 ID {contrat.id} - Client : {contrat.client.nom_complet}")

        id_contrat = click.prompt("ID du contrat", type=int)

        # Demander la date de début
        date_debut = click.prompt("Date de début (JJ/MM/AAAA)", type=str)
        date_fin = click.prompt("Date de fin (JJ/MM/AAAA)", type=str)
        try:
            date_debut = datetime.strptime(date_debut, "%d/%m/%Y").date()
            date_fin = datetime.strptime(date_fin, "%d/%m/%Y").date()
            if date_fin < date_debut:
                console.print("[bold red]Erreur : La date de fin doit être après la date de début.[/bold red]")
                return
        except ValueError:
            console.print("[bold red]Erreur : Format de date invalide. Utilisez JJ/MM/AAAA.[/bold red]")
            return

        lieu = click.prompt("Lieu", type=str)
        nombre_participants = click.prompt("Nombre de participants", type=int)
        notes = click.prompt("Notes (optionnel)", type=str, default="", show_default=False)

        # Création de l'événement
        with SessionLocal() as db:
            try:
                evenement = create_event_for_client(
                    db, token, id_contrat, date_debut, date_fin, lieu,
                    nombre_participants, notes
                )
                console.print(f"[bold green]✨ Événement ID {evenement.id} créé avec succès ![/bold green]")
            except ValueError as e:
                console.print(f"[bold red]Erreur : {str(e)}[/bold red]")
            except Exception as e:
                console.print(f"[bold red]Erreur : {str(e)}[/bold red]")


@evenements_group.command(name="assign_support")
@role_required(["gestion"])
def assign_support_to_evenement():
    """
    Assigner un support à un événement existant (Gestion uniquement).
    """
    token = load_token()
    if not token:
        console.print("[bold red]Erreur : Vous devez être connecté pour cette commande.[/bold red]")
        return

    payload = decode_token(token)
    if not payload:
        console.print("[bold red]Erreur : Token invalide ou expiré. Veuillez vous reconnecter.[/bold red]")
        return

    with SessionLocal() as db:
        evenements = get_unassigned_evenements(db)

        if not evenements:
            console.print("[bold yellow]Tous les événements ont déjà un support attribué.[/bold yellow]")
            return

        console.print("\n[bold cyan]📌 Événements en attente de support :[/bold cyan]")
        for evt in evenements:
            console.print(f"   🔹 ID {evt.id} - Lieu : {evt.lieu} - Date : {evt.date_debut.strftime('%d/%m/%Y')}")

        id_evenement = click.prompt("ID de l'événement à attribuer", type=int)

        evenement = get_evenement(db, id_evenement)
        if not evenement:
            console.print("[bold red]Erreur : Aucun événement trouvé avec cet ID.[/bold red]")
            return
        if evenement.id_support:
            console.print("[bold red]Erreur : Cet événement a déjà un support attribué.[/bold red]")
            return

        # Lister les collaborateurs du département support
        supports = list_supports(db)
        if not supports:
            console.print("[bold red]Erreur : Aucun collaborateur support disponible.[/bold red]")
            return

        console.print("\n[bold cyan]📌 Liste des supports disponibles :[/bold cyan]")
        for sup in supports:
            console.print(f"   🔹 ID {sup.id} - Nom : {sup.nom} {sup.prenom}")

        id_support = click.prompt("ID du support à assigner", type=int)

        # Vérifier si le support existe
        support = get_support(db, id_support)
        if not support:
            console.print("[bold red]Erreur : Aucun support trouvé avec cet ID.[/bold red]")
            return

        # Assigner le support à l'événement
        try:
            evenement = assign_support(db, token, id_evenement, id_support)
            console.print(
                f"[bold green]✨ Support {support.nom} {support.prenom} "
                f"assigné à l'événement ID {evenement.id} ![/bold green]"
            )
        except ValueError as e:
            console.print(f"[bold red]Erreur : {str(e)}[/bold red]")
        except Exception as e:
            console.print(f"[bold red]Erreur inattendue : {str(e)}[/bold red]")


@evenements_group.command(name="list")
@role_required(["commercial", "support", "gestion"])
@click.option("-mine", is_flag=True)
@click.option("-unassigned", is_flag=True)
def list_evenements(mine, unassigned):
    """
    Lister les événements disponibles
    """
    token = load_token()
    if not token:
        console.print("[bold red]Erreur : Vous devez être connecté pour accéder à cette commande.[/bold red]")
        return

    payload = decode_token(token)
    if not payload:
        console.print("[bold red]Erreur : Token invalide ou expiré. Veuillez vous reconnecter.[/bold red]")
        return

    role = payload.get("role")

    if mine and role != "support":
        console.print("[bold red]Erreur : Seuls les supports peuvent utiliser l'option '--mine'.[/bold red]")
        return

    if unassigned and role != "gestion":
        console.print("[bold red]Erreur : Seuls les gestionnaires peuvent utiliser l'option '--unassigned'.[/bold red]")
        return

    console.print(f"[bold cyan]Rôle actuel : {role}[/bold cyan]")

    with SessionLocal() as db:
        try:
            if role == "gestion":
                evenements = get_unassigned_evenements(db) if unassigned else list_all_evenements(db, token)
            elif role == "commercial":
                evenements = list_all_evenements(db, token)
            elif role == "support":
                evenements = list_events_for_support(db, token) if mine else list_all_evenements(db, token)

            if not evenements:
                console.print("[bold magenta]Aucun événement trouvé avec ces critères.[/bold magenta]")
                return

            table = Table(title="[bold green]Liste des événements[/bold green]")
            table.add_column("ID", style="cyan")
            table.add_column("Client", style="magenta")
            table.add_column("Lieu", style="yellow")
            table.add_column("Date début", style="green")
            table.add_column("Date fin", style="green")
            table.add_column("Participants", style="green")
            table.add_column("Support", style="green")
            table.add_column("Notes", style="green")

            for evt in evenements:
                table.add_row(
                    str(evt.id),
                    evt.contrat.client.nom_complet,
                    evt.lieu,
                    evt.date_debut.strftime("%d/%m/%Y"),
                    evt.date_fin.strftime("%d/%m/%Y"),
                    str(evt.nombre_participants),
                    f"{evt.support.nom} {evt.support.prenom}"
                    if evt.support else "Non attribué",
                    evt.notes or "Aucune"
                )

            console.print(table)
        except Exception as e:
            console.print(f"[bold red]Erreur lors de la récupération des événements : {e}[/bold red]")


@evenements_group.command(name="update")
@role_required(["support"])
def update_evenement():
    """
    Permet aux supports de modifier uniquement les événements qui leur sont assignés.
    """
    token = load_token()
    if not token:
        console.print("[bold red]Erreur : Vous devez être connecté pour accéder à cette commande.[/bold red]")
        return

    payload = decode_token(token)
    if not payload:
        console.print("[bold red]Erreur : Token invalide ou expiré. Veuillez vous reconnecter.[/bold red]")
        return

    role = payload.get("role")
    user_id = payload.get("user_id")

    if role != "support":
        console.print("[bold red]Erreur : Seuls les supports peuvent mettre à jour leur propre événement.[/bold red]")
        return

    with SessionLocal() as db:
        try:
            # Afficher les événements assignés au support connecté
            evenements = get_evenements_by_support(db, user_id)
            if not evenements:
                console.print("[bold magenta]Aucun événement assigné à votre compte.[/bold magenta]")
                return

            console.print("\n[bold cyan]Événements que vous pouvez modifier :[/bold cyan]")
            for evt in evenements:
                console.print(f"   🔹 ID {evt.id} - {evt.lieu} - Date : {evt.date_debut.strftime('%d/%m/%Y')}")

            # Sélectionner l'événement à modifier
            id_evenement = click.prompt("\nID de l'événement à modifier", type=int)

            # Vérifier si l'événement appartient bien au support
            evenement = get_evenement_for_support(db, id_evenement, user_id)

            if not evenement:
                console.print("[bold red]Erreur : Cet événement ne vous est pas attribué ou n'existe pas.[/bold red]")
                return

            # Demander les modifications
            console.print("\n[bold cyan]📝 Modifications de l'événement[/bold cyan]")

            date_debut_str = click.prompt(
                "Nouvelle date de début (JJ/MM/AAAA) (laisser vide pour ne pas changer)",
                default="", show_default=False
            )
            date_fin_str = click.prompt(
                "Nouvelle date de fin (JJ/MM/AAAA) (laisser vide pour ne pas changer)",
                default="", show_default=False
            )
            lieu = click.prompt("Nouveau lieu (laisser vide pour ne pas changer)", default="", show_default=False)
            participants = click.prompt("Nombre de participants (laisser vide pour ne pas changer)", type=int, default=None)
            notes = click.prompt("Notes (laisser vide pour ne pas changer)", default="", show_default=False)

            # Convertir les dates
            date_debut = datetime.strptime(date_debut_str, "%d/%m/%Y") if date_debut_str else None
            date_fin = datetime.strptime(date_fin_str, "%d/%m/%Y") if date_fin_str else None

            # Vérification date début < date fin
            if date_debut and date_fin and date_debut > date_fin:
                console.print("[bold red]Erreur : La date de début ne peut pas être après la date de fin.[/bold red]")
                return

            # Créer le dictionnaire des mises à jour
            updates = {k: v for k, v in {
                "date_debut": date_debut,
                "date_fin": date_fin,
                "lieu": lieu,
                "nombre_participants": participants,
                "notes": notes
            }.items() if v}

            if not updates:
                console.print("[bold yellow]Aucune modification apportée.[/bold yellow]")
                return

            # Appliquer les modifications
            for key, value in updates.items():
                setattr(evenement, key, value)

            db.commit()

            console.print(f"\n[bold green]Événement ID {evenement.id} mis à jour avec succès ![/bold green]")
            console.print(f"   🔹 Lieu : {evenement.lieu}")
            console.print(f"   🔹 Date : {evenement.date_debut.strftime('%d/%m/%Y')} - {evenement.date_fin.strftime('%d/%m/%Y')}")
            console.print(f"   🔹 Participants : {evenement.nombre_participants}")
            console.print(f"   🔹 Notes : {evenement.notes or 'Aucune'}")

        except ValueError as e:
            console.print(f"[bold red]Erreur : {e}[/bold red]")
        except Exception as e:
            console.print(f"[bold red]Erreur inattendue : {e}[/bold red]")
