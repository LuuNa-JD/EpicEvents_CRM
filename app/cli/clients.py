import click
from rich.console import Console
from app.services.client_service import (
    list_all_clients,
    create_client_for_commercial,
)
from app.utils.file_utils import load_token
from app.auth.jwt_utils import decode_token
from app.db.session import SessionLocal

console = Console()


@click.group(name="clients", help="Commandes pour gérer les clients.")
def clients_group():
    pass


@clients_group.command(name="list", help="Afficher tous les clients.")
def list_clients():
    """
    Liste tous les clients disponibles dans le CRM.
    """
    token = load_token()
    if not token:
        console.print(
            "[bold red]Erreur : Vous devez être connecté pour accéder à cette "
            "commande.[/bold red]"
        )
        return

    # Décoder le token pour vérifier la validité et récupérer le rôle
    payload = decode_token(token)
    if not payload:
        console.print(
            "[bold red]Erreur : Token invalide ou expiré. "
            "Veuillez vous reconnecter.[/bold red]"
        )
        return

    role = payload.get("role")
    console.print(f"[bold cyan]Rôle actuel : {role}[/bold cyan]")

    # Se connecter à la base de données
    with SessionLocal() as db:
        try:
            # Appeler le service pour récupérer les clients
            clients = list_all_clients(db=db, token=token)
            if clients:
                console.print("[bold green]Liste des clients :[/bold green]")
                for client in clients:
                    console.print(
                        f"• [yellow]{client.nom_complet}[/yellow] - "
                        f"{client.email} - {client.telephone}"
                    )
            else:
                console.print(
                    "[bold magenta]Aucun client trouvé.[/bold magenta]"
                )
        except Exception as e:
            console.print(
                f"[bold red]Erreur lors de la récupération des clients : "
                f"{e}[/bold red]"
            )


@clients_group.command(name="create", help="Créer un nouveau client.")
def create_client():
    """
    Créer un nouveau client en tant que commercial.
    """
    # Charger le token JWT sauvegardé
    token = load_token()
    if not token:
        console.print(
            "[bold red]Erreur : Vous devez être connecté pour cette commande."
            "[/bold red]"
        )
        return

    # Décoder le token pour extraire les informations
    payload = decode_token(token)
    if not payload:
        console.print(
            "[bold red]Erreur : Token invalide ou expiré. "
            "Veuillez vous reconnecter.[/bold red]"
        )
        return

    role = payload.get("role")
    user_id = payload.get("user_id")

    # Vérifier si l'utilisateur a le bon rôle
    if role != "commercial":
        console.print(
            "[bold red]Erreur : Seuls les utilisateurs avec le rôle 'commercial' "
            "peuvent créer un client.[/bold red]"
            "peuvent créer un client.[/bold red]"
        )
        return

    # Si l'utilisateur est autorisé, on demande les informations
    nom = click.prompt("Nom complet", type=str)
    email = click.prompt("Email", type=str)
    telephone = click.prompt("Téléphone", type=str)
    entreprise = click.prompt("Nom de l'entreprise", type=str)

    # Créer le client
    with SessionLocal() as db:
        try:
            # Appel au service pour créer un client
            create_client_for_commercial(
                db, user_id, nom, email, telephone, entreprise
            )
            console.print(
                f"[bold green]Client '{nom}' créé avec succès ![/bold green]"
            )
        except Exception as e:
            console.print(
                f"[bold red]Erreur lors de la création du client : {e}[/bold red]"
            )
