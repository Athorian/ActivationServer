
# add_key.py
# ---------------------------------------------------------
# Script pour ajouter une clé KJP dans la base SQLite
# Utilisation :
#   - Interactif : python add_key.py
#   - Ligne de commande : python add_key.py KJP-XXXX-XXXX-XXXX-SIGN 3
# ---------------------------------------------------------

import sys
from db import create_license, init_db
import license_core

# Initialisation automatique de la base de données
init_db()


def main():
    # Mode ligne de commande : clé + max_activations
    if len(sys.argv) >= 3:
        key = sys.argv[1].strip().upper()
        try:
            max_act = int(sys.argv[2].strip())
        except ValueError:
            print("❌ ERREUR : max_activations doit être un entier.")
            return
    else:
        print("=== Ajout d'une clé KJP dans la base du serveur ===")
        key = input("Entrez la clé KJP (ex: KJP-AB12-CD34-EF56-9A3F) : ").strip().upper()
        try:
            max_act = int(input("Nombre maximum d'activations autorisées : ").strip())
        except ValueError:
            print("❌ ERREUR : Veuillez entrer un nombre entier.")
            return

    # Vérification cryptographique
    if not license_core.verify_key(key):
        print("❌ ERREUR : La clé n'est pas valide (signature incorrecte).")
        return

    # Ajout dans la base
    create_license(key, max_act)

    print("✔ Clé ajoutée avec succès dans la base.")
    print(f"   → Clé : {key}")
    print(f"   → Activations max : {max_act}")


if __name__ == "__main__":
    main()
