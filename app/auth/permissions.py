from functools import wraps
from app.auth.jwt_utils import decode_token
from app.utils.file_utils import load_token
import jwt


def check_permission(required_roles):
    """
    Décorateur pour vérifier si le rôle de l'utilisateur permet
    d'accéder à une action.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            token = load_token()  # Charge le token JWT stocké localement
            if not token:
                print(
                    "Erreur : Vous devez vous connecter pour accéder à cette "
                    "action."
                )
                return
            try:
                payload = decode_token(token)  # Décodage du JWT
                user_role = payload.get("role")
                if user_role in required_roles:
                    f"Accès autorisé. Rôle : {user_role}"
                    return func(*args, **kwargs)

                else:
                    print(
                        f"Accès refusé. Cette action nécessite : "
                        f"{required_roles}"
                    )
            except jwt.ExpiredSignatureError:
                print("Erreur : Votre session a expiré. "
                      "Veuillez vous reconnecter.")
            except Exception as e:
                print(f"Erreur d'authentification : {e}")
        return wrapper
    return decorator


# Décorateurs pour chaque département
gestion_required = check_permission(["gestion"])  # Équipe Gestion
commercial_required = check_permission(["commercial"])  # Équipe Commerciale
support_required = check_permission(["support"])  # Équipe Support
read_only_required = check_permission([
    "gestion",
    "commercial",
    "support",
    "lecture"
])  # Lecture seule
