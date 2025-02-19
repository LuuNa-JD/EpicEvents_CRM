COMMAND_DESCRIPTIONS = {
        "help": (
            "Affiche la liste des commandes disponibles avec leur "
            "description."
        ),
        "auth": "Commandes pour gérer l'authentification.",
        "auth login": "Se connecter en utilisant le login et le mot de passe.",
        "auth logout": "Se déconnecter et supprimer le token JWT.",
        "auth status": (
            "Vérifier si l'utilisateur est connecté et afficher son rôle"
        ),
        "clients": "Commandes pour gérer les clients",
        "clients list": (
            "Lister les clients disponibles du commercial, ajouter '-all' "
            "pour voir tous les clients."
        ),
        "clients show": (
            "Afficher les détails d'un client par ID : ajouter l'ID du client."
        ),
        "clients create": (
            "Créer un nouveau client (Commercial uniquement)."
        ),
        "clients update": (
            "Modifier un client existant (Commercial uniquement)."
        ),
        "contrats": "Commandes pour gérer les contrats.",
        "contrats create": (
            "Créer un nouveau contrat (Gestion uniquement)."
        ),
        "contrats list": (
            "Afficher la liste des contrats. Ajouter '-unsigned' pour les "
            "contrats non signés, '-unpaid' pour les contrats impayés., "
            "'-all' "
            "pour tous les contrats (commercial uniquement)."
        ),
        "contrats update": (
            "Mettre à jour un contrat existant (Gestion uniquement)."
        ),
        "contrats update-mine": (
            "Mettre à jour un contrat existant (Commercial uniquement)."
        ),
        "evenements": "Commandes pour gérer les événements.",
        "evenements create": (
            "Créer un nouvel événement (Commercial uniquement)."
        ),
        "evenements assign_support": (
            "Assigner un support à un événement (Gestion uniquement)."
        ),
        "evenements list": (
            "Lister les événements, ajouter '-mine' pour les événements "
            "attribués au support et '-unassigned' pour les événements sans "
            "support. (Gestion uniquement)."
        ),
        "evenements update": (
            "Mettre à jour un événement (Support uniquement)."
        ),
        "collaborateurs": "Commandes pour gérer les collaborateurs.",
        "collaborateurs create": (
            "Créer un nouveau collaborateur (Gestion uniquement)."
        ),
        "collaborateurs list": "Lister tous les collaborateurs.",
        "collaborateurs show": (
            "Afficher les détails d'un collaborateur par ID."
        ),
        "collaborateurs update": (
            "Mettre à jour un collaborateur (Gestion uniquement)."
        ),
        "collaborateurs delete": (
            "Supprimer un collaborateur (Gestion uniquement)."
        ),
        "clear": "Nettoyer l'affichage du terminal.",
        "exit": "Quitter l'application."
    }


def get_command_description(cmd):
    return COMMAND_DESCRIPTIONS.get(cmd, "Aucune description disponible.")
