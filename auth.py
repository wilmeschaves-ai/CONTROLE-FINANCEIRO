import streamlit as st
import hashlib
from banco import conectar


def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()


def login(usuario, senha):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, tipo FROM usuarios WHERE usuario=? AND senha=?",
        (usuario, hash_senha(senha)),
    )

    return cursor.fetchone()


def cadastrar(usuario, senha):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO usuarios (usuario, senha) VALUES (?, ?)",
            (usuario, hash_senha(senha)),
        )
        conn.commit()
        return True
    except:
        return False
