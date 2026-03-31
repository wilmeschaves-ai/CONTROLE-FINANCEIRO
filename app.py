import streamlit as st
from banco import criar_tabelas
from auth import login, cadastrar
from banco import conectar, adicionar_coluna_feedback

import qrcode
from io import BytesIO


st.markdown(
    """
<style>

/* Forçar cursor de clique */
button, 
.stButton > button,
[data-baseweb="select"],
[data-baseweb="select"] * {
    cursor: pointer !important;
}

/* Inputs também */
input, textarea {
    cursor: text !important;
}

/* Selectbox dropdown */
ul, li {
    cursor: pointer !important;
}

</style>
""",
    unsafe_allow_html=True,
)


# ========GERAR QR CODE PIX========
import qrcode
from io import BytesIO
import streamlit as st


col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.image("logo.png", width=280)

st.markdown(
    "<h1 style='text-align:center;'>💰 Controle Financeiro</h1>", unsafe_allow_html=True
)


# =========================
# GERAR PIX (CÓDIGO COPIA E COLA)
# =========================
def crc16(payload):
    polinomio = 0x1021
    resultado = 0xFFFF

    for byte in payload.encode():
        resultado ^= byte << 8
        for _ in range(8):
            if resultado & 0x8000:
                resultado = (resultado << 1) ^ polinomio
            else:
                resultado <<= 1
            resultado &= 0xFFFF

    return format(resultado, "04X")


def gerar_payload_pix(chave, nome, cidade):
    nome = nome[:25]
    cidade = cidade[:15]

    payload = (
        "000201"
        "26"
        + f"{len('0014BR.GOV.BCB.PIX01' + f'{len(chave):02}{chave}'):02}"
        + "0014BR.GOV.BCB.PIX"
        + f"01{len(chave):02}{chave}"
        + "52040000"
        "5303986"
        "5802BR" + f"59{len(nome):02}{nome}" + f"60{len(cidade):02}{cidade}"
        "62070503***"
        "6304"
    )

    payload += crc16(payload)
    return payload


def gerar_qr_pix(payload):
    qr = qrcode.make(payload)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


# =========================
# EXIBIR NO APP
# =========================

payload = gerar_payload_pix(
    chave="wilmeschaves@gmail.com", nome="WILMES CHAVES", cidade="ARAPIRACA"
)

qr_img = gerar_qr_pix(payload)
st.divider()


st.markdown(
    "<h3 style='text-align:center;'>💖 Apoie este projeto</h3>", unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align:center;'>Escaneie o QR Code para contribuir 🙌</p>",
    unsafe_allow_html=True,
)

# CENTRALIZA O QR
col1, col2, col3 = st.columns([2, 1, 2])

with col2:
    st.image(qr_img, width=250)

# TEXTO ABAIXO CENTRALIZADO

st.markdown(
    "<p style='text-align:center; font-size:16px;'>Ou use a chave PIX:</p>",
    unsafe_allow_html=True,
)

st.markdown(
    "<p style='text-align:center; font-size:18px; font-weight:bold;'>wilmeschaves@gmail.com</p>",
    unsafe_allow_html=True,
)
# =================================


# 1️⃣ cria tabelas
criar_tabelas()


# 2️⃣ ajusta banco (ALTER TABLE)
# adicionar_coluna_tipo_usuario()
adicionar_coluna_feedback()

# SESSION
if "logado" not in st.session_state:
    st.session_state.logado = False

if "usuario_id" not in st.session_state:
    st.session_state.usuario_id = None

if "tipo_usuario" not in st.session_state:
    st.session_state.tipo_usuario = "usuario"


def tela_login():
    st.title("🔐 Login")

    user = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        result = login(user, senha)

        if result:
            st.session_state.logado = True
            st.session_state.usuario_id = result[0]
            st.session_state.tipo_usuario = result[1]
            st.rerun()
        else:
            st.error("Login inválido")


def tela_cadastro():
    st.title("🆕 Cadastro")

    user = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Cadastrar"):
        if cadastrar(user, senha):
            st.success("Usuário criado!")
        else:
            st.error("Usuário já existe")


# LOGIN FLOW
if not st.session_state.logado:
    opcao = st.radio("Escolha", ["Login", "Cadastrar"])

    if opcao == "Login":
        tela_login()
    else:
        tela_cadastro()

    st.stop()

if st.session_state.tipo_usuario == "usuario":

    st.divider()
    st.subheader("😊 Avalie o aplicativo")

    opcoes = {"😡 Ruim": "ruim", "🙂 Bom": "bom", "😄 Ótimo": "otimo"}

    escolha = st.radio("Sua experiência:", list(opcoes.keys()))

    if st.button("Enviar Avaliação"):

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE usuarios SET satisfacao = ? WHERE id = ?",
            (opcoes[escolha], st.session_state.usuario_id),
        )

        conn.commit()
        conn.close()

        st.success("Obrigado pelo feedback! 🙌")

# MENU
menu = ["Lançamentos", "Resumo", "Análise", "Metas"]

if st.session_state.tipo_usuario == "admin":
    menu.append("Admin")

escolha = st.sidebar.selectbox("Menu", menu)

if st.sidebar.button("Sair"):
    st.session_state.clear()
    st.rerun()
# ========================

# =================================
# ROTAS
if escolha == "Lançamentos":
    from pages.lancamentos import render

    render()

elif escolha == "Resumo":
    from pages.resumo import render

    render()

elif escolha == "Análise":
    from pages.analise import render

    render()

elif escolha == "Metas":
    from pages.metas import render

    render()

elif escolha == "Admin":
    from pages.admin import render

    render()
