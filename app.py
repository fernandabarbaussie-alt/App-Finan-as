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

# --- UI/UX COM A NOVA PALETA ---
# Primária: #1F3A93 | Secundária: #2ECC71 | Neutros: #F5F5F5, #4A4A4A | Destaque: #E67E22, #E74C3C
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Inter', sans-serif; 
        background-color: #F5F5F5; /* Cinza Claro */
        color: #4A4A4A; /* Cinza Escuro */
    }

    header, footer, #MainMenu {visibility: hidden;}
    .block-container {padding-top: 1.5rem; max-width: 600px; margin: auto;}

    /* Cartões de Métricas */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #DEDEDE;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    div[data-testid="stMetricValue"] {
        color: #1F3A93 !important; /* Azul Escuro */
        font-weight: 800;
    }

    /* Cards de Gastos */
    .expense-card { 
        background: #FFFFFF; 
        border-radius: 15px; 
        padding: 18px; 
        margin-bottom: 12px; 
        border: 1px solid #DEDEDE;
        border-left: 5px solid #E74C3C; /* Vermelho para pendente */
    }
    .expense-card b { color: #1F3A93 !important; font-size: 16px; }
    .expense-card small { color: #4A4A4A !important; }

    /* Tags e Abas */
    .owner-tag { 
        font-size: 10px; 
        background: #2ECC71; /* Verde */
        padding: 3px 10px; 
        border-radius: 20px; 
        color: #FFFFFF !important; 
        font-weight: bold; 
    }
    
    .stTabs [data-baseweb="tab-list"] { background-color: #1F3A93; border-radius: 12px; padding: 5px; }
    .stTabs [data-baseweb="tab"] { color: #FFFFFF; }
    .stTabs [aria-selected="true"] { background-color: #2ECC71 !important; color: #FFFFFF !important; border-radius: 8px; }

    /* Botão */
    .stButton>button { 
        background-color: #1F3A93; 
        color: white; 
        border-radius: 12px; 
        font-weight: bold; 
        height: 3.5rem;
        border: none;
    }
    .stButton>button:hover { background-color: #E67E22; color: white; } /* Laranja no Hover */
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("<h2 style='text-align: center; color: #1F3A93;'>💍 FamilyBank</h2>", unsafe_allow_html=True)
    senha = st.text_input("Senha de Acesso", type="password")
    if st.button("Entrar"):
        if senha == SENHA_ACESSO:
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.error("Chave incorreta.")
    st.stop()

# --- DB & LOGICA ---
conn = sqlite3.connect("financas_casal.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS contas (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, valor REAL, vencimento TEXT, pago INTEGER DEFAULT 0, responsavel TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS investimentos (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, valor REAL, data TEXT)")
conn.commit()

st.markdown("<h1 style='text-align: center; color: #1F3A93; margin-bottom: 0;'>Family<span style='color: #2ECC71;'>Bank</span></h1>", unsafe_allow_html=True)

df_c = pd.read_sql("SELECT * FROM contas", conn)
df_i = pd.read_sql("SELECT * FROM investimentos", conn)

tab1, tab2, tab3 = st.tabs(["⚡ PAINEL", "📑 EXTRATO", "➕ NOVO"])

with tab1:
    c1, c2 = st.columns(2)
    pend_f = df_c[(df_c['responsavel'] == 'Fernanda') & (df_c['pago'] == 0)]['valor'].sum()
    pend_j = df_c[(df_c['responsavel'] == 'Jonathan') & (df_c['pago'] == 0)]['valor'].sum()
    
    c1.metric("FERNANDA", f"R$ {pend_f:,.2f}")
    c2.metric("JONATHAN", f"R$ {pend_j:,.2f}")

    st.markdown("<br><h5 style='color: #4A4A4A;'>PENDÊNCIAS ATUAIS</h5>", unsafe_allow_html=True)
    contas_p = df_c[df_c['pago'] == 0]
    if contas_p.empty:
        st.success("Tudo em dia! ✨")
    else:
        for _, r in contas_p.iterrows():
            st.markdown(f"""
                <div class='expense-card'>
                    <div style='display: flex; justify-content: space-between; align-items: flex-start;'>
                        <div>
                            <span class='owner-tag'>{r['responsavel']}</span><br>
                            <b style='margin-top: 5px; display: inline-block;'>{r['descricao']}</b><br>
                            <small>Vencimento: {r['vencimento']}</small>
                        </div>
                        <div style='color: #E74C3C; font-weight: 800; font-size: 18px;'>R$ {r['valor']:,.2f}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

with tab3:
    with st.form("add_family", clear_on_submit=True):
        resp = st.selectbox("Quem?", ["Fernanda", "Jonathan"])
        desc = st.text_input("O que é?")
        val = st.number_input("Valor R$", min_value=0.0)
        dt = st.date_input("Vencimento", datetime.date.today())
        if st.form_submit_button("REGISTRAR GASTO"):
            cursor.execute("INSERT INTO contas (descricao, valor, vencimento, responsavel) VALUES (?, ?, ?, ?)", 
                         (desc, val, dt.strftime("%d/%m"), resp))
            conn.commit()
            st.balloons()
            st.rerun()
