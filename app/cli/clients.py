import click
from rich.console import Console
import re
from app.services.client_service import (
    list_all_clients,
    create_client_for_commercial,
    update_client_by_commercial,
    get_client_details
)
from app.crud.clients import get_client_id
from app.utils.file_utils import load_token
from app.auth.jwt_utils import decode_token
from app.db.session import SessionLocal
from app.auth.permissions import role_required
from app.utils.config import CustomGroup

console = Console()


@click.group(
    name="clients",
    no_args_is_help=False,
    invoke_without_command=True,
    cls=CustomGroup
)
@click.pass_context
def clients_group(ctx):
    """Commandes pour gérer les clients."""
    if ctx.invoked_subcommand is None:  # Si aucune sous-commande n'est fournie
        console.print("[bold yellow]❗ Utilisez 'help' pour voir les commandes "
                      "disponibles.[/bold yellow]")
        ctx.exit(1)


@clients_group.command(name="list")
@role_required(["gestion", "support", "commercial"])
@click.option("-all", "-a", is_flag=True)
def list_clients(all):
    """
    Liste les clients disponibles dans le CRM.
    """
    token = load_token()
    if not token:
        console.print("[bold red]Erreur : Vous devez être connecté pour "
                      "accéder à cette commande.[/bold red]")
        return

    # Décoder le token et vérifier le rôle
    payload = decode_token(token)
    if not payload:
        console.print("[bold red]Erreur : Token invalide ou expiré. "
                      "Veuillez vous reconnecter.[/bold red]")
        return

    role = payload.get("role")
    console.print(f"[bold cyan]Rôle actuel : {role}[/bold cyan]")

    # Se connecter à la base de données
    with SessionLocal() as db:
        try:
            clients = list_all_clients(db=db, token=token, all_clients=all)

            if clients:
                mode = "TOUS" if all else "MES CLIENTS"
                console.print(
                    f"[bold green]Liste des clients ({mode}):[/bold green]"
                )
                for client in clients:
                    console.print(
                        f"[bold yellow]ID {client.id}[/bold yellow] - "
                        f"{client.nom_complet} - {client.email} - "
                        f"{client.telephone}"
                    )
            else:
                console.print("[bold magenta]Aucun client trouvé."
                              "[/bold magenta]")
        except Exception as e:
            console.print(
                f"[bold red]Erreur lors de la récupération des clients : "
                f"{e}[/bold red]"
            )


@clients_group.command(name="create")
@role_required(["commercial"])
def create_client():
    """
    Créer un nouveau client en tant que commercial.
    """
    # Charger et vérifier le token JWT
    token = load_token()
    if not token:
        console.print("[bold red]Erreur : Vous devez être connecté pour cette "
                      "commande.[/bold red]")
        return

    payload = decode_token(token)
    if not payload:
        console.print("[bold red]Erreur : Token invalide ou expiré. "
                      "Veuillez vous reconnecter.[/bold red]")
        return

    user_id = payload.get("user_id")
    role = payload.get("role")

    # Vérifier que l'utilisateur est un commercial
    if role != "commercial":
        console.print("[bold red]Erreur : Seuls les commerciaux peuvent créer "
                      "un client.[/bold red]")
        return

    console.print(f"[bold cyan]🔹 Token valide - Utilisateur ID {user_id} - "
                  f"Rôle : {role}[/bold cyan]")

    # Saisie des informations du client
    nom = click.prompt("Nom complet", type=str)
    email = click.prompt("Email", type=str)
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        console.print("[bold red]Erreur : Email invalide.[/bold red]")
        return
    telephone = click.prompt("Téléphone", type=str)
    if not re.match(r"0[1-9]\d{8}", telephone):
        console.print("[bold red]Erreur : Numéro de "
                      "téléphone invalide.[/bold red]")
        return
    entreprise = click.prompt("Nom de l'entreprise", type=str)

    # Connexion à la base de données et création du client
    with SessionLocal() as db:
        try:
            client = create_client_for_commercial(
                db, user_id, nom, email, telephone, entreprise
            )
            db.commit()
            console.print(f"[bold green] Client '{client.nom_complet}' "
                          "créé avec succès ![/bold green]")
        except Exception as e:
            db.rollback()
            console.print(f"[bold red] Erreur lors de la création "
                          f"du client : {e}[/bold red]")


@clients_group.command(name="update")
@role_required(["commercial"])
def update_client():
    """
    Modifier un client existant en tant que commercial
    (uniquement ses propres clients).
    """
    # Charger le token JWT sauvegardé
    token = load_token()
    if not token:
        console.print("[bold red]Erreur : Vous devez être connecté "
                      "pour cette commande.[/bold red]")
        return

    # Décoder le token pour extraire les informations
    payload = decode_token(token)
    if not payload:
        console.print("[bold red]Erreur : Token invalide ou expiré. "
                      "Veuillez vous reconnecter.[/bold red]")
        return

    user_id = payload.get("user_id")
    role = payload.get("role")

    # Vérifier si l'utilisateur a le bon rôle
    if role != "commercial":
        console.print("[bold red]Erreur : Seuls les commerciaux peuvent "
                      "modifier un client.[/bold red]")
        return

    # Demander l'ID du client à modifier
    client_id = click.prompt("ID du client à modifier", type=int)

    with SessionLocal() as db:
        client = get_client_id(db, client_id)
        if not client:
            console.print("[bold red]Erreur : Client introuvable.[/bold red]")
            return

        if client.id_commercial != user_id:
            console.print("[bold red]Erreur : Vous ne pouvez modifier que vos "
                          "propres clients.[/bold red]")
            return

    # Demander les champs à modifier (avec valeurs par défaut à None)
    nom = click.prompt(
        "Nouveau nom (laisser vide pour ne pas changer)",
        default="",
        type=str
    )
    email = click.prompt(
        "Nouvel email (laisser vide pour ne pas changer)",
        default="",
        type=str
    )
    if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        console.print("[bold red]Erreur : Email invalide.[/bold red]")
        return
    telephone = click.prompt(
        "Nouveau téléphone (laisser vide pour ne pas changer)",
        default="",
        type=str
    )
    if telephone and not re.match(r"0[1-9]\d{8}", telephone):
        console.print("[bold red]Erreur : Numéro de téléphone "
                      "invalide.[/bold red]")
        return
    entreprise = click.prompt(
        "Nouvelle entreprise (laisser vide pour ne pas changer)",
        default="",
        type=str
    )

    # Construire l'objet updates
    updates = {k: v for k, v in {
        "nom_complet": nom,
        "email": email,
        "telephone": telephone,
        "nom_entreprise": entreprise
    }.items() if v}

    if not updates:
        console.print("[bold yellow]Aucune modification "
                      "apportée.[/bold yellow]")
        return

    # Mettre à jour le client en base de données
    with SessionLocal() as db:
        try:
            client = update_client_by_commercial(
                db, token, client_id, **updates
            )
            if client:
                console.print(f"[bold green]Client ID {client.id} mis à jour "
                              "avec succès ![/bold green]")
        except PermissionError as e:
            console.print(f"[bold red]Erreur d'autorisation : {e}[/bold red]")
        except ValueError as e:
            console.print(f"[bold red]Erreur : {e}[/bold red]")
        except Exception as e:
            console.print(f"[bold red]Erreur inattendue : {e}[/bold red]")


@clients_group.command(name="show")
@role_required(["gestion", "support", "commercial"])
@click.argument("client_id", type=int)
def show_client(client_id):
    """
    Affiche tous les détails d'un client par son ID.
    """
    token = load_token()
    if not token:
        console.print("[bold red]Erreur : Vous devez être connecté pour cette "
                      "commande.[/bold red]")
        return

    payload = decode_token(token)
    if not payload:
        console.print("[bold red]Erreur : Token invalide ou expiré. "
                      "Veuillez vous reconnecter.[/bold red]")
        return

    role = payload.get("role")
    user_id = payload.get("user_id")

    with SessionLocal() as db:
        try:
            client = get_client_details(db, client_id, user_id, role)
            if client:
                console.print(f"\n[bold green]📋 Détails complets du client "
                              f"ID {client.id} :[/bold green]")
                console.print(f"[bold yellow]Nom :"
                              f"[/bold yellow] {client.nom_complet}")
                console.print(f"[bold yellow]Email :"
                              f"[/bold yellow] {client.email}")
                console.print(f"[bold yellow]Téléphone :"
                              f"[/bold yellow] {client.telephone}")
                console.print(f"[bold yellow]Entreprise :"
                              f"[/bold yellow] {client.nom_entreprise}")
                console.print(f"[bold yellow]Date de création :"
                              f"[/bold yellow] {client.date_creation}")
                console.print(f"[bold yellow]Dernière mise à jour :"
                              f"[/bold yellow] "
                              f"{client.date_derniere_mise_a_jour}")

                # Afficher les détails du commercial associé
                if client.commercial:
                    console.print("\n[bold cyan]Commercial "
                                  "associé :[/bold cyan]")
                    console.print(f"Nom : {client.commercial.nom}")
                    console.print(f"Prénom : {client.commercial.prenom}")
                    console.print(f"Email : {client.commercial.email}")

                # Afficher les contrats liés au client
                console.print("\n[bold cyan]Contrats liés :[/bold cyan]")
                if client.contrats:
                    for contrat in client.contrats:
                        console.print(f"- ID Contrat {contrat.id} : "
                                      f"Montant Total "
                                      f"{contrat.montant_total}€, "
                                      f"Statut : "
                                      f"{'Signé' if contrat.statut == True else 'Non signé'}"
                                      )
                else:
                    console.print("[italic]Aucun contrat trouvé.[/italic]")

            else:
                console.print("[bold magenta]Client non trouvé ou "
                              "accès refusé.[/bold magenta]")
        except PermissionError as e:
            console.print(f"[bold red]Erreur d'autorisation : {e}[/bold red]")
        except ValueError as e:
            console.print(f"[bold red]Erreur : {e}[/bold red]")
        except Exception as e:
            console.print(f"[bold red]Erreur inattendue : {e}[/bold red]")
