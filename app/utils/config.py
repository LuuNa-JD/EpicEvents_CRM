import os
import json
from dotenv import load_dotenv
from rich.console import Console
import click

# Initialize the console
console = Console()

# Charger les variables d'environnement
load_dotenv()


def get_role_commands():
    """
    Charge ROLE_COMMANDS depuis .env et le convertit en dictionnaire Python.
    """
    role_commands_json = os.getenv("ROLE_COMMANDS")
    if role_commands_json:
        return json.loads(role_commands_json)
    return {}  # Retourne un dictionnaire vide en cas d'erreur


def get_command_description(cmd):
    """Retourne une description plus détaillée des commandes."""
    descriptions = {
        "help": "Affiche la liste des commandes disponibles avec leur description.",
        "auth": "Commandes pour gérer l'authentification.",
        "auth login": "Se connecter en utilisant le login et le mot de passe.",
        "auth logout": "Se déconnecter et supprimer le token JWT.",
        "auth status": "Vérifier si l'utilisateur est connecté et afficher son rôle",
        "clients": "Commandes pour gérer les clients",
        "clients list": "Lister les clients disponibles du commercial, ajouter '-all' pour voir tous les clients.",
        "clients show": "Afficher les détails d'un client par ID : ajouter l'ID du client.",
        "clients create": "Créer un nouveau client (Commercial uniquement).",
        "clients update": "Modifier un client existant (Commercial uniquement).",
        "contrats list": "Afficher la liste des contrats.",
        "evenements list": "Voir tous les événements.",
        "collaborateurs list": "Lister tous les collaborateurs.",
        "create_user": "Créer un nouvel utilisateur (Admin uniquement).",
        "delete_user": "Supprimer un utilisateur (Admin uniquement).",
        "update_user": "Modifier les informations d'un utilisateur (Admin uniquement).",
        "clear": "Nettoyer l'affichage du terminal.",
        "exit": "Quitter l'application."
    }
    return descriptions.get(cmd, "Aucune description disponible.")


class CustomGroup(click.Group):
    """Gère les erreurs pour les sous-commandes."""
    def get_command(self, ctx, cmd_name):
        """Intercepter les erreurs sur les sous-commandes."""
        command = super().get_command(ctx, cmd_name)
        if command is None:
            console.print(f"[bold red]Erreur : La sous-commande '{cmd_name}' n'existe pas.[/bold red]")
            ctx.exit(1)
        return command
