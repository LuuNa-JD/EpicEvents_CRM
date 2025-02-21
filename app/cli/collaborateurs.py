import click
import re
import sentry_sdk
from rich.console import Console
from app.services.collaborateur_service import (
    create_new_collaborateur,
    update_existing_collaborateur,
    delete_collaborateur_service,
    all_collaborateurs,
    get_collaborateur_by_id
)
from app.db.session import SessionLocal
from app.auth.permissions import role_required
from app.utils.config import CustomGroup
from app.utils.file_utils import load_token
from app.auth.jwt_utils import decode_token
from app.services.departement_service import get_all_departements
from app.crud.clients import get_clients_by_commercial
from app.db.models.collaborateur import Collaborateur

console = Console()


@click.group(
    name="collaborateurs",
    no_args_is_help=False,
    invoke_without_command=True,
    cls=CustomGroup
)
@click.pass_context
def collaborateurs_group(ctx):
    """Commandes pour gérer les collaborateurs."""
    if ctx.invoked_subcommand is None:
        console.print("[bold yellow]❗ Utilisez 'help' pour voir les commandes disponibles.[/bold yellow]")
        ctx.exit(1)


@collaborateurs_group.command(name="create")
@role_required(["gestion"])
def create_collaborateur():
    """Créer un nouveau collaborateur en tant que gestionnaire."""
    token = load_token()
    if not token:
        console.print("[bold red]Erreur : Vous devez être connecté pour cette commande.[/bold red]")
        return

    payload = decode_token(token)
    if not payload:
        console.print("[bold red]Erreur : Token invalide ou expiré. Veuillez vous reconnecter.[/bold red]")
        return

    user_id = payload.get("user_id")
    role = payload.get("role")

    if role != "gestion":
        console.print("[bold red]Erreur : Seuls les gestionnaires peuvent créer un collaborateur.[/bold red]")
        return

    console.print(f"[bold cyan]🔹 Token valide - Utilisateur ID {user_id} - Rôle : {role}[/bold cyan]")

    # Récupération des informations utilisateur
    nom = click.prompt("Nom", type=str)
    prenom = click.prompt("Prénom", type=str)
    email = click.prompt("Email", type=str)
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        console.print("[bold red]Erreur : Email invalide.[/bold red]")
        return
    login = click.prompt("Nom d'utilisateur", type=str)
    password = click.prompt("Mot de passe", type=str, hide_input=True)

    # Récupération et affichage des départements disponibles
    with SessionLocal() as db:
        departements = get_all_departements(db)
        departement_choices = {str(dep.id): dep.nom for dep in departements}

    console.print("\n[bold cyan]Départements disponibles :[/bold cyan]")
    for dep_id, dep_nom in departement_choices.items():
        console.print(f"   🔹 {dep_id} - {dep_nom}")

    # Demander à l'utilisateur de choisir un département
    departement_id = click.prompt(
        "\nSélectionnez un département par son numéro",
        type=click.Choice(departement_choices.keys(), case_sensitive=False),
        show_choices=False
    )

    departement_id = int(departement_id)  # 🔹 Convertir en entier

    with SessionLocal() as db:
        try:
            collaborateur = create_new_collaborateur(
                db, token, nom, prenom, email, departement_id, login, password
            )
            db.commit()
            sentry_sdk.capture_message(
                f"Collaborateur {nom} {prenom} créé par {payload.get('nom') + ' ' + payload.get('prenom')} (Gestion)",
                level="info"
            )
            console.print(
                f"[bold green]Collaborateur {collaborateur.nom} créé avec succès ![/bold green]"
            )
        except Exception as e:
            db.rollback()
            sentry_sdk.capture_exception(e)
            console.print(f"[bold red]Erreur lors de la création du collaborateur : {e}[/bold red]")


@collaborateurs_group.command(name="list")
@role_required(["gestion"])
def list_collaborateurs():
    """Lister tous les collaborateurs."""
    token = load_token()
    if not token:
        console.print(
            "[bold red]Erreur : Vous devez être connecté pour cette commande.[/bold red]"
        )
        return

    payload = decode_token(token)
    if not payload:
        console.print(
            "[bold red]Erreur : Token invalide ou expiré. "
            "Veuillez vous reconnecter.[/bold red]"
        )
        return

    user_id = payload.get("user_id")
    role = payload.get("role")

    if role != "gestion":
        console.print(
            "[bold red]Erreur : Seuls les gestionnaires peuvent "
            "lister les collaborateurs.[/bold red]"
        )
        return

    console.print(
        f"[bold cyan]🔹 Token valide - Utilisateur ID {user_id} - "
        f"Rôle : {role}[/bold cyan]"
    )

    with SessionLocal() as db:
        collaborateurs = all_collaborateurs(db)
        if not collaborateurs:
            console.print(
                "[bold yellow]Aucun collaborateur trouvé.[/bold yellow]"
            )
            return

        console.print("\n[bold cyan]Liste des collaborateurs :[/bold cyan]")
        for collab in collaborateurs:
            console.print(
                f"   🔹 ID {collab.id} - {collab.nom} {collab.prenom} - "
                f"{collab.email} - {collab.departement.nom}"
            )


@collaborateurs_group.command(name="show")
@role_required(["gestion"])
@click.argument("collaborateur_id", type=int)
def show_collaborateur(collaborateur_id):
    """Afficher les détails d'un collaborateur."""
    token = load_token()
    if not token:
        console.print(
            "[bold red]Erreur : Vous devez être connecté pour cette commande.[/bold red]"
        )
        return

    payload = decode_token(token)
    if not payload:
        console.print(
            "[bold red]Erreur : Token invalide ou expiré. "
            "Veuillez vous reconnecter.[/bold red]"
        )
        return

    with SessionLocal() as db:
        try:
            collaborateur = get_collaborateur_by_id(db, collaborateur_id)
            if not collaborateur:
                console.print(
                    f"[bold red]Erreur : Collaborateur ID {collaborateur_id} non trouvé.[/bold red]"
                )
                return

            # Afficher les infos du collaborateur
            console.print(
                f"\n[bold cyan]Détails du collaborateur ID {collaborateur_id} :[/bold cyan]"
            )
            console.print(
                f"   🔹 Nom : {collaborateur.nom} {collaborateur.prenom}\n"
                f"   🔹 Email : {collaborateur.email}\n"
                f"   🔹 Département : {collaborateur.departement.nom}\n"
                f"   🔹 Login : {collaborateur.login}"
            )

            # Si le collaborateur est un commercial, afficher ses clients
            if collaborateur.departement.nom == "commercial":
                clients = get_clients_by_commercial(db, collaborateur_id)
                if clients:
                    console.print("\n[bold cyan]Clients gérés :[/bold cyan]")
                    for client in clients:
                        console.print(f"   🔹 {client.nom_complet} ({client.email})")
                else:
                    console.print("[bold magenta]Ce commercial n'a pas encore de clients.[/bold magenta]")

        except Exception as e:
            console.print(f"[bold red]Erreur : {e}[/bold red]")


@collaborateurs_group.command(name="update")
@role_required(["gestion"])
def update_collaborateur():
    """Mettre à jour un collaborateur."""
    token = load_token()
    if not token:
        console.print("[bold red]Erreur : Vous devez être connecté pour cette commande.[/bold red]")
        return

    payload = decode_token(token)
    if not payload:
        console.print("[bold red]Erreur : Token invalide ou expiré. Veuillez vous reconnecter.[/bold red]")
        return

    role = payload.get("role")
    if role != "gestion":
        console.print("[bold red]Erreur : Seuls les gestionnaires peuvent mettre à jour un collaborateur.[/bold red]")
        return

    collaborateur_id = click.prompt("ID Collaborateur", type=int)

    nom = click.prompt("Nouveau nom (laisser vide pour ne pas changer)", default="", show_default=False)
    prenom = click.prompt("Nouveau prénom (laisser vide pour ne pas changer)", default="", show_default=False)
    email = click.prompt("Nouvel email (laisser vide pour ne pas changer)", default="", show_default=False)
    if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        console.print("[bold red]Erreur : Email invalide.[/bold red]")
        return
    login = click.prompt("Nouveau login (laisser vide pour ne pas changer)", default="", show_default=False)
    password = click.prompt("Nouveau mot de passe (laisser vide pour ne pas changer)", default="", show_default=False, hide_input=True)

    with SessionLocal() as db:
        departements = get_all_departements(db)
        departement_choices = {str(dep.id): dep.nom for dep in departements}

        console.print("\n[bold cyan]Départements disponibles :[/bold cyan]")
        for dep_id, dep_nom in departement_choices.items():
            console.print(f"   🔹 {dep_id} - {dep_nom}")

        departement_choices = ["1", "2", "3"]
        departement_id = click.prompt(
            "\nSélectionnez un département par son numéro (laisser vide pour ne pas changer)",
            type=str,
            default="",
            show_default=False
        )

        # Si l'utilisateur laisse vide, on ne change pas le département
        if not departement_id.strip():
            departement_id = None
        elif departement_id not in ["1", "2", "3"]:
            console.print("[bold red]Erreur : Sélection invalide.[/bold red]")
            return
        else:
            departement_id = int(departement_id)

    updates = {k: v for k, v in {
        "nom": nom,
        "prenom": prenom,
        "email": email,
        "departement_id": departement_id,
        "login": login
    }.items() if v}

    if password:
        updates["password_hash"] = Collaborateur.set_password(password)

    if not updates:
        console.print("[bold yellow]Aucune modification apportée.[/bold yellow]")
        return

    with SessionLocal() as db:
        try:
            collaborateur = update_existing_collaborateur(db, token, collaborateur_id, **updates)
            if collaborateur:
                modified_fields = ", ".join(updates.keys())
                sentry_sdk.capture_message(
                    f"🔧 Collaborateur {collaborateur.nom} (ID {collaborateur.id}) "
                    f"modifié par {payload.get('nom') + ' ' + payload.get('prenom')}: "
                    f"{modified_fields}",
                    level="info"
                )
                console.print(f"[bold green]Collaborateur ID {collaborateur.id} mis à jour avec succès ![/bold green]")
        except PermissionError as e:
            console.print(f"[bold red]Erreur d'autorisation : {e}[/bold red]")
        except ValueError as e:
            console.print(f"[bold red]Erreur : {e}[/bold red]")
        except Exception as e:
            sentry_sdk.capture_exception(e)
            console.print(f"[bold red]Erreur inattendue : {e}[/bold red]")


@collaborateurs_group.command(name="delete")
@role_required(["gestion"])
@click.argument("collaborateur_id", type=int)
def delete_collaborateur(collaborateur_id):
    """
    Supprimer un collaborateur en tant que gestionnaire.
    """
    token = load_token()
    if not token:
        console.print("[bold red]Erreur : Vous devez être connecté pour cette commande.[/bold red]")
        return

    payload = decode_token(token)
    if not payload:
        console.print("[bold red]Erreur : Token invalide ou expiré. Veuillez vous reconnecter.[/bold red]")
        return

    role = payload.get("role")
    if role != "gestion":
        console.print("[bold red]Erreur : Seuls les gestionnaires peuvent supprimer un collaborateur.[/bold red]")
        return

    console.print(f"\n[bold cyan]🔹 Suppression du collaborateur ID {collaborateur_id}...[/bold cyan]")

    confirmation = click.confirm("Êtes-vous sûr de vouloir supprimer ce collaborateur ?", default=False)
    if not confirmation:
        console.print("[bold yellow]Suppression annulée.[/bold yellow]")
        return

    with SessionLocal() as db:
        try:
            collaborateur = delete_collaborateur_service(db, token, collaborateur_id)
            if collaborateur:
                sentry_sdk.capture_message(
                    f"Collaborateur {collaborateur.nom} (ID {collaborateur.id}) supprimé par {payload.get('nom') + ' ' + payload.get('prenom')}",
                    level="info"
                )
                console.print(f"[bold green]Collaborateur ID {collaborateur.id} supprimé avec succès ![/bold green]")
            else:
                console.print(f"[bold red]Erreur : Collaborateur ID {collaborateur_id} non trouvé.[/bold red]")
        except PermissionError as e:
            console.print(f"[bold red]Erreur d'autorisation : {e}[/bold red]")
        except Exception as e:
            sentry_sdk.capture_exception(e)
            console.print(f"[bold red]Erreur inattendue : {e}[/bold red]")
