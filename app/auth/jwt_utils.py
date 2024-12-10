import jwt
import datetime
from app.core.config import settings


def generate_token(user_id: int, role: str):
    """Génère un token JWT pour un utilisateur."""
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def decode_token(token: str):
    """Décode et vérifie un token JWT."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        print("Erreur : Votre token a expiré.")
        return None
    except jwt.InvalidTokenError:
        print("Erreur : Token invalide.")
        return None