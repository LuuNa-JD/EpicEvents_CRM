import os

TOKEN_FILE = os.path.expanduser("~/.epicevents_token")


def save_token(token: str):
    """Stocke le token localement."""
    with open(TOKEN_FILE, "w") as file:
        file.write(token)


def load_token():
    """Charge le token stocké localement."""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as file:
            return file.read()
    return None


def delete_token():
    """Supprime le token JWT stocké localement."""
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
        return True
    return False
