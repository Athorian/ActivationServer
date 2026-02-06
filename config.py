
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "licenses.db")

# On préparera plus tard une vraie clé secrète pour HMAC (Étape D)
HMAC_SECRET_KEY = b"CHANGE_ME_LATER_FOR_HMAC"
