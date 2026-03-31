import streamlit as st
import pandas as pd
from datetime import datetime
import io
import calendar
import altair as alt

import sqlite3
from banco import conectar, criar_tabelas


def adicionar_coluna_tipo_usuario():
    cursor.execute("PRAGMA table_info(usuarios)")
    colunas = [col[1] for col in cursor.fetchall()]

    if "tipo" not in colunas:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN tipo TEXT DEFAULT 'usuario'")
        conn.commit()


# 🔗 conexão primeiro
conn = sqlite3.connect("financeiro.db", check_same_thread=False)
cursor = conn.cursor()

# 📦 depois cria tabelas
criar_tabelas()


# 🛠️ função
def adicionar_coluna_tipo_usuario():
    cursor.execute("PRAGMA table_info(usuarios)")
    colunas = [col[1] for col in cursor.fetchall()]

    if "tipo" not in colunas:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN tipo TEXT DEFAULT 'usuario'")
        conn.commit()


# 🚀 agora sim pode chamar
adicionar_coluna_tipo_usuario()


conn = sqlite3.connect("financeiro.db", check_same_thread=False)
cursor = conn.cursor()
criar_tabelas()
adicionar_coluna_tipo_usuario()

# =========================
# MENU
# =========================


# SESSION STATE


if "usuario_id" not in st.session_state:
    st.session_state.usuario_id = None

if "tipo_usuario" not in st.session_state:
    st.session_state.tipo_usuario = "usuario"


def tela_cadastro():
    st.title("🆕 Criar Conta")

    novo_usuario = st.text_input("Novo usuário")
    nova_senha = st.text_input("Nova senha", type="password")

    if st.button("Cadastrar", key="cadastrar"):
        if not novo_usuario or not nova_senha:
            st.warning("Preencha todos os campos")
            return

        # verifica se já existe
        cursor.execute("SELECT id FROM usuarios WHERE usuario=?", (novo_usuario,))
        if cursor.fetchone():
            st.error("Usuário já existe")
            return

        cursor.execute(
            "INSERT INTO usuarios (usuario, senha, tipo) VALUES (?, ?, ?)",
            (novo_usuario, nova_senha, "usuario"),
        )
        conn.commit()

        st.success("✅ Usuário criado com sucesso!")


def tela_login():
    st.title("🔐 Login")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar", key="entrar"):
        cursor.execute(
            "SELECT id, tipo FROM usuarios WHERE usuario=? AND senha=?",
            (usuario, senha),
        )
        result = cursor.fetchone()

        if result:
            st.session_state.logado = True
            st.session_state.usuario_id = result[0]
            st.session_state.tipo_usuario = result[1]  # 👈 AQUI
            st.rerun()
        else:
            st.error("Login inválido")


def init_state():
    defaults = {
        "logado": False,
        "usuario_id": None,
        "tipo_usuario": "usuario",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()

if not st.session_state.logado:

    opcao = st.radio("Escolha", ["Login", "Cadastrar"])

    if opcao == "Login":
        tela_login()
    else:
        tela_cadastro()

    st.stop()
menu_opcoes = ["Lançamentos", "Resumo", "Análise", "Metas"]

if st.session_state.tipo_usuario == "admin":
    menu_opcoes.append("Admin")

menu = st.selectbox("📌 Navegação", menu_opcoes)
if st.session_state.logado:
    if st.button("🚪 Sair"):
        st.session_state.clear()
        st.rerun()


def adicionar_coluna_se_nao_existir():
    cursor.execute("PRAGMA table_info(lancamentos)")
    colunas = [col[1] for col in cursor.fetchall()]

    if "forma_pagamento" not in colunas:
        cursor.execute("ALTER TABLE lancamentos ADD COLUMN forma_pagamento TEXT")
        conn.commit()


adicionar_coluna_se_nao_existir()


# -----------------------
# SESSION
# -----------------------
def salvar_lancamento(data, tipo, categoria, descricao, valor, forma_pagamento):
    cursor.execute(
        """
        INSERT INTO lancamentos (
            usuario_id, data, tipo, categoria, descricao, valor, forma_pagamento
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (
            st.session_state.usuario_id,
            data,
            tipo,
            categoria,
            descricao,
            valor,
            forma_pagamento,
        ),
    )
    conn.commit()


def atualizar_lancamento(
    id_lancamento, data, tipo, categoria, descricao, valor, forma_pagamento
):
    cursor.execute(
        """
        UPDATE lancamentos
        SET data = ?,
            tipo = ?,
            categoria = ?,
            descricao = ?,
            valor = ?,
            forma_pagamento = ?
        WHERE id = ? AND usuario_id = ?
    """,
        (
            data,
            tipo,
            categoria,
            descricao,
            valor,
            forma_pagamento,
            id_lancamento,
            st.session_state.usuario_id,
        ),
    )

    conn.commit()


# 👇 COLOQUE AQUI
def excluir_lancamento(id_lancamento):
    cursor.execute(
        "DELETE FROM lancamentos WHERE id = ? AND usuario_id = ?",
        (id_lancamento, st.session_state.usuario_id),
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
    return f" {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


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


def card(titulo, valor, cor):
    return f"""
    <div style="
        background: linear-gradient(135deg, #1f2937, #111827);
        padding:20px;
        border-radius:15px;
        text-align:center;
        box-shadow: 0px 6px 15px rgba(0,0,0,0.4);
    ">
        <h4 style="color:#9ca3af;">{titulo}</h4>
        <h2 style="color:{cor}; margin-top:10px;">{valor}</h2>
    </div>
    """


# =========================
# CONFIG
# =========================

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.image("logo.png", width=180)

st.markdown(
    "<h1 style='text-align:center;'>💰 Controle Financeiro</h1>", unsafe_allow_html=True
)


df = carregar_dados()

if not df.empty:
    df["data"] = pd.to_datetime(df["data"])


# =========================
# MENU
# =========================


menu_opcoes = ["Lançamentos", "Resumo", "Análise", "Metas"]

if st.session_state.tipo_usuario == "admin":
    menu_opcoes.append("Admin")


# =========================
# LANÇAMENTOS
# =========================

categorias = {
    "Receita": ["Salário", "Extra", "Empréstimo", "Outros"],
    "Despesa": [
        "Aluguel",
        "Luz",
        "Água",
        "Internet",
        "Mercado",
        "Transporte",
        "Lazer",
        "Saúde",
        "Educação",
        "Empréstimos",
        "Dízimo",
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

        forma_pagamento = None
        if tipo == "Despesa" or tipo == "Receita":
            forma_pagamento = st.selectbox(
                "Forma de pagamento/Recebimento",
                [
                    "Dinheiro",
                    "Pix",
                    "Cartão de Débito",
                    "Cartão de Crédito",
                    "Crédito em Conta",
                    "Empréstimos",
                ],
            )

        # 👇 BOTÃO FORA DAS COLUNAS
        st.divider()

    if st.button("💾 Salvar"):
        salvar_lancamento(
            data.strftime("%Y-%m-%d"),
            tipo,
            categoria,
            descricao,
            valor,
            forma_pagamento,
        )

        st.success("✅ Lançamento salvo!")
        st.rerun()

    st.subheader("📋 Histórico")

    if not df.empty:
        df_exibir = df.copy()
        df_exibir["data"] = df_exibir["data"].dt.strftime("%d/%m/%Y")

        st.dataframe(df_exibir, use_container_width=True)

        # ---------------
        st.divider()
        st.subheader("🗑️ Excluir Lançamento")

        st.write("Selecione o lançamento para excluir:")

        df_exibir["label"] = df_exibir.apply(
            lambda row: f"{row['data']} | {row['categoria']} | {row['valor']:.2f}",
            axis=1,
        )

        selecao = st.selectbox(
            "Escolha o lançamento",
            df_exibir["id"],
            format_func=lambda x: df_exibir[df_exibir["id"] == x]["label"].values[0],
        )

        if st.button("Excluir"):
            excluir_lancamento(selecao)
            st.success("✅ Lançamento excluído!")
            st.rerun()

        # =======================================
        st.subheader("✏️ Editar Lançamento")

        if not df.empty:

            df_edit = df.copy()

            df_edit["label"] = df_edit.apply(
                lambda row: f"{row['data'].strftime('%d/%m/%Y')} | {row['categoria']} | R$ {row['valor']:.2f}",
                axis=1,
            )

            lancamento_id = st.selectbox(
                "Selecione o lançamento",
                df_edit["id"],
                format_func=lambda x: df_edit[df_edit["id"] == x]["label"].values[0],
            )

            lancamento = df_edit[df_edit["id"] == lancamento_id].iloc[0]

            col1, col2 = st.columns(2)

            with col1:
                nova_data = st.text_input(
                    "Data", lancamento["data"].strftime("%d/%m/%Y")
                )

                novo_tipo = st.selectbox(
                    "Tipo",
                    ["Receita", "Despesa"],
                    index=0 if lancamento["tipo"] == "Receita" else 1,
                )

                nova_categoria = st.selectbox(
                    "Categoria",
                    categorias[novo_tipo],
                    index=(
                        categorias[novo_tipo].index(lancamento["categoria"])
                        if lancamento["categoria"] in categorias[novo_tipo]
                        else 0
                    ),
                )

            with col2:
                novo_valor = st.number_input("Valor", value=float(lancamento["valor"]))

                nova_descricao = st.text_input("Descrição", lancamento["descricao"])
                # ==================================
                opcoes_pagamento = [
                    "Dinheiro",
                    "Pix",
                    "Cartão de Débito",
                    "Cartão de Crédito",
                    "Crédito em Conta",
                ]

                valor_atual = lancamento["forma_pagamento"]

                # garante valor válido mesmo se for None ou vazio
                if valor_atual not in opcoes_pagamento:
                    valor_atual = opcoes_pagamento[0]

                nova_forma = st.selectbox(
                    "Forma de pagamento",
                    opcoes_pagamento,
                    index=opcoes_pagamento.index(valor_atual),
                )
                # =======================================
                if st.button("💾 Atualizar Lançamento"):

                    try:
                        data_convertida = pd.to_datetime(nova_data, dayfirst=True)
                        data_final = data_convertida.strftime("%Y-%m-%d")

                        atualizar_lancamento(
                            lancamento_id,
                            data_final,
                            novo_tipo,
                            nova_categoria,
                            nova_descricao,
                            novo_valor,
                            nova_forma,
                        )

                        st.success("✅ Lançamento atualizado com sucesso!")
                        st.rerun()

                    except:
                        st.error("❌ Data inválida! Use DD/MM/AAAA")
                # =======================================


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

    df_filtrado = df[(df["data"].dt.month == mes_num) & (df["data"].dt.year == ano)]
    df_filtrado = df_filtrado.copy()
    categorias_unicas = ["Todas"] + sorted(df_filtrado["categoria"].dropna().unique())
    categoria_filtro = st.selectbox("Filtrar por categoria", categorias_unicas)

    # 👇 AQUI ENTRA O df_exibir

    # df_exibir = df_filtrado.copy()

    if categoria_filtro != "Todas":
        df_filtrado = df_filtrado[df_filtrado["categoria"] == categoria_filtro]

    df_exibir = df_filtrado.copy()

    df_exibir["valor"] = df_exibir.apply(
        lambda row: valor_colorido(row["valor"], row["tipo"]), axis=1
    )

    df_exibir["data"] = df_exibir["data"].dt.strftime("%d/%m/%Y")

    # 👇 MOSTRA FORMATADO
    st.write(df_exibir.to_html(escape=False, index=False), unsafe_allow_html=True)

    st.write("Linhas filtradas:", len(df_filtrado))
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
elif menu == "Admin":

    st.subheader("👑 Painel Administrativo")

    # LISTAR USUÁRIOS
    st.write("### 👥 Usuários cadastrados")

    df_users = pd.read_sql_query("SELECT id, usuario, tipo FROM usuarios", conn)
    st.dataframe(df_users, use_container_width=True)

    st.divider()

    # ALTERAR TIPO DE USUÁRIO
    st.write("### 🔄 Alterar nível de acesso")

    user_id = st.selectbox(
        "Selecione o usuário",
        df_users["id"],
        format_func=lambda x: df_users[df_users["id"] == x]["usuario"].values[0],
    )

    novo_tipo = st.selectbox("Tipo", ["usuario", "admin"])

    if st.button("Atualizar Permissão"):
        cursor.execute(
            "UPDATE usuarios SET tipo = ? WHERE id = ?",
            (novo_tipo, user_id),
        )
        conn.commit()

        st.success("✅ Permissão atualizada!")
        st.rerun()
