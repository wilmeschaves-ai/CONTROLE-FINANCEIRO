import streamlit as st
import pandas as pd
from datetime import datetime
from banco import conectar


def render():
    st.subheader("💰 Lançamentos")

    conn = conectar()
    cursor = conn.cursor()

    # =========================
    # SALVAR
    # =========================
    def salvar(data, tipo, categoria, descricao, valor, forma):
        cursor.execute(
            """
            INSERT INTO lancamentos 
            (usuario_id, data, tipo, categoria, descricao, valor, forma_pagamento)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                st.session_state.usuario_id,
                data,
                tipo,
                categoria,
                descricao,
                valor,
                forma,
            ),
        )
        conn.commit()

    # =========================
    # EXCLUIR
    # =========================
    def excluir(id_):
        cursor.execute(
            "DELETE FROM lancamentos WHERE id=? AND usuario_id=?",
            (id_, st.session_state.usuario_id),
        )
        conn.commit()

    # =========================
    # ATUALIZAR
    # =========================
    def atualizar(id_, data, tipo, categoria, descricao, valor, forma):
        cursor.execute(
            """
            UPDATE lancamentos SET
            data=?, tipo=?, categoria=?, descricao=?, valor=?, forma_pagamento=?
            WHERE id=? AND usuario_id=?
        """,
            (
                data,
                tipo,
                categoria,
                descricao,
                valor,
                forma,
                id_,
                st.session_state.usuario_id,
            ),
        )
        conn.commit()

    # =========================
    # FORM
    # =========================
    data = st.date_input("Data")
    st.write("Data selecionada:", data.strftime("%d/%m/%Y"))
    tipo = st.selectbox("Tipo", ["Receita", "Despesa"])

    categorias = {
        "Receita": ["Salário", "Extra"],
        "Despesa": [
            "Aluguel",
            "Mercado",
            "Energia",
            "Agua",
            "Transporte",
            "Internet",
            "Dizimo",
            "Saude",
            "Educação",
            "Outros",
        ],
    }

    categoria = st.selectbox("Categoria", categorias[tipo])
    valor = st.number_input("Valor", min_value=0.0)
    descricao = st.text_input("Descrição")

    forma = st.selectbox(
        "Forma",
        [
            "Pix",
            "Dinheiro",
            "Cartão de Débito",
            "Cartão de Crédito",
            "Crédito em conta",
            "Outros",
        ],
    )

    if st.button("Salvar"):
        salvar(data.strftime("%Y-%m-%d"), tipo, categoria, descricao, valor, forma)
        st.success("Salvo!")
        st.rerun()

    # =========================
    # LISTA
    # =========================
    df = pd.read_sql(
        "SELECT * FROM lancamentos WHERE usuario_id=?",
        conn,
        params=(st.session_state.usuario_id,),
    )

    if not df.empty:
        df["data"] = pd.to_datetime(df["data"])

        df_exibir = df.copy()
        df_exibir["data"] = df_exibir["data"].dt.strftime("%d/%m/%Y")

        st.dataframe(df_exibir)

        # EXCLUIR
        id_del = st.selectbox("Excluir ID", df["id"], key="del")
        if st.button("Excluir"):
            excluir(id_del)
            st.rerun()

        # EDITAR
        id_edit = st.selectbox("Editar ID", df["id"], key="edit")
        linha = df[df["id"] == id_edit].iloc[0]

        nova_data = st.date_input("Nova data", linha["data"])
        novo_valor = st.number_input("Novo valor", value=float(linha["valor"]))

        if st.button("Atualizar"):
            atualizar(
                id_edit,
                nova_data.strftime("%Y-%m-%d"),
                linha["tipo"],
                linha["categoria"],
                linha["descricao"],
                novo_valor,
                linha["forma_pagamento"],
            )
            st.rerun()
