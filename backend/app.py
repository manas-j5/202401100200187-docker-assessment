import os
from datetime import datetime, timezone

from flask import Flask, jsonify, request
import psycopg2

app = Flask(__name__)
registrations = []


def get_connection():
    database_host = os.getenv("DB_HOST")
    if not database_host:
        return None

    return psycopg2.connect(
        host=database_host,
        dbname=os.getenv("DB_NAME", "festpass"),
        user=os.getenv("DB_USER", "festpass"),
        password=os.getenv("DB_PASSWORD"),
        connect_timeout=2,
    )


def database_available():
    try:
        connection = get_connection()
        if connection is None:
            return False
        connection.close()
        return True
    except (OSError, psycopg2.Error):
        return False


def load_registrations():
    connection = get_connection()
    if connection is None:
        return registrations

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS registrations (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL
                )
                """
            )
            cursor.execute(
                "SELECT id, name, email, created_at FROM registrations ORDER BY id"
            )
            rows = cursor.fetchall()
    connection.close()
    return [
        {
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "created_at": row[3].isoformat(),
        }
        for row in rows
    ]


@app.get("/api/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "database": database_available(),
            "version": os.getenv("APP_VERSION", "0.1"),
            "regno": os.getenv("REGNO", ""),
        }
    )


@app.get("/api/registrations")
def get_registrations():
    try:
        return jsonify(load_registrations())
    except (OSError, psycopg2.Error):
        return jsonify({"error": "database unavailable"}), 503


@app.post("/api/registrations")
def create_registration():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    email = str(payload.get("email", "")).strip()

    if not name or not email:
        return jsonify({"error": "name and email are required"}), 400

    created_at = datetime.now(timezone.utc)
    connection = get_connection()
    if connection is None:
        registration = {
            "id": len(registrations) + 1,
            "name": name,
            "email": email,
            "created_at": created_at.isoformat(),
        }
        registrations.append(registration)
        return jsonify(registration), 201

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS registrations (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL
                )
                """
            )
            cursor.execute(
                """
                INSERT INTO registrations (name, email, created_at)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (name, email, created_at),
            )
            registration_id = cursor.fetchone()[0]
    connection.close()
    registration = {
        "id": registration_id,
        "name": name,
        "email": email,
        "created_at": created_at.isoformat(),
    }
    return jsonify(registration), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)