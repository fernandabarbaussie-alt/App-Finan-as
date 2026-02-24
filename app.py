import streamlit as st
import sqlite3
import pandas as pd
import datetime
import io

# --- CONFIGURAÇÃO DE ACESSO ---
SENHA_ACESSO = "1234"  # Altere aqui a sua senha pessoal

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Elite Finance Private", page_icon="🔐", layout="wide")

# --- CSS PREMIUM ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;500;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #0A0E14; color: #E2E8F0; }
    header, footer, #MainMenu {visibility: hidden;}
    .stButton>button { background: linear-gradient(90deg, #00FFA3 0%, #00D1FF 100%); color: black; border-radius: 15px; font-weight: 800; }
    .expense-card { background: #141B26; border-radius: 18px; padding: 18px; margin-bottom: 12px; border-left: 5px solid #FF3366; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO DE LOGIN ---
def login():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        st.markdown("<h2 style='text-align: center;'>🔐 Acesso Restrito</h2>", unsafe_allow_html=True)
        senha = st.text_input("Digite sua chave de acesso", type="password")
        if st.button("Entrar"):
            if senha == SENHA_ACESSO:
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("Senha incorreta. Tente novamente.")
        st.stop() # Interrompe a execução do resto do app

# Executa o login antes de carregar o app
login()

# --- DAQUI PARA BAIXO O APP SÓ RODA SE ESTIVER AUTENTICADO ---

# --- BANCO DE DADOS ---
conn = sqlite3.connect("financas_elite.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS contas (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, valor REAL, vencimento TEXT, pago INTEGER DEFAULT 0)")
cursor.execute("CREATE TABLE IF NOT EXISTS investimentos (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, valor REAL, data TEXT, categoria TEXT)")
conn.commit()

# --- HEADER ---
st.markdown("<p style='text-align: center; color: #00FFA3; font-weight: 800; font-size: 26px;'>PRIVATE<span style='color: white;'>BANKING</span></p>", unsafe_allow_html=True)

# --- SISTEMA DE ALERTAS INTELIGENTES ---
df_c = pd.read_sql("SELECT * FROM contas", conn)
df_i = pd.read_sql("SELECT * FROM investimentos", conn)

hoje = datetime.date.today()
proximos_3_dias = [(hoje + datetime.timedelta(days=i)).strftime("%d/%m") for i in range(4)]

alertas = df_c[(df_c['vencimento'].isin(proximos_3_dias)) & (df_c['pago'] == 0)]

# --- ABAS ---
tab_dash, tab_lista, tab_novo, tab_config = st.tabs(["⚡ DASH", "📑 LISTA", "💎 NOVO", "⚙️ ADM"])

with tab_dash:
    c1, c2 = st.columns(2)
    pendente = df_c[df_c['pago'] == 0]['valor'].sum()
    investido = df_i['valor'].sum()
    c1.metric("A PAGAR", f"R$ {pendente:,.2f}")
    c2.metric("INVESTIDO", f"R$ {investido:,.2f}")

    if not alertas.empty:
        st.markdown("<p style='color: #FF3366; font-weight: bold;'>⚠️ ALERTAS DE VENCIMENTO</p>", unsafe_allow_html=True)
        for _, r in alertas.iterrows():
            status = "VENCE HOJE" if r['vencimento'] == hoje.strftime("%d/%m") else f"Vence em {r['vencimento']}"
            st.markdown(f"""
                <div class='expense-card'>
                    <div><b>{r['descricao']}</b><br><small>{status}</small></div>
                    <div style='color: #FF3366; font-weight: 800;'>R$ {r['valor']:.2f}</div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.success("Nenhum vencimento próximo. Tudo limpo! ✨")

with tab_novo:
    with st.form("add_v5", clear_on_submit=True):
        tipo = st.selectbox("Tipo", ["Conta", "Investimento"])
        desc = st.text_input("Descrição")
        val = st.number_input("Valor", min_value=0.0)
        dt = st.date_input("Vencimento", datetime.date.today())
        if st.form_submit_button("REGISTRAR"):
            if tipo == "Conta":
                cursor.execute("INSERT INTO contas (descricao, valor, vencimento) VALUES (?, ?, ?)", (desc, val, dt.strftime("%d/%m")))
            else:
                cursor.execute("INSERT INTO investimentos (descricao, valor, data, categoria) VALUES (?, ?, ?, ?)", (desc, val, dt.strftime("%d/%m"), "Geral"))
            conn.commit()
            st.rerun()

with tab_config:
    if st.button("Sair / Bloquear App"):
        st.session_state["autenticado"] = False
        st.rerun()
