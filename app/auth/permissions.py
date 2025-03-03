from functools import wraps
from rich.console import Console
from app.auth.jwt_utils import decode_token
from app.utils.file_utils import load_token
import jwt
from app.utils.sentry import sentry_sdk

console = Console()


def role_required(allowed_roles):
    """Décorateur pour restreindre une commande aux rôles spécifiés."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            token = load_token()
            if not token:
                error_message = (
                    "Vous devez être connecté pour utiliser cette commande."
                )
                console.print(f"[bold red]{error_message}[/bold red]")
                sentry_sdk.capture_message(error_message, level="warning")
                return

            try:
                payload = decode_token(token)
                user_role = payload.get("role")

                if user_role not in allowed_roles:
                    error_message = (
                        "Accès refusé : Cette commande est réservée aux rôles "
                        f"{allowed_roles}. Utilisateur avec "
                        f"rôle '{user_role}' "
                        " tenté d'y accéder."
                    )
                    console.print(f"[bold red]{error_message}[/bold red]")
                    sentry_sdk.capture_message(error_message, level="warning")
                    return

                return func(*args, **kwargs)
            except jwt.ExpiredSignatureError:
                error_message = (
                    "Erreur : Votre session a expiré. Veuillez vous "
                    "reconnecter."
                )
                console.print(f"[bold red]{error_message}[/bold red]")
                sentry_sdk.capture_message(error_message, level="warning")
            except Exception as e:
                error_message = f"Erreur d'authentification : {e}"
                console.print(f"[bold red]{error_message}[/bold red]")
                sentry_sdk.capture_exception(e)
        return wrapper
    return decorator


# Décorateurs pour chaque rôle
gestion_required = role_required(["gestion"])
commercial_required = role_required(["commercial"])
support_required = role_required(["support"])
read_only_required = role_required([
    "gestion", "commercial", "support", "lecture"
])
