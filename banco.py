import sqlite3


def conectar():
    return sqlite3.connect("financeiro.db", check_same_thread=False)


def criar_tabelas():
    conn = sqlite3.connect("financeiro.db")
    cursor = conn.cursor()

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE,
        senha TEXT
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
        valor REAL
    )
    """
    )

    conn.commit()
    conn.close()
