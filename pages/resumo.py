import streamlit as st
import pandas as pd
from banco import conectar
from datetime import datetime


def render():
    st.subheader("📊 Resumo")

    conn = conectar()

    df = pd.read_sql(
        "SELECT * FROM lancamentos WHERE usuario_id=?",
        conn,
        params=(st.session_state.usuario_id,),
    )

    if df.empty:
        st.warning("Sem dados")
        return

    df["data"] = pd.to_datetime(df["data"])

    mes = st.selectbox("Mês", list(range(1, 13)))
    ano = st.selectbox("Ano", list(range(2025, datetime.today().year + 1)))

    df = df[(df["data"].dt.month == mes) & (df["data"].dt.year == ano)]

    receitas = df[df["tipo"] == "Receita"]["valor"].sum()
    despesas = df[df["tipo"] == "Despesa"]["valor"].sum()

    st.metric("Receitas", f"R$ {receitas:,.2f}")
    st.metric("Despesas", f"R$ {despesas:,.2f}")
    st.metric("Saldo", f"R$ {receitas - despesas:,.2f}")
