import streamlit as st
import pandas as pd
from datetime import datetime
import io
import calendar
import altair as alt


hoje = datetime.today()

st.markdown(
    """
<style>

/* Selectbox (dropdown) */
div[data-baseweb="select"] > div {
    cursor: pointer !important;
}

/* Área clicável do select */
div[data-baseweb="select"] {
    cursor: pointer !important;
}

/* Opções dentro do dropdown */
ul {
    cursor: pointer !important;
}

/* Itens da lista */
li {
    cursor: pointer !important;
}

</style>
""",
    unsafe_allow_html=True,
)

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Controle Financeiro", layout="wide")
st.title("🏠 Controle Financeiro Pessoal")

ARQUIVO = "financas.csv"

# =========================
# CARREGAR DADOS
# =========================
try:
    df = pd.read_csv(ARQUIVO)
except:
    df = pd.DataFrame(columns=["Data", "Tipo", "Categoria", "Descricao", "Valor"])

if not df.empty:
    df["Data"] = pd.to_datetime(df["Data"], dayfirst=True, errors="coerce")

# =========================
# CATEGORIAS
# =========================

# =========================
# MENU
# =========================
menu = st.sidebar.radio("Menu", ["Lançamentos", "Resumo", "Análise", "Metas"])

# =========================
# LANÇAMENTOS
# =========================

categorias = {
    "Receita": ["Salário", "Extra"],
    "Despesa": [
        "Aluguel",
        "Luz",
        "Água",
        "Internet",
        "Mercado",
        "Transporte",
        "Lazer",
        "Saúde",
        "Outros",
    ],
}

if menu == "Lançamentos":
    st.subheader("➕ Novo Lançamento")

    col1, col2 = st.columns(2)

    with col1:
        # data = st.date_input("Data", datetime.today())

        data_str = st.text_input(
            "Data (DD/MM/AAAA)", datetime.today().strftime("%d/%m/%Y")
        )

        try:
            data = pd.to_datetime(data_str, dayfirst=True)

        except:
            st.error("❌ Data inválida! Use o formato DD/MM/AAAA")
            st.stop()

        tipo = st.selectbox("Tipo", ["Receita", "Despesa"])

    with col2:

        categoria = st.selectbox("Categoria", categorias[tipo])

        valor = st.number_input("Valor", min_value=0.0, format="%.2f")

    descricao = st.text_input("Descrição")

    if st.button("Salvar"):
        data_formatada = pd.to_datetime(data).strftime("%d/%m/%Y")

        novo = pd.DataFrame(
            [
                {
                    "Data": pd.to_datetime(data),
                    "Tipo": tipo,
                    "Categoria": categoria,
                    "Descricao": descricao,
                    "Valor": valor,
                }
            ]
        )

        df = pd.concat([df, novo], ignore_index=True)
        df.to_csv(ARQUIVO, index=False)

        st.success("✅ Lançamento salvo!")

    st.divider()
    st.subheader("📋 Histórico")

    if not df.empty:
        df_exibir = df.copy()
        df_exibir["Data"] = df_exibir["Data"].dt.strftime("%d/%m/%Y")

        st.dataframe(df_exibir, use_container_width=True)

        # ---------------
        st.divider()
        st.subheader("🗑️ Excluir Lançamento")

        indice = st.number_input(
            "Digite o índice do lançamento para excluir",
            min_value=0,
            max_value=len(df) - 1,
            step=1,
        )

        if st.button("Excluir"):
            df = df.drop(indice)
            df.to_csv(ARQUIVO, index=False)
            st.success("✅ Lançamento excluído!")
            st.rerun()
            # ---------------


# =========================
# RESUMO
# =========================
elif menu == "Resumo":

    st.subheader("📊 Visão Geral")

    col1, col2 = st.columns(2)
    with col1:

        # ------------------

        hoje = datetime.today()

        meses = {
            1: "Janeiro",
            2: "Fevereiro",
            3: "Março",
            4: "Abril",
            5: "Maio",
            6: "Junho",
            7: "Julho",
            8: "Agosto",
            9: "Setembro",
            10: "Outubro",
            11: "Novembro",
            12: "Dezembro",
        }

        mes_num = st.selectbox(
            "Mês",
            list(meses.keys()),
            format_func=lambda x: meses[x],
            index=hoje.month - 1,
        )
        # mes = st.selectbox("Mês", list(range(1, 13)), index=hoje.month - 1)
        # ------------------

    with col2:
        # ano = st.selectbox("Ano", [2024, 2025, 2026])
        # ------------------
        anos = list(range(2020, hoje.year + 5))

        ano = st.selectbox("Ano", anos, index=anos.index(hoje.year))

        # ------------------

    if not df.empty:

        df_filtrado = df[(df["Data"].dt.month == mes_num) & (df["Data"].dt.year == ano)]

        receitas = df_filtrado[df_filtrado["Tipo"] == "Receita"]["Valor"].sum()
        despesas = df_filtrado[df_filtrado["Tipo"] == "Despesa"]["Valor"].sum()
        saldo = receitas - despesas

        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Receitas", f"R$ {receitas:,.2f}")
        c2.metric("💸 Despesas", f"R$ {despesas:,.2f}")
        c3.metric("Saldo", f"R$ {saldo:,.2f}")

        if despesas > receitas:
            st.error("⚠️ Você gastou mais do que ganhou!")

        # EXPORTAR EXCEL
        st.divider()
        st.subheader("📥 Exportar")

        buffer = io.BytesIO()
        df_filtrado.to_excel(buffer, index=False, engine="openpyxl")
        buffer.seek(0)

        st.download_button(
            label="📊 Baixar Excel do mês",
            data=buffer,
            file_name=f"financeiro_{mes_num}_{ano}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

# =========================
# ANÁLISE
# =========================
elif menu == "Análise":

    st.subheader("📈 Para onde vai seu dinheiro")

    if not df.empty:
        despesas_df = df[df["Tipo"] == "Despesa"]

        if not despesas_df.empty:
            resumo = despesas_df.groupby("Categoria")["Valor"].sum()

            chart = (
                alt.Chart(resumo.reset_index())
                .mark_bar(color="#6BAED6")  # azul suave
                .encode(x="Categoria", y="Valor")
            )

            st.altair_chart(chart, use_container_width=True)

        else:
            st.warning("Sem despesas cadastradas.")

# =========================
# METAS
# =========================
elif menu == "Metas":

    st.subheader("🎯 Meta de Economia")

    meta = st.number_input("Meta mensal (R$)", min_value=0.0)

    if not df.empty:
        receitas = df[df["Tipo"] == "Receita"]["Valor"].sum()
        despesas = df[df["Tipo"] == "Despesa"]["Valor"].sum()
        saldo = receitas - despesas

        st.write(f"Saldo atual: R$ {saldo:,.2f}")

        if saldo >= meta:
            st.success("🎉 Meta atingida!")
        else:
            st.warning("Continue economizando!")
