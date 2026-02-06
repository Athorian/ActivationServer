
import secrets
import hmac
import hashlib

# Clé secrète commune (ne jamais diffuser)
# Doit être identique dans license_manager.py
SECRET_KEY = b'"uo,AYw8s!=3V#RxffNr'

# Préfixe des clés générées
PREFIX = "KJP"


# ---------------------------------------------------------
#  GÉNÉRATION DES BLOCS
# ---------------------------------------------------------
def generate_block():
    """
    Génère un bloc hexadécimal de 4 caractères (2 octets).
    Exemple : 'A3F9'
    """
    return secrets.token_hex(2).upper()


# ---------------------------------------------------------
#  SIGNATURE DU 4ᵉ BLOC
# ---------------------------------------------------------
def sign_key(prefix, b1, b2, b3):
    """
    Calcule la signature du 4ᵉ bloc (b4) à partir des 3 premiers blocs.
    Signature = 4 premiers caractères du SHA256(prefix-b1-b2-b3)
    """
    base = f"{prefix}-{b1}-{b2}-{b3}"
    digest = hmac.new(SECRET_KEY, base.encode("utf-8"), hashlib.sha256).hexdigest().upper()
    return digest[:4]


# ---------------------------------------------------------
#  GÉNÉRATION DE CLÉ
# ---------------------------------------------------------
def generate_key():
    """
    Génère une clé complète :
    KJP-XXXX-XXXX-XXXX-SIGN
    """
    b1 = generate_block()
    b2 = generate_block()
    b3 = generate_block()
    b4 = sign_key(PREFIX, b1, b2, b3)
    return f"{PREFIX}-{b1}-{b2}-{b3}-{b4}"


# ---------------------------------------------------------
#  DÉCOMPOSITION DE CLÉ
# ---------------------------------------------------------
def split_key(key: str):
    """
    Décompose une clé en ses 5 blocs.
    Retourne None si le format est incorrect.
    """
    parts = key.strip().upper().split("-")
    if len(parts) != 5:
        return None

    prefix, b1, b2, b3, b4 = parts

    if prefix != PREFIX:
        return None

    if not all(len(x) == 4 for x in (b1, b2, b3, b4)):
        return None

    return prefix, b1, b2, b3, b4


# ---------------------------------------------------------
#  VÉRIFICATION DE CLÉ
# ---------------------------------------------------------
def verify_key(key: str) -> bool:
    """
    Vérifie :
    - le format de la clé
    - la signature interne (b4)
    """
    parsed = split_key(key)
    if not parsed:
        return False

    prefix, b1, b2, b3, b4 = parsed

    base = f"{prefix}-{b1}-{b2}-{b3}"
    digest = hmac.new(SECRET_KEY, base.encode("utf-8"), hashlib.sha256).hexdigest().upper()
    expected_b4 = digest[:4]

    return b4 == expected_b4
