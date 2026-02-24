import streamlit as st
import sqlite3
import pandas as pd
import datetime
import base64
from dateutil.relativedelta import relativedelta
import plotly.express as px

# --- CONFIGURAÇÃO ---
SENHA_ACESSO = "1234" 
st.set_page_config(page_title="FamilyBank", page_icon="💍", layout="wide")

# --- UI/UX FOCO TOTAL EM CELULAR (VERTICAL) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; background-color: #FFFFFF !important; color: #000000 !important; }
    header, footer, #MainMenu {visibility: hidden;}
    .block-container {padding: 1rem; max-width: 500px; margin: auto;}
    .section-title { color: #001f3f; font-weight: 900; font-size: 22px; margin-top: 15px; border-bottom: 3px solid #001f3f; padding-bottom: 5px;}
    .expense-card { background: #F9F9F9; border-radius: 10px; padding: 15px; margin-bottom: 5px; border: 2px solid #000000;}
    .card-price { font-size: 20px; font-weight: 900; color: #D32F2F; }
    
    /* BOTÕES VERTICAIS (UM ABAIXO DO OUTRO) */
    .stButton>button { 
        border: 2px solid #000000; 
        border-radius: 8px; 
        font-weight: 900; 
        height: 3.5rem; 
        background-color: #FFFFFF; 
        color: #000000; 
        box-shadow: 3px 3px 0px #000000; 
        width: 100% !important; 
        display: block;
        margin-bottom: 10px !important;
    }
    .stTabs [data-baseweb="tab-list"] { background-color: #001f3f; border-radius: 10px; padding: 5px; width: 100%;}
    .stTabs [data-baseweb="tab"] { color: #FFFFFF !important; font-size: 12px;}
    </style>
    """, unsafe_allow_html=True)

# --- BANCO DE DADOS (v12) ---
conn = sqlite3.connect("familybank_v12.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS contas (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, categoria TEXT, valor REAL, vencimento TEXT, pago INTEGER DEFAULT 0, responsavel TEXT, data_pagamento TEXT, comprovante TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS investimentos (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, categoria TEXT, valor REAL, data TEXT)")
conn.commit()

# --- DADOS ---
df_c = pd.read_sql("SELECT * FROM contas", conn)
df_i = pd.read_sql("SELECT * FROM investimentos", conn)
hoje = datetime.date.today()
mes_atual = hoje.strftime("%m")

st.markdown("<h1 style='text-align: center; color: #001f3f; font-weight: 900; margin:0;'>FamilyBank</h1>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["⚡ PAINEL", "📊 DASH", "📈 INVEST", "🔮 PROJ.", "➕ NOVO"])

with tab1:
    t_mes = df_c[(df_c['pago'] == 0) & (df_c['vencimento'].str.contains(f"/{mes_atual}"))]['valor'].sum()
    st.markdown(f"<div style='background:#000;color:#fff;padding:10px;border-radius:10px;text-align:center;'><b>PENDENTE NO MÊS</b><br><span style='font-size:20px;'>R$ {t_mes:,.2f}</span></div>", unsafe_allow_html=True)

    for resp in ["Fernanda", "Jonathan"]:
        st.markdown(f"<div class='section-title'>{resp.upper()}</div>", unsafe_allow_html=True)
        # SÓ MOSTRA O MÊS ATUAL NO PAINEL
        df_p = df_c[(df_c['responsavel'] == resp) & (df_c['pago'] == 0) & (df_c['vencimento'].str.contains(f"/{mes_atual}"))]
        
        if df_p.empty: st.write("✓ Tudo em dia.")
        else:
            for _, r in df_p.iterrows():
                st.markdown(f"<div class='expense-card'><b>{r['descricao']}</b><br><span class='card-price'>R$ {r['valor']:,.2f}</span><br><small>Venc: {r['vencimento']}</small></div>", unsafe_allow_html=True)
                
                # COMPROVANTE E BOTÕES UM ABAIXO DO OUTRO
                comp = st.file_uploader("Subir Comprovante", type=['png','jpg'], key=f"f_{r['id']}")
                
                if st.button("LIQUIDADO ✅", key=f"b_{r['id']}"):
                    img = base64.b64encode(comp.read()).decode() if comp else ""
                    cursor.execute("UPDATE contas SET pago = 1, data_pagamento = ?, comprovante = ? WHERE id = ?", (hoje.strftime("%d/%m/%Y"), img, r['id']))
                    conn.commit()
                    st.rerun()
                
                if st.button("REMOVER 🗑️", key=f"del_{r['id']}"):
                    cursor.execute("DELETE FROM contas WHERE id = ?", (r['id'],))
                    conn.commit()
                    st.rerun()

with tab4:
    st.markdown("<div class='section-title'>PROJEÇÃO (PARCELAS)</div>", unsafe_allow_html=True)
    for i in range(1, 7):
        data_f = hoje + relativedelta(months=i)
        mes_f = data_f.strftime("%m")
        df_futuro = df_c[(df_c['pago'] == 0) & (df_c['vencimento'].str.contains(f"/{mes_f}"))]
        if not df_futuro.empty:
            with st.expander(f"📅 {data_f.strftime('%B/%Y').upper()}"):
                for _, fut in df_futuro.iterrows():
                    st.write(f"{fut['descricao']} - R$ {fut['valor']:.2f}")

with tab5:
    with st.form("add_v12", clear_on_submit=True):
        tipo = st.radio("Tipo", ["Saída", "Investimento"], horizontal=True)
        des = st.text_input("Descrição")
        val = st.number_input("Valor")
        dat = st.date_input("Data de Vencimento")
        res = st.selectbox("Quem?", ["Fernanda", "Jonathan"])
        rep = st.number_input("Repetir (Parcelas)", min_value=1, value=1)
        if st.form_submit_button("REGISTRAR"):
            if tipo == "Saída":
                for i in range(int(rep)):
                    v_p = dat + relativedelta(months=i) # MANTÉM O DIA
                    # PARCELA INICIANDO EM (0)
                    d_parc = f"{des} ({i})" if rep > 1 else des
                    cursor.execute("INSERT INTO contas (descricao, valor, vencimento, responsavel) VALUES (?, ?, ?, ?)", (d_parc, val, v_p.strftime("%d/%m"), res))
            conn.commit()
            st.rerun()

