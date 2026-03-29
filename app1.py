import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date

# =========================
# BANCO DE DADOS
# =========================
conn = sqlite3.connect("financeiro.db", check_same_thread=False)
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

# =========================
# SESSION STATE
# =========================
if "logado" not in st.session_state:
    st.session_state.logado = False

if "usuario_id" not in st.session_state:
    st.session_state.usuario_id = None


# =========================
# LOGIN / CADASTRO
# =========================
def tela_login():
    st.title("💰 Sistema Financeiro")

    opcao = st.radio("Acesso", ["Login", "Cadastro"])

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if opcao == "Cadastro":
        if st.button("Criar conta"):
            try:
                cursor.execute(
                    "INSERT INTO usuarios (usuario, senha) VALUES (?, ?)",
                    (usuario, senha),
                )
                conn.commit()
                st.success("Conta criada com sucesso!")
            except:
                st.error("Usuário já existe")

    else:
        if st.button("Entrar"):
            cursor.execute(
                "SELECT id FROM usuarios WHERE usuario=? AND senha=?", (usuario, senha)
            )
            result = cursor.fetchone()

            if result:
                st.session_state.logado = True
                st.session_state.usuario_id = result[0]
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos")


# =========================
# BLOQUEIO LOGIN
# =========================
if not st.session_state.logado:
    tela_login()
    st.stop()


# =========================
# LOGOUT
# =========================
st.sidebar.success("Logado com sucesso")

if st.sidebar.button("🚪 Sair"):
    st.session_state.logado = False
    st.session_state.usuario_id = None
    st.rerun()


# =========================
# SALVAR LANÇAMENTO
# =========================
from datetime import datetime, date


def salvar(data, tipo, categoria, descricao, valor):

    # 🔥 garante que sempre é date
    if isinstance(data, str):
        # aceita BR OU ISO automaticamente
        try:
            data = datetime.strptime(data, "%d/%m/%Y")
        except:
            data = datetime.strptime(data, "%Y-%m-%d")

    data_iso = data.strftime("%Y-%m-%d")

    cursor.execute(
        """
        INSERT INTO lancamentos (
            usuario_id, data, tipo, categoria, descricao, valor
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (st.session_state.usuario_id, data_iso, tipo, categoria, descricao, valor),
    )

    conn.commit()


# =========================
# CARREGAR DADOS
# =========================
def carregar():
    return pd.read_sql_query(
        """
        SELECT * FROM lancamentos
        WHERE usuario_id = ?
        ORDER BY id DESC
    """,
        conn,
        params=(st.session_state.usuario_id,),
    )


# =========================
# SISTEMA PRINCIPAL
# =========================
st.title("📊 Controle Financeiro")

menu = st.sidebar.radio("Menu", ["Lançamentos", "Resumo"])

df = carregar()

# =========================
# LANÇAMENTOS
# =========================
if menu == "Lançamentos":

    st.subheader("➕ Novo Lançamento")

    categorias = {
        "Receita": ["Salário", "Extra"],
        "Despesa": ["Aluguel", "Luz", "Água", "Internet", "Mercado", "Outros"],
    }

    data = st.date_input("Data", datetime.today())
    tipo = st.selectbox("Tipo", ["Receita", "Despesa"])
    categoria = st.selectbox("Categoria", categorias[tipo])
    descricao = st.text_input("Descrição")
    valor = st.number_input("Valor", min_value=0.0)
    data = data.strftime("%d/%m/%Y")
    if st.button("Salvar"):
        salvar(data, tipo, categoria, descricao, valor)
        st.success("Lançamento salvo!")
        st.rerun()

    st.divider()
    st.subheader("📋 Histórico")

    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    df["data"] = df["data"].dt.strftime("%d/%m/%Y")
    st.dataframe(df, use_container_width=True)


# =========================
# RESUMO
# =========================
if menu == "Resumo":

    st.subheader("📊 Resumo")

    receitas = df[df["tipo"] == "Receita"]["valor"].sum()
    despesas = df[df["tipo"] == "Despesa"]["valor"].sum()
    saldo = receitas - despesas

    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Receitas", f"R$ {receitas:,.2f}")
    c2.metric("💸 Despesas", f"R$ {despesas:,.2f}")
    c3.metric("📊 Saldo", f"R$ {saldo:,.2f}")

    if saldo < 0:
        st.error("⚠️ Você está no vermelho!")
