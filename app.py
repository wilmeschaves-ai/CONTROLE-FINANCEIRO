import streamlit as st
import pandas as pd
from datetime import datetime
import io
import calendar
import altair as alt

import sqlite3
from banco import conectar, criar_tabelas


conn = sqlite3.connect("financeiro.db", check_same_thread=False)
cursor = conn.cursor()

# SESSION STATE
if "logado" not in st.session_state:
    st.session_state.logado = False

if "usuario_id" not in st.session_state:
    st.session_state.usuario_id = None


def tela_cadastro():
    st.title("🆕 Criar Conta")

    novo_usuario = st.text_input("Novo usuário")
    nova_senha = st.text_input("Nova senha", type="password")

    if st.button("Cadastrar"):
        if not novo_usuario or not nova_senha:
            st.warning("Preencha todos os campos")
            return

        # verifica se já existe
        cursor.execute("SELECT id FROM usuarios WHERE usuario=?", (novo_usuario,))
        if cursor.fetchone():
            st.error("Usuário já existe")
            return

        cursor.execute(
            "INSERT INTO usuarios (usuario, senha) VALUES (?, ?)",
            (novo_usuario, nova_senha),
        )
        conn.commit()

        st.success("✅ Usuário criado com sucesso!")


def tela_login():
    st.title("🔐 Login")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

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
            st.error("Login inválido")


def init_state():
    defaults = {"logado": False, "usuario_id": None, "nome_usuario": ""}

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()


if "logado" not in st.session_state:
    st.session_state.logado = False

if "usuario_id" not in st.session_state:
    st.session_state.usuario_id = None


if not st.session_state.logado:

    opcao = st.radio("Escolha", ["Login", "Cadastrar"])

    if opcao == "Login":
        tela_login()
    else:
        tela_cadastro()

    st.stop()


criar_tabelas()


# -----------------------
# SESSION
# -----------------------
def salvar_lancamento(data, tipo, categoria, descricao, valor):
    cursor.execute(
        """
        INSERT INTO lancamentos (
            usuario_id, data, tipo, categoria, descricao, valor
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (st.session_state.usuario_id, data, tipo, categoria, descricao, valor),
    )
    conn.commit()


def carregar_dados():
    return pd.read_sql_query(
        """
        SELECT * FROM lancamentos
        WHERE usuario_id = ?
    """,
        conn,
        params=(st.session_state.usuario_id,),
    )


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


def moeda_br(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def cor_valor(valor):
    if valor > 0:
        return "green"
    elif valor < 0:
        return "red"
    else:
        return "gray"


def valor_colorido(v, tipo):
    if tipo == "Receita":
        cor = "#22c55e"  # verde
    elif tipo == "Despesa":
        cor = "#ef4444"  # vermelho
    else:
        cor = "#9ca3af"  # cinza

    return f'<span style="color:{cor}; font-weight:bold">{moeda_br(v)}</span>'


# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Controle Financeiro", layout="wide")
st.title("🏠 Controle Financeiro")
# st.title("💰 Controle Financeiro")


df = carregar_dados()

if not df.empty:
    df["data"] = pd.to_datetime(df["data"])
# st.dataframe(df)


# =========================
# MENU
# =========================

menu = st.radio(
    "Menu",
    ["Lançamentos", "Resumo", "Análise", "Metas"],
    horizontal=True,
    key="menu_principal",
)

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

        data_str = st.text_input(
            "data (DD/MM/AAAA)", datetime.today().strftime("%d/%m/%Y")
        )

        try:
            data = pd.to_datetime(data_str, dayfirst=True)

        except:
            st.error("❌ Data inválida! Use o formato DD/MM/AAAA")
            st.stop()

        tipo = st.selectbox("tipo", ["Receita", "Despesa"])

    with col2:

        categoria = st.selectbox("categoria", categorias[tipo])

        valor = st.number_input("valor", min_value=0.0, format="%.2f")

        descricao = st.text_input("Descrição")

    if st.button("Salvar"):
        salvar_lancamento(data.strftime("%Y-%m-%d"), tipo, categoria, descricao, valor)
        st.success("✅ Lançamento salvo!")
        st.rerun()

    st.divider()
    st.subheader("📋 Histórico")

    if not df.empty:
        df_exibir = df.copy()
        df_exibir["data"] = df_exibir["data"].dt.strftime("%d/%m/%Y")

        st.dataframe(df_exibir, use_container_width=True)

        # ---------------
        st.divider()
        st.subheader("🗑️ Excluir Lançamento")

        st.write("Selecione o lançamento para excluir:")

        selecao = st.selectbox(
            "Escolha o lançamento",
            df_exibir.index,
            format_func=lambda x: f"{df_exibir.loc[x, 'data']} | {df_exibir.loc[x, 'categoria']} | R$ {df_exibir.loc[x, 'valor']:.2f}",
        )

        if st.button("Excluir"):
            df = df.drop(selecao)
            st.success("✅ Lançamento excluído!")
            st.rerun()

# =========================
# RESUMO
# =========================

elif menu == "Resumo":

    st.subheader("📊 Resumo")

    # 🔥 FILTRO AQUI (logo abaixo do título)
    col1, col2 = st.columns(2)

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

    mes_num = col1.selectbox(
        "Mês",
        list(meses.keys()),
        format_func=lambda x: meses[x],
        index=datetime.today().month - 1,
    )

    ano = col2.selectbox(
        "Ano",
        list(range(2020, datetime.today().year + 5)),
        index=datetime.today().year - 2020,
    )

    # 🔽 DEPOIS vem os cálculos
    df["data"] = pd.to_datetime(df["data"], errors="coerce")

    # df_filtrado = df[(df["data"].dt.month == mes_num) & (df["data"].dt.year == ano)]

    df_filtrado = df[(df["data"].dt.month == mes_num) & (df["data"].dt.year == ano)]

    # 👇 AQUI ENTRA O df_exibir

    df_exibir = df_filtrado.copy()

    df_exibir["valor"] = df_exibir.apply(
        lambda row: valor_colorido(row["valor"], row["tipo"]), axis=1
    )

    # df_exibir["valor"] = df_exibir["valor"].apply(moeda_br)
    df_exibir["data"] = df_exibir["data"].dt.strftime("%d/%m/%Y")

    categorias_unicas = ["Todas"] + sorted(df_filtrado["categoria"].dropna().unique())

    categoria_filtro = st.selectbox("Filtrar por categoria", categorias_unicas)

    if categoria_filtro != "Todas":
        df_filtrado = df_filtrado[df_filtrado["categoria"] == categoria_filtro]

    # 👇 MOSTRA FORMATADO
    # st.dataframe(df_exibir, use_container_width=True)
    st.write(df_exibir.to_html(escape=False, index=False), unsafe_allow_html=True)
    # df_exibir = df_filtrado.copy()

    st.write("Linhas filtradas:", len(df_filtrado))
    # st.write(df_filtrado)
    receitas = df_filtrado[df_filtrado["tipo"] == "Receita"]["valor"].sum()
    despesas = df_filtrado[df_filtrado["tipo"] == "Despesa"]["valor"].sum()
    saldo = receitas - despesas

    st.markdown(
        f"""
    💰 Receitas: <span style='color:{cor_valor(receitas)}; font-size:20px'>
    {moeda_br(receitas)}
    </span>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
    💸 Despesas: <span style='color:{cor_valor(despesas)}; font-size:20px'>
    {moeda_br(despesas)}
    </span>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
    📊 Saldo: <span style='color:{cor_valor(saldo)}; font-size:22px; font-weight:bold'>
    {moeda_br(saldo)}
    </span>
    """,
        unsafe_allow_html=True,
    )

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
        despesas_df = df[df["tipo"] == "Despesa"]

        if not despesas_df.empty:
            resumo = despesas_df.groupby("categoria")["valor"].sum()

            chart = (
                alt.Chart(resumo.reset_index())
                .mark_bar(color="#6BAED6")  # azul suave
                .encode(x="categoria", y="valor")
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
        receitas = df[df["tipo"] == "Receita"]["valor"].sum()
        despesas = df[df["tipo"] == "Despesa"]["valor"].sum()
        saldo = receitas - despesas

        st.write(f"Saldo atual: R$ {saldo:,.2f}")

        if saldo >= meta:
            st.success("🎉 Meta atingida!")
        else:
            st.warning("Continue economizando!")
