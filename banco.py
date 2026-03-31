import sqlite3


def conectar():
    return sqlite3.connect("financeiro.db", check_same_thread=False)


def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE,
        senha TEXT,
        tipo TEXT DEFAULT 'usuario'
    )
    """
    )

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS lancamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        data TEXT,
        tipo TEXT,
        categoria TEXT,
        descricao TEXT,
        valor REAL,
        forma_pagamento TEXT
    )
    """
    )

    conn.commit()
    conn.close()


def adicionar_coluna_feedback():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(usuarios)")
    colunas = [col[1] for col in cursor.fetchall()]

    if "satisfacao" not in colunas:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN satisfacao TEXT")
        conn.commit()

    conn.close()
