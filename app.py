import streamlit as st
import sqlite3
import pandas as pd
import datetime

# --- CONFIGURAÇÃO DE ACESSO ---
SENHA_ACESSO = "1234" 

st.set_page_config(
    page_title="FamilyBank", 
    page_icon="💍", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- UI/UX AJUSTADA PARA MÁXIMO CONTRASTE ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;500;800&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Plus Jakarta Sans', sans-serif; 
        background-color: #0A0E14; 
        color: #FFFFFF !important; /* Força texto branco em tudo */
    }

    header, footer, #MainMenu {visibility: hidden;}
    .block-container {padding-top: 1.5rem; max-width: 600px; margin: auto;}

    /* Ajuste de métricas */
    div[data-testid="stMetricValue"] {
        color: #00FFA3 !important;
        font-weight: 800;
    }
    div[data-testid="stMetricLabel"] {
        color: #FFFFFF !important;
    }

    /* Cards de Gastos com Texto em Alto Contraste */
    .expense-card { 
        background: #141B26; 
        border-radius: 18px; 
        padding: 18px; 
        margin-bottom: 12px; 
        border: 1px solid #1E293B;
        border-left: 5px solid #FF3366; 
        color: #FFFFFF !important; /* Texto branco dentro do card */
    }
    
    .expense-card b { color: #FFFFFF !important; font-size: 16px; }
    .expense-card small { color: #94A3B8 !important; font-size: 12px; }

    .owner-tag { 
        font-size: 10px; 
        background: #00FFA3; 
        padding: 2px 8px; 
        border-radius: 10px; 
        color: #000000 !important; /* Texto preto no fundo verde para ler o nome */
        text-transform: uppercase; 
        font-weight: bold; 
    }
    
    /* Estilo das Abas */
    .stTabs [data-baseweb="tab-list"] { background-color: #141B26; border-radius: 20px; }
    .stTabs [aria-selected="true"] { background-color: #00FFA3 !important; color: #000000 !important; }
    
    /* Tabelas (Dataframe) - Forçar cores legíveis */
    .stDataFrame { background-color: #141B26; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("<h2 style='text-align: center; color: white;'>🔐 FamilyBank Access</h2>", unsafe_allow_html=True)
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

df_c = pd.read_sql("SELECT * FROM contas", conn)
df_i = pd.read_sql("SELECT * FROM investimentos", conn)

tab_dash, tab_lista, tab_novo = st.tabs(["⚡ PAINEL", "📑 EXTRATO", "💎 LANÇAR"])

with tab_dash:
    c1, c2 = st.columns(2)
    total_f = df_c[(df_c['responsavel'] == 'Fernanda') & (df_c['pago'] == 0)]['valor'].sum()
    total_j = df_c[(df_c['responsavel'] == 'Jonathan') & (df_c['pago'] == 0)]['valor'].sum()
    
    c1.metric("FERNANDA", f"R$ {total_f:,.2f}")
    c2.metric("JONATHAN", f"R$ {total_j:,.2f}")

    st.markdown("<br><h4 style='color: white;'>Próximas Contas</h4>", unsafe_allow_html=True)
    contas_p = df_c[df_c['pago'] == 0]
    if contas_p.empty:
        st.success("Tudo pago! ✨")
    else:
        for _, r in contas_p.iterrows():
            st.markdown(f"""
                <div class='expense-card'>
                    <div>
                        <span class='owner-tag'>{r['responsavel']}</span><br>
                        <b>{r['descricao']}</b><br>
                        <small>Vencimento: {r['vencimento']}</small>
                    </div>
                    <div style='color: #FF3366; font-weight: 800; font-size: 18px;'>R$ {r['valor']:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)

with tab_novo:
    with st.form("form_family", clear_on_submit=True):
        resp = st.selectbox("Responsável", ["Fernanda", "Jonathan"])
        desc = st.text_input("Descrição")
        val = st.number_input("Valor R$", min_value=0.0)
        dt = st.date_input("Vencimento")
        if st.form_submit_button("CONFIRMAR REGISTRO"):
            cursor.execute("INSERT INTO contas (descricao, valor, vencimento, responsavel) VALUES (?, ?, ?, ?)", 
                         (desc, val, dt.strftime("%d/%m"), resp))
            conn.commit()
            st.balloons()
            st.rerun()
