from app.auth.permissions import check_permission
from app.auth.jwt_utils import generate_token
from app.utils.file_utils import save_token


def test_gestion_permission():
    """Vérifie qu'une action réservée à 'gestion' fonctionne."""
    token = generate_token(1, "gestion")
    save_token(token)

    @check_permission(["gestion"])
    def gestion_action():
        return "Action autorisée"

    assert gestion_action() == "Action autorisée"


def test_permission_refusee():
    """Vérifie qu'une action protégée est refusée pour un rôle incorrect."""
    token = generate_token(1, "commercial")
    save_token(token)

    @check_permission(["gestion"])
    def gestion_action():
        return "Action autorisée"

    assert gestion_action() is None
