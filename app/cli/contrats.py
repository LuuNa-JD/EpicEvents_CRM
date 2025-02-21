import click
import sentry_sdk
from rich.console import Console
from app.services.contrat_service import (
    list_all_contrats,
    create_new_contrat,
    update_client_contrat,
    update_contrat_commercial_service,
    list_contrats_by_commercial,

)
from app.db.session import SessionLocal
from app.utils.config import CustomGroup
from app.auth.permissions import role_required
from app.utils.file_utils import load_token
from app.auth.jwt_utils import decode_token
from rich.table import Table

console = Console()


@click.group(
    name="contrats",
    no_args_is_help=False,
    invoke_without_command=True,
    cls=CustomGroup
)
@click.pass_context
def contrats_group(ctx):
    """Commandes pour gérer les contrats."""
    if ctx.invoked_subcommand is None:
        console.print("[bold yellow]❗ Utilisez 'help' pour voir les commandes disponibles.[/bold yellow]")
        ctx.exit(1)


@contrats_group.command(name="create")
@role_required(["gestion"])
def create_contrat_cli():
    """
    Créer un nouveau contrat (Gestion uniquement).
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
        try:
            # Récupération du client
            id_client = click.prompt("ID du client", type=int)
            montant_total = click.prompt("Montant total du contrat", type=float)

            # Création du contrat
            contrat = create_new_contrat(db, token, id_client, montant_total)

            console.print(
                f"[bold green]Contrat ID {contrat.id} créé avec succès pour le client {contrat.client.nom_complet} ![/bold green]"
            )

        except ValueError as e:
            console.print(f"[bold red]Erreur : {e}[/bold red]")
        except Exception as e:
            console.print(f"[bold red]Erreur inattendue : {e}[/bold red]")


@contrats_group.command(name="list")
@role_required(["gestion", "support", "commercial"])
@click.option("-unsigned", "-u", is_flag=True)
@click.option("-unpaid", "-p", is_flag=True)
@click.option("-all", "-a", is_flag=True)
def list_contrats(unsigned, unpaid, all):
    """Afficher tous les contrats, avec des options de filtrage pour les commerciaux."""
    token = load_token()
    if not token:
        console.print("[bold red]Erreur : Vous devez être connecté pour accéder à cette commande.[/bold red]")
        return

    payload = decode_token(token)
    if not payload:
        console.print("[bold red]Erreur : Token invalide ou expiré. Veuillez vous reconnecter.[/bold red]")
        return

    user_id = payload.get("user_id")
    role = payload.get("role")

    console.print(
        f"[bold cyan]🔹 Token valide - Utilisateur ID {user_id} - "
        f"Rôle : {role}[/bold cyan]"
    )

    with SessionLocal() as db:
        if role in ["gestion", "support"]:
            contrats = list_all_contrats(db)

        elif role == "commercial":
            if all:
                contrats = list_all_contrats(db)
            else:
                contrats = list_contrats_by_commercial(db, user_id)

            if unsigned:
                contrats = [c for c in contrats if not c.statut]
            if unpaid:
                contrats = [c for c in contrats if c.montant_restant > 0]

        if not contrats:
            console.print("[bold yellow]Aucun contrat trouvé avec ces critères.[/bold yellow]")
            return

        table = Table(title="Liste des contrats")

        table.add_column("ID", justify="right", style="cyan", no_wrap=True)
        table.add_column("Client", style="magenta")
        table.add_column("Commercial", style="green")
        table.add_column("Montant Total (€)", justify="right", style="yellow")
        table.add_column("Montant Restant (€)", justify="right", style="red")
        table.add_column("Statut", style="blue")

        # Trier les contrats par nom de client
        contrats = sorted(contrats, key=lambda c: c.client.nom_complet)

        for contrat in contrats:
            table.add_row(
                str(contrat.id),
                contrat.client.nom_complet,
                contrat.client.commercial.nom,
                f"{contrat.montant_total:.2f}",
                f"{contrat.montant_restant:.2f}",
                "Signé" if contrat.statut else "Non signé"
            )

        console.print(table)


@contrats_group.command(name="update")
@role_required(["gestion"])
def update_contrat_cli():
    """
    Mettre à jour le contrat d'un client (Gestion uniquement).
    """
    token = load_token()
    if not token:
        console.print("[bold red]Erreur : Vous devez être connecté pour cette commande.[/bold red]")
        return

    payload = decode_token(token)
    if not payload:
        console.print("[bold red]Erreur : Token invalide ou expiré. Veuillez vous reconnecter.[/bold red]")
        return

    id_contrat = click.prompt("ID du contrat", type=int)

    montant_restant = click.prompt(
        "Montant restant (€) (laisser vide pour ne pas changer)",
        default="",
        show_default=False
    )
    statut = click.confirm("Le contrat est-il signé ?", default=None)
    montant_restant_final = float(montant_restant) if montant_restant.strip() else None

    updates = {k: v for k, v in {
        "montant_restant": montant_restant_final,
        "statut": statut
    }.items() if v is not None}

    if not updates:
        console.print("[bold yellow]Aucune modification apportée.[/bold yellow]")
        return

    with SessionLocal() as db:
        try:
            contrat = update_client_contrat(db, token, id_contrat, **updates)

            if updates.get("statut"):
                sentry_sdk.capture_message(
                    f"Contrat ID {contrat.id} signé (Gestion) - "
                    f"Client : {contrat.client.nom_complet}",
                    level="info"
                )

            console.print(
                f"[bold green]Contrat ID {contrat.id} mis à jour avec succès ![/bold green]\n"
                f"   🔹 Client : {contrat.client.nom_complet}\n"
                f"   🔹 Montant Total : {contrat.montant_total}€\n"
                f"   🔹 Montant Restant : {contrat.montant_restant}€\n"
                f"   🔹 Statut : {'Signé' if contrat.statut else 'Non signé'}"
            )
        except ValueError as e:
            console.print(f"[bold red]Erreur : {e}[/bold red]")
        except Exception as e:
            sentry_sdk.capture_exception(e)
            console.print(f"[bold red]Erreur inattendue : {e}[/bold red]")


@contrats_group.command(name="update-mine")
@role_required(["commercial"])
def update_contrat_commercial():
    """
    Modifier un contrat dont le commercial est responsable.
    """
    token = load_token()
    if not token:
        console.print("[bold red]Erreur : Vous devez être connecté pour cette commande.[/bold red]")
        return

    payload = decode_token(token)
    if not payload:
        console.print("[bold red]Erreur : Token invalide ou expiré. Veuillez vous reconnecter.[/bold red]")
        return

    user_id = payload.get("user_id")

    console.print("\n[bold cyan]Modification d'un contrat (Commercial)[/bold cyan]")
    id_contrat = click.prompt("ID du contrat", type=int)

    montant_restant = click.prompt(
        "Montant restant (€) (laisser vide pour ne pas changer)",
        default="",
        show_default=False
    )
    statut = click.confirm("Le contrat est-il signé ?", default=None)
    montant_restant_final = float(montant_restant) if montant_restant.strip() else None

    updates = {k: v for k, v in {
        "montant_restant": montant_restant_final,
        "statut": statut
    }.items() if v is not None}

    if not updates:
        console.print("[bold yellow]Aucune modification apportée.[/bold yellow]")
        return

    with SessionLocal() as db:
        try:
            contrat = update_contrat_commercial_service(db, token, id_contrat, **updates)

            if contrat.client.id_commercial != user_id:
                raise PermissionError(
                    "Vous ne pouvez modifier que les contrats de vos propres "
                    "clients."
                )

            if updates.get("statut"):
                sentry_sdk.capture_message(
                    f"📜 Contrat ID {contrat.id} signé (Commercial) - "
                    f"Client : {contrat.client.nom_complet}",
                    level="info"
                )

            console.print(
                f"[bold green]Contrat ID {contrat.id} mis à jour avec succès ![/bold green]\n"
                f"   🔹 Client : {contrat.client.nom_complet}\n"
                f"   🔹 Montant Total : {contrat.montant_total}€\n"
                f"   🔹 Montant Restant : {contrat.montant_restant}€\n"
                f"   🔹 Statut : {'Signé' if contrat.statut else 'Non signé'}"
            )
        except PermissionError as e:
            console.print(f"[bold red]Erreur : {e}[/bold red]")
        except ValueError as e:
            console.print(f"[bold red]Erreur : {e}[/bold red]")
        except Exception as e:
            sentry_sdk.capture_exception(e)
            console.print(f"[bold red]Erreur inattendue : {e}[/bold red]")
