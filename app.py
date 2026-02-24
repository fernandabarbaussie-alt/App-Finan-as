import streamlit as st
import sqlite3
import pandas as pd
import datetime

# --- CONFIGURAÇÃO PREMIUM ---
st.set_page_config(page_title="Finanças Elite", page_icon="💎", layout="wide")

# --- CSS DE ALTA COSTURA (UI/UX) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
        background-color: #050505;
    }

    /* Remover barras e menus padrão */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {padding-top: 2rem;}

    /* Cards de KPI Estilizados */
    .kpi-card {
        background: linear-gradient(145deg, #1e1e1e, #141414);
        border: 1px solid #333;
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 10px 20px rgba(0,0,0,0.5);
    }

    /* Estilo das Abas Modernas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        justify-content: center;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        border-radius: 30px;
        background-color: #1a1a1a;
        color: #888;
        border: 1px solid #333;
        padding: 0 25px;
        transition: 0.3s;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        transform: scale(1.05);
    }

    /* Lista de Transações Neumórfica */
    .transaction-item {
        background: #111;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 12px;
        border: 1px solid #222;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGICA DE DADOS ---
conn = sqlite3.connect("financas.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS contas (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, valor REAL, vencimento TEXT, pago INTEGER DEFAULT 0)")
cursor.execute("CREATE TABLE IF NOT EXISTS investimentos (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, valor REAL, categoria TEXT)")
conn.commit()

# --- INTERFACE ---
st.markdown("<h1 style='text-align: center; color: white; letter-spacing: -1px;'>ELITE <span style='color: #888;'>FINANCE</span></h1>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Dashboard", "Carteira", "Lançar"])

with tab1:
    df_c = pd.read_sql("SELECT * FROM contas", conn)
    total_pendente = df_c[df_c['pago'] == 0]['valor'].sum()
    
    # KPIs com HTML para controle total
    col1, col2 = st.columns(2)
    col1.markdown(f"""<div class='kpi-card'><p style='color: #888; font-size: 14px;'>DEBITO PENDENTE</p><h2 style='color: white;'>R$ {total_pendente:,.2f}</h2></div>""", unsafe_allow_html=True)
    col2.markdown(f"""<div class='kpi-card'><p style='color: #888; font-size: 14px;'>PATRIMÔNIO</p><h2 style='color: #00ff88;'>R$ {pd.read_sql("SELECT SUM(valor) FROM investimentos", conn).iloc[0,0] or 0:,.2f}</h2></div>""", unsafe_allow_html=True)

    st.markdown("<br><h4 style='color: white;'>Próximos Vencimentos</h4>", unsafe_allow_html=True)
    for _, row in df_c[df_c['pago'] == 0].iterrows():
        st.markdown(f"""
            <div class='transaction-item'>
                <div>
                    <span style='color: white; font-weight: bold;'>{row['descricao']}</span><br>
                    <span style='color: #555; font-size: 12px;'>Vence {row['vencimento']}</span>
                </div>
                <div style='color: #ff4b4b; font-weight: bold;'>R$ {row['valor']:.2f}</div>
            </div>
        """, unsafe_allow_html=True)

with tab3:
    st.markdown("<div class='kpi-card'>", unsafe_allow_html=True)
    with st.form("add_pro", clear_on_submit=True):
        tipo = st.selectbox("Tipo", ["Conta", "Investimento"])
        desc = st.text_input("O que é?")
        vlr = st.number_input("Quanto?", min_value=0.0)
        dt = st.date_input("Data")
        if st.form_submit_button("REGISTRAR NA NUVEM"):
            if tipo == "Conta":
                cursor.execute("INSERT INTO contas (descricao, valor, vencimento) VALUES (?, ?, ?)", (desc, vlr, dt.strftime("%d/%m")))
            else:
                cursor.execute("INSERT INTO investimentos (descricao, valor, categoria) VALUES (?, ?, ?)", (desc, vlr, "Geral"))
            conn.commit()
            st.toast("Dados sincronizados com sucesso!", icon="☁️")
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

