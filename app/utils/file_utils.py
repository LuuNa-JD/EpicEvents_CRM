import os
from cryptography.fernet import Fernet, InvalidToken

# Chemin sécurisé du token
TOKEN_FILE = os.path.expanduser("~/.epicevents_token")
KEY_FILE = os.path.expanduser("~/.epicevents_key")  # Clé de chiffrement


# Générer une clé de chiffrement si elle n'existe pas encore
def generate_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)


# Charger la clé de chiffrement
def load_key():
    with open(KEY_FILE, "rb") as key_file:
        return key_file.read()


# Stocke le token chiffré
def save_token(token: str):
    """Stocke le token en le chiffrant."""
    generate_key()  # Génère la clé si elle n'existe pas
    key = load_key()
    cipher = Fernet(key)

    encrypted_token = cipher.encrypt(token.encode())

    with open(TOKEN_FILE, "wb") as file:
        file.write(encrypted_token)

    # Sécuriser les permissions du fichier
    os.chmod(TOKEN_FILE, 0o600)  # Seulement accessible par l'utilisateur


# Charge et déchiffre le token
def load_token():
    """Charge et déchiffre le token stocké localement."""
    if not os.path.exists(TOKEN_FILE):
        return None

    key = load_key()
    cipher = Fernet(key)

    with open(TOKEN_FILE, "rb") as file:
        encrypted_token = file.read()

    try:
        return cipher.decrypt(encrypted_token).decode()
    except (InvalidToken, TypeError):
        print("Erreur : Impossible de déchiffrer le token "
              "(corrompu ou clé invalide).")
        return None


def delete_token():
    """Supprime le token JWT stocké localement de manière sécurisée."""
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
        return True
    return False
