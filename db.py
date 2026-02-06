
import sqlite3
from datetime import datetime
from config import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS licenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            license_key TEXT UNIQUE NOT NULL,
            machine_id TEXT,
            activation_count INTEGER NOT NULL DEFAULT 0,
            max_activations INTEGER NOT NULL DEFAULT 1,
            status TEXT NOT NULL DEFAULT 'active', -- active / blocked / revoked
            first_activation_at TEXT,
            last_activation_at TEXT
        );
        """
    )
    conn.commit()
    conn.close()

def get_license(license_key):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM licenses WHERE license_key = ?", (license_key,))
    row = cur.fetchone()
    conn.close()
    return row

def create_license(license_key, max_activations=1):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT OR IGNORE INTO licenses (license_key, max_activations)
        VALUES (?, ?)
        """,
        (license_key, max_activations),
    )
    conn.commit()
    conn.close()

def update_license_activation(license_key, machine_id):
    now = datetime.utcnow().isoformat()
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM licenses WHERE license_key = ?", (license_key,))
    row = cur.fetchone()
    if row is None:
        conn.close()
        return None

    stored_machine_id = row["machine_id"]
    activation_count = row["activation_count"]
    max_activations = row["max_activations"]
    status = row["status"]

    if status in ("blocked", "revoked"):
        conn.close()
        return {"status": "DENIED", "reason": status.upper()}

    # Première activation : on lie la clé à cette machine
    if stored_machine_id is None:
        stored_machine_id = machine_id
        activation_count = 0

    # Si la clé est déjà liée à une autre machine → refus
    if stored_machine_id != machine_id:
        conn.close()
        return {"status": "DENIED", "reason": "MACHINE_MISMATCH"}

    if activation_count >= max_activations:
        conn.close()
        return {"status": "DENIED", "reason": "TOO_MANY_ACTIVATIONS"}

    activation_count += 1

    cur.execute(
        """
        UPDATE licenses
        SET machine_id = ?,
            activation_count = ?,
            last_activation_at = ?,
            first_activation_at = COALESCE(first_activation_at, ?)
        WHERE license_key = ?
        """,
        (stored_machine_id, activation_count, now, now, license_key),
    )
    conn.commit()
    conn.close()

    return {
        "status": "OK",
        "activation_count": activation_count,
        "max_activations": max_activations,
    }

def set_license_status(license_key, new_status):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE licenses SET status = ? WHERE license_key = ?",
        (new_status, license_key),
    )
    conn.commit()
    conn.close()
