from functools import wraps
from rich.console import Console
from app.auth.jwt_utils import decode_token
from app.utils.file_utils import load_token
import jwt

console = Console()


def role_required(allowed_roles):
    """Décorateur pour restreindre une commande aux rôles spécifiés."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            token = load_token()
            if not token:
                console.print("[bold red]Vous devez être connecté pour utiliser cette commande.[/bold red]")
                return

            try:
                payload = decode_token(token)
                user_role = payload.get("role")

                if user_role not in allowed_roles:
                    console.print(f"[bold red]Accès refusé : Cette commande est réservée aux rôles {allowed_roles}.[/bold red]")
                    return

                return func(*args, **kwargs)
            except jwt.ExpiredSignatureError:
                console.print("[bold red]Erreur : Votre session a expiré. Veuillez vous reconnecter.[/bold red]")
            except Exception as e:
                console.print(f"[bold red]Erreur d'authentification : {e}[/bold red]")
        return wrapper
    return decorator


# Décorateurs pour chaque rôle
gestion_required = role_required(["gestion"])
commercial_required = role_required(["commercial"])
support_required = role_required(["support"])
read_only_required = role_required([
    "gestion", "commercial", "support", "lecture"
])
