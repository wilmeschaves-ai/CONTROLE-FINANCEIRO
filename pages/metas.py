import streamlit as st
import pandas as pd
from banco import conectar


def render():
    st.subheader("🎯 Metas")

    meta = st.number_input("Meta mensal", min_value=0.0)

    conn = conectar()

    df = pd.read_sql(
        "SELECT * FROM lancamentos WHERE usuario_id=?",
        conn,
        params=(st.session_state.usuario_id,),
    )

    if not df.empty:
        receitas = df[df["tipo"] == "Receita"]["valor"].sum()
        despesas = df[df["tipo"] == "Despesa"]["valor"].sum()

        saldo = receitas - despesas

        st.write(f"Saldo atual: R$ {saldo:,.2f}")

        if saldo >= meta:
            st.success("Meta atingida!")
        else:
            st.warning("Continue economizando!")
