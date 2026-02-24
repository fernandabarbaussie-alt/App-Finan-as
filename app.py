import streamlit as st
import sqlite3
import pandas as pd
import datetime

# --- CONFIGURAÇÃO DE ACESSO ---
SENHA_ACESSO = "1234" 

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="FamilyBank", 
    page_icon="💍", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- UI/UX PREMIUM ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;500;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #0A0E14; color: #E2E8F0; }
    header, footer, #MainMenu {visibility: hidden;}
    .stButton>button { background: linear-gradient(90deg, #00FFA3 0%, #00D1FF 100%); color: black; border-radius: 15px; font-weight: 800; border:none; height: 3.5rem; width: 100%;}
    .expense-card { background: #141B26; border-radius: 18px; padding: 18px; margin-bottom: 12px; border-left: 5px solid #FF3366; }
    .owner-tag { font-size: 10px; background: #1E293B; padding: 2px 8px; border-radius: 10px; color: #00FFA3; text-transform: uppercase; font-weight: bold; }
    
    .stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; background-color: #141B26; padding: 8px; border-radius: 20px; }
    .stTabs [aria-selected="true"] { background-color: #00FFA3 !important; color: #050505 !important; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO DE LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("<h2 style='text-align: center; margin-top: 50px;'>🔐 FamilyBank Access</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        senha = st.text_input("Chave da Família", type="password")
        if st.button("Acessar Painel"):
            if senha == SENHA_ACESSO:
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("Chave incorreta.")
    st.stop()

# --- BANCO DE DADOS ---
conn = sqlite3.connect("financas_casal.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS contas (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, valor REAL, vencimento TEXT, pago INTEGER DEFAULT 0, responsavel TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS investimentos (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, valor REAL, data TEXT)")
conn.commit()

# --- HEADER ---
st.markdown("<p style='text-align: center; color: #00FFA3; font-weight: 800; font-size: 26px; margin-bottom:0;'>FAMILY<span style='color: white;'>BANK</span></p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94A3B8; font-size: 11px; letter-spacing: 2px; margin-top:0;'>FERNANDA & JONATHAN</p>", unsafe_allow_html=True)

# --- DADOS ---
df_c = pd.read_sql("SELECT * FROM contas", conn)
df_i = pd.read_sql("SELECT * FROM investimentos", conn)

tab_dash, tab_lista, tab_novo, tab_config = st.tabs(["⚡ PAINEL", "📑 EXTRATO", "💎 LANÇAR", "⚙️ ADM"])

with tab_dash:
    c1,
