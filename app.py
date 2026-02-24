import streamlit as st
import sqlite3
import pandas as pd
import datetime
import base64
from dateutil.relativedelta import relativedelta
import plotly.express as px
from fpdf import FPDF

# --- CONFIGURAÇÃO ---
SENHA_ACESSO = "1234" 
st.set_page_config(page_title="FamilyBank", page_icon="💍", layout="wide")

# --- UI/UX ALTO CONTRASTE (SEM VERDE) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; background-color: #FFFFFF !important; color: #000000 !important; }
    header, footer, #MainMenu {visibility: hidden;}
    .block-container {padding-top: 1rem; max-width: 600px; margin: auto;}
    .section-title { color: #001f3f; font-weight: 900; font-size: 24px; margin-top: 20px; border-bottom: 4px solid #001f3f; width: 100%; padding-bottom: 5px; margin-bottom: 15px;}
    .expense-card { background: #F9F9F9; border-radius: 10px; padding: 15px; margin-bottom: 8px; border: 2px solid #000000;}
    .card-desc { font-size: 18px; font-weight: 700; color: #000000; }
    .card-price { font-size: 20px; font-weight: 900; color: #D32F2F; }
    .stTabs [data-baseweb="tab-list"] { background-color: #001f3f; border-radius: 10px; padding: 5px; }
    .stTabs [data-baseweb="tab"] { color: #FFFFFF !important; font-weight: bold; }
    .stTabs [aria-selected="true"] { background-color: #334e68 !important; border-radius: 8px; }
    
    /* Botões Empilhados e Maiores */
    .stButton>button { 
        border: 2px solid #000000; 
        border-radius: 8px; 
        font-weight: 900; 
        height: 3.8rem; 
        background-color: #FFFFFF; 
        color: #000000; 
        box-shadow: 3px 3px 0px #000000; 
        width: 100%;
        margin-bottom: 10px; /* Espaço entre botões empilhados */
    }
    input, select { border: 2px solid #000000 !important; border-radius: 8px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if "autenticado" not in st.session_state: st.session_state["autenticado"] = False
if not st.session_state["autenticado"]:
    st.markdown("<h2 style='text-align: center; color: #001f3f; font-weight: 900;'>🔐 FamilyBank</h2>", unsafe_allow_html=True)
    senha = st.text_input("Senha", type="password")
    if st.button("ENTRAR NO PAINEL"):
        if senha == SENHA_ACESSO:
            st.session_state["autenticado"] = True
            st.rerun()
    st.stop()

# --- BANCO DE DADOS (v11) ---
conn = sqlite3.connect("familybank_v11.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS contas (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, categoria TEXT, valor REAL, vencimento TEXT, pago INTEGER DEFAULT 0, responsavel TEXT, data_pagamento TEXT, comprovante TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS investimentos (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, categoria TEXT, valor REAL, data TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS metas (id INTEGER PRIMARY KEY AUTOINCREMENT, objetivo TEXT, valor_alvo REAL, valor_atual REAL)")
conn.commit()

# --- CARGA DE DADOS ---
df_c = pd.read_sql("SELECT * FROM contas", conn)
df_i = pd.read_sql("SELECT * FROM investimentos", conn)
df_m = pd.read_sql("SELECT * FROM metas", conn)

hoje = datetime.date.today()
mes_atual = hoje.strftime("%m")
t_saidas_mes = df_c[(df_c['pago'] == 0) & (df_c['vencimento'].str.contains(f"/{mes_atual}"))]['valor'].sum()
t_investido = df_i['valor'].sum()

st.markdown("<h1 style='text-align: center; color: #001f3f; font-weight: 900; margin:0;'>FamilyBank</h1>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["⚡ PAINEL", "🎯 METAS", "📊 DASHBOARD", "📈 INVEST", "🔮 PROJEÇÃO", "➕ NOVO"])

with tab1:
    st.markdown(f"""<div style="background-color:#000;padding:15px;border-radius:12px;color:white;text-align:center;border:2px solid #001f3f;margin-bottom:10px;"><div style="display:flex;justify-content:space-around;"><div><small>A PAGAR</small><br><b style="font-size:22px;">R$ {t_saidas_mes:,.2f}</b></div><div style="border-left:1px solid #333;"></div><div><small>PATRIMÔNIO</small><br><b style="font-size:22px;color:#94a3b8;">R$ {t_investido:,.2f}</b></div></div></div>""", unsafe_allow_html=True)
    
    for resp in ["Fernanda", "Jonathan"]:
        st.markdown(f"<div class='section-title'>{resp.upper()}</div>", unsafe_allow_html=True)
        df_p = df_c[(df_c['responsavel'] == resp) & (df_c['pago'] == 0) & (df_c['vencimento'].str.contains(f"/{mes_atual}"))]
        
        if df_p.empty: 
            st.write("✓ Tudo em dia este mês.")
        else:
            for _, r in df_p.iterrows():
                st.markdown(f"""
                    <div class='expense-card'>
                        <div style='display:flex;justify-content:space-between;'>
                            <span class='card-desc'>{r['descricao']}</span>
                            <span class='card-price'>R$ {r['valor']:,.2f}</span>
                        </div>
                        <small>Vencimento: {r['vencimento']}</small>
                    </div>
                """, unsafe_allow_html=True)
                
                # BOTÕES EMPILHADOS PARA CELULAR
                comp = st.file_uploader("Comprovante", type=['png','jpg'], key=f"f_{r['id']}")
                
                if st.button("LIQUIDADO ✅", key=f"b_{r['id']}"):
                    img = base64.b64encode(comp.read()).decode() if comp else ""
                    cursor.execute("UPDATE contas SET pago = 1, data_pagamento = ?, comprovante = ? WHERE id = ?", (hoje.strftime("%d/%m/%Y"), img, r['id']))
                    conn.commit()
                    st.rerun()
                
                if st.button("REMOVER 🗑️", key=f"del_{r['id']}"):
                    cursor.execute("DELETE FROM contas WHERE id = ?", (r['id'],))
                    conn.commit()
                    st.rerun()
                
                st.markdown("---")

# ... (restante das abas mantido conforme v11) ...

