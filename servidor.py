# PFO 2 - Sistema de Gestión de Tareas
# Servidor con Flask + SQLite (arquitectura cliente-servidor)

import sqlite3
from flask import Flask, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "clave-secreta-pfo2"
DB = "usuarios.db"


def inicializar_db():
    """Crea la tabla de usuarios si todavía no existe."""
    with sqlite3.connect(DB) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )"""
        )


def datos_validos(data):
    """Revisa que lleguen usuario y contraseña como texto y no vacíos."""
    if not data:
        return False
    usuario = data.get("usuario")
    contraseña = data.get("contraseña")
    if not isinstance(usuario, str) or not isinstance(contraseña, str):
        return False
    return usuario.strip() != "" and contraseña != ""


@app.route("/registro", methods=["POST"])
def registro():
    data = request.get_json(silent=True)
    if not datos_validos(data):
        return jsonify({"error": "Se necesitan usuario y contraseña"}), 400

    usuario = data["usuario"].strip()
    # Se guarda el hash, nunca la contraseña en texto plano
    password_hash = generate_password_hash(data["contraseña"])

    try:
        with sqlite3.connect(DB) as conn:
            conn.execute(
                "INSERT INTO usuarios (usuario, password_hash) VALUES (?, ?)",
                (usuario, password_hash),
            )
    except sqlite3.IntegrityError:
        return jsonify({"error": "El usuario ya existe"}), 409

    return jsonify({"mensaje": f"Usuario '{usuario}' registrado con éxito"}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if not datos_validos(data):
        return jsonify({"error": "Se necesitan usuario y contraseña"}), 400

    usuario = data["usuario"].strip()

    with sqlite3.connect(DB) as conn:
        fila = conn.execute(
            "SELECT password_hash FROM usuarios WHERE usuario = ?", (usuario,)
        ).fetchone()

    # Mismo mensaje si falla el usuario o la contraseña
    if fila is None or not check_password_hash(fila[0], data["contraseña"]):
        return jsonify({"error": "Usuario o contraseña incorrectos"}), 401

    session["usuario"] = usuario
    return jsonify({"mensaje": f"Bienvenido, {usuario}"}), 200


@app.route("/tareas", methods=["GET"])
def tareas():
    # HTML de bienvenida (requisito de la consigna)
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Gestión de Tareas</title>
    </head>
    <body style="font-family: Arial; text-align: center; margin-top: 80px;">
        <h1>¡Bienvenido al Sistema de Gestión de Tareas!</h1>
        <p>Accediste correctamente a la sección de tareas.</p>
    </body>
    </html>
    """


if __name__ == "__main__":
    inicializar_db()
    app.run(debug=True)
