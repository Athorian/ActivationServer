
from flask import Flask, request, jsonify, send_file
from db import init_db, get_license, update_license_activation, set_license_status, create_license
import license_core   # Vérification cryptographique

app = Flask(__name__)

# Initialisation de la base au démarrage
init_db()

@app.route("/activate", methods=["POST"])
def activate():
    data = request.get_json(force=True, silent=True) or {}

    license_key = data.get("key")
    machine_id = data.get("machine_id")

    if not license_key or not machine_id:
        return jsonify({"status": "DENIED", "reason": "MISSING_DATA"}), 400

    # Vérification cryptographique
    if not license_core.verify_key(license_key):
        return jsonify({"status": "DENIED", "reason": "INVALID_SIGNATURE"}), 403

    # Vérification dans la base
    lic = get_license(license_key)
    if lic is None:
        return jsonify({"status": "DENIED", "reason": "UNKNOWN_KEY"}), 404

    # Mise à jour de l'activation
    result = update_license_activation(license_key, machine_id)
    if result is None:
        return jsonify({"status": "DENIED", "reason": "UNKNOWN_KEY"}), 404

    if result["status"] != "OK":
        return jsonify(result), 403

    return jsonify(result), 200


@app.route("/key-info/<license_key>", methods=["GET"])
def key_info(license_key):
    lic = get_license(license_key)
    if lic is None:
        return jsonify({"error": "UNKNOWN_KEY"}), 404

    return jsonify({
        "license_key": lic["license_key"],
        "machine_id": lic["machine_id"],
        "activation_count": lic["activation_count"],
        "max_activations": lic["max_activations"],
        "status": lic["status"],
        "first_activation_at": lic["first_activation_at"],
        "last_activation_at": lic["last_activation_at"],
    })


@app.route("/block/<license_key>", methods=["POST"])
def block_key(license_key):
    set_license_status(license_key, "blocked")
    return jsonify({"status": "OK", "license_key": license_key, "new_status": "blocked"})


@app.route("/revoke/<license_key>", methods=["POST"])
def revoke_key(license_key):
    set_license_status(license_key, "revoked")
    return jsonify({"status": "OK", "license_key": license_key, "new_status": "revoked"})


# ---------------------------------------------------------
# 🔥 AJOUT MINIMAL : route pour télécharger licenses.db
# ---------------------------------------------------------
@app.route("/licenses.db", methods=["GET"])
def download_db():
    return send_file("licenses.db", as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
