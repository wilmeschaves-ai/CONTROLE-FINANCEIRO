import sqlite3


def conectar():
    return sqlite3.connect("financeiro.db", check_same_thread=False)


def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    # Tabela de usuários
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE,
        senha TEXT
    )
    """
    )

    # Tabela de lançamentos
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
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    )
    """
    )

    conn.commit()
    conn.close()
