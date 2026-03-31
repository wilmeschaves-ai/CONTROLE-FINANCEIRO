import streamlit as st
import pandas as pd
import altair as alt
from banco import conectar


def render():
    st.subheader("📈 Análise")

    conn = conectar()

    df = pd.read_sql(
        "SELECT * FROM lancamentos WHERE usuario_id=?",
        conn,
        params=(st.session_state.usuario_id,),
    )

    if df.empty:
        st.warning("Sem dados")
        return

    df = df[df["tipo"] == "Despesa"]

    resumo = df.groupby("categoria")["valor"].sum().reset_index()

    chart = alt.Chart(resumo).mark_bar().encode(x="categoria", y="valor")

    st.altair_chart(chart, use_container_width=True)
