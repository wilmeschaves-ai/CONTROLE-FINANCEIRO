import streamlit as st
import pandas as pd
from banco import conectar


def render():
    st.title("👑 Admin")

    conn = conectar()

    df = pd.read_sql("SELECT id, usuario, tipo FROM usuarios", conn)
    st.dataframe(df)

    user_id = st.selectbox(
        "Usuário",
        df["id"],
        format_func=lambda x: df[df["id"] == x]["usuario"].values[0],
    )

    tipo = st.selectbox("Tipo", ["usuario", "admin"])

    if st.button("Atualizar"):
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE usuarios SET tipo=? WHERE id=?",
            (tipo, user_id),
        )
        conn.commit()
        st.success("Atualizado!")
        st.rerun()
