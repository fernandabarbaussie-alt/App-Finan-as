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
st.set_page_config(page_title="FamilyBank", page_icon="💎", layout="wide")

# --- UI/UX PREMIUM MODERNO ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #F4F7F9 !important; }
    header, footer, #MainMenu {visibility: hidden;}
    .block-container {padding: 1rem; max-width: 500px; margin: auto;}

    /* Resumo do Topo */
    .summary-card {
        background: linear-gradient(135deg, #001f3f 0%, #003366 100%);
        color: white; padding: 20px; border-radius: 20px;
        text-align: center; box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }

    /* Cards de Despesa Modernos */
    .expense-card-fernanda { border-left: 8px solid #E91E63; background: white; padding: 15px; border-radius: 15px; margin-bottom: 15px; shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .expense-card-jonathan { border-left: 8px solid #2196F3; background: white; padding: 15px; border-radius: 15px; margin-bottom: 15px; shadow: 0 4px 6px rgba(0,0,0,0.05); }
    
    .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
    .card-title { font-weight: 800; font-size: 18px; color: #333; }
    .card-price { font-weight: 800; font-size: 20px; color: #000; }
    .card-meta { color: #888; font-size: 13px; font-weight: 600; }

    /* Botões de Ação Rápida Estilizados */
    div.stButton > button {
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        height: 3.5rem !important;
        width: 100% !important;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Botão Liquidar - Estilo Sucesso */
    div[data-testid="stVerticalBlock"] > div:nth-child(3) button {
        background-color: #E3F2FD !important; color: #1976D2 !important;
        border: 1px solid #BBDEFB !important;
    }
    
    /* Botão Remover - Estilo Sutil */
    div[data-testid="stVerticalBlock"] > div:nth-child(4) button {
        background-color: #FFEBEE !important; color: #D32F2F !important;
        height: 2.5rem !important; font-size: 11px !important;
    }

    .stTabs [data-baseweb="tab-list"] { background-color: transparent; gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #E0E0E0; border-radius: 20px; 
        color: #666 !important; padding: 8px 16px; font-weight: 600;
    }
    .stTabs [aria-selected="true"] { background-color: #001f3f !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES AUXILIARES ---
def get_icon(categoria):
    icons = {"Mercado": "🛒", "Lazer": "🎡", "Saúde": "💊", "Fixas": "🏠", "Educação": "📚", "Outros": "📦"}
    return icons.get(categoria, "💰")

# --- BANCO DE DADOS ---
conn = sqlite3.connect("familybank_v21.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS contas (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, categoria TEXT, valor REAL, vencimento TEXT, pago INTEGER DEFAULT 0, responsavel TEXT, data_pagamento TEXT, comprovante TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS investimentos (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, categoria TEXT, valor REAL, data TEXT)")
conn.commit()

df_c = pd.read_sql("SELECT * FROM contas", conn)
df_i = pd.read_sql("SELECT * FROM investimentos", conn)
hoje = datetime.date.today()
mes_atual_str = hoje.strftime("/%m")

# --- CONTEÚDO ---
st.markdown("<h3 style='text-align: center; color: #001f3f; font-weight: 800; letter-spacing: -1px;'>FamilyBank 💎</h3>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["⚡ PAINEL", "📊 DASH", "🔮 PROJ.", "📑 HIST.", "➕ NOVO"])

with tab1:
    df_aberto = df_c[(df_c['pago'] == 0) & (df_c['vencimento'].str.contains(mes_atual_str, na=False))]
    t_mes = df_aberto['valor'].sum()
    
    st.markdown(f"""
        <div class="summary-card">
            <small style="opacity: 0.8; text-transform: uppercase; font-weight: 600;">Pendente em {hoje.strftime('%B')}</small>
            <div style="font-size: 32px; font-weight: 800;">R$ {t_mes:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)

    for resp in ["Fernanda", "Jonathan"]:
        st.markdown(f"<div style='font-weight:800; color:#555; margin-bottom:10px;'>{resp.upper()}</div>", unsafe_allow_html=True)
        df_resp = df_aberto[df_aberto['responsavel'] == resp]
        
        if df_resp.empty:
            st.info(f"Tudo pago para {resp}!")
        else:
            for _, r in df_resp.iterrows():
                classe = "expense-card-fernanda" if resp == "Fernanda" else "expense-card-jonathan"
                icon = get_icon(r['categoria'])
                
                st.markdown(f"""
                    <div class="{classe}">
                        <div class="card-header">
                            <span class="card-title">{icon} {r['descricao']}</span>
                            <span class="card-price">R$ {r['valor']:,.2f}</span>
                        </div>
                        <div class="card-meta">VENCIMENTO: {r['vencimento']}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                # AÇÕES RÁPIDAS
                comp = st.file_uploader("Anexar", type=['png','jpg','pdf'], key=f"u_{r['id']}", label_visibility="collapsed")
                
                if st.button(f"LIQUIDAR CONTA", key=f"liq_{r['id']}"):
                    img = base64.b64encode(comp.read()).decode() if comp else ""
                    cursor.execute("UPDATE contas SET pago = 1, data_pagamento = ?, comprovante = ? WHERE id = ?", (hoje.strftime("%d/%m/%Y"), img, r['id']))
                    conn.commit()
                    st.rerun()
                
                if st.button(f"REMOVER", key=f"del_{r['id']}"):
                    cursor.execute("DELETE FROM contas WHERE id = ?", (r['id'],))
                    conn.commit()
                    st.rerun()
                st.markdown("<br>", unsafe_allow_html=True)

with tab4: # HISTÓRICO COM VISUAL DE APP
    st.markdown("<div class='section-title'>Histórico</div>", unsafe_allow_html=True)
    df_h = df_c[df_c['pago'] == 1].sort_values('id', ascending=False)
    for _, h in df_h.iterrows():
        with st.expander(f"✅ {h['descricao']} - R$ {h['valor']:.2f}"):
            st.write(f"Pago por: {h['responsavel']}")
            if h['comprovante']: st.image(base64.b64decode(h['comprovante']))

with tab5: # NOVO REGISTRO
    with st.form("novo_v21"):
        st.markdown("<b>Novo Lançamento</b>", unsafe_allow_html=True)
        des = st.text_input("O que comprou?")
        cat = st.selectbox("Categoria", ["Mercado", "Lazer", "Fixas", "Saúde", "Educação", "Outros"])
        val = st.number_input("Valor", min_value=0.0)
        res = st.selectbox("Quem paga?", ["Fernanda", "Jonathan"])
        rep = st.number_input("Parcelas", min_value=1, value=1)
        dat = st.date_input("Data base")
        if st.form_submit_button("ADICIONAR"):
            for i in range(int(rep)):
                v_p = dat + relativedelta(months=i)
                d_p = f"{des} ({i})" if rep > 1 else des
                cursor.execute("INSERT INTO contas (descricao, categoria, valor, vencimento, responsavel) VALUES (?, ?, ?, ?, ?)", (d_p, cat, val, v_p.strftime("%d/%m"), res))
            conn.commit()
            st.rerun()
