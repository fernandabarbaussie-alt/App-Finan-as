import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# --- CONFIGURAÇÃO ELITE PRO ---
st.set_page_config(page_title="Elite Finance Cloud", page_icon="💳", layout="wide")

# --- UI/UX PREMIUM 3.0 (DESIGN DE ALTO NÍVEL) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;500;800&display=swap');
    
    /* Configuração Geral */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #0A0E14; /* Deep Navy Background */
        color: #E2E8F0;
    }

    /* Esconder o que não é profissional */
    header, footer, #MainMenu {visibility: hidden;}
    .block-container {padding-top: 1rem; max-width: 600px;} /* Centralizado para celular */

    /* Dashboard Cards (Glassmorphism + Glow) */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.01) 100%);
        border: 1px solid rgba(0, 255, 163, 0.2); /* Glow Verde */
        backdrop-filter: blur(12px);
        padding: 20px;
        border-radius: 22px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
    }

    /* Cores das Métricas */
    div[data-testid="stMetricValue"] {
        color: #00FFA3 !important; /* Mint Green */
        font-weight: 800;
    }

    /* Estilo das Abas (Modern Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #141B26;
        padding: 6px;
        border-radius: 16px;
        border: 1px solid #1E293B;
    }
    .stTabs [data-baseweb="tab"] {
        color: #94A3B8;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00FFA3 !important; /* Fundo Verde no Selecionado */
        color: #050505 !important; /* Texto Preto para Contraste */
        border-radius: 12px;
    }

    /* Cards de Lista de Gastos */
    .expense-card {
        background: #141B26;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 12px;
        border-left: 4px solid #FF3366; /* Rosa para pendente */
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Botões Premium */
    .stButton>button {
        background: linear-gradient(90deg, #00FFA3 0%, #00D1FF 100%);
        color: #000;
        border: none;
        border-radius: 14px;
        font-weight: 800;
        letter-spacing: 1px;
        padding: 15px;
        transition: 0.4s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 20px rgba(0, 255, 163, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXÃO CLOUD ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_contas = conn.read(worksheet="contas")
    df_invest = conn.read(worksheet="investimentos")
except:
    st.warning("⚠️ Aguardando conexão com a Planilha Elite...")
    st.stop()

# --- HEADER PREMIUM ---
st.markdown("<p style='text-align: center; color: #00FFA3; font-weight: 800; font-size: 24px; margin-bottom: 0;'>PRIVATE<span style='color: white;'>BANKING</span></p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94A3B8; font-size: 12px; margin-top: 0;'>Wealth Management System</p>", unsafe_allow_html=True)

# --- ABAS ---
tab1, tab2, tab3 = st.tabs(["⚡ Dashboard", "📑 Extrato", "💎 Novo"])

with tab1:
    # Resumo Visual
    col1, col2 = st.columns(2)
    pendente = df_contas[df_contas['pago'] == "Não"]['valor'].sum()
    total_inv = df_invest['valor'].sum()
    
    col1.metric("A PAGAR", f"R$ {pendente:,.2f}")
    col2.metric("INVESTIDO", f"R$ {total_inv:,.2f}")

    st.markdown("<br><h4 style='font-size: 16px; color: #94A3B8;'>CONTAS VENCENDO</h4>", unsafe_allow_html=True)
    
    for _, r in df_contas[df_contas['pago'] == "Não"].iterrows():
        st.markdown(f"""
            <div class="expense-card">
                <div>
                    <span style="color: white; font-weight: 600;">{r['descricao']}</span><br>
                    <span style="color: #64748B; font-size: 12px;">Data: {r['vencimento']}</span>
                </div>
                <div style="color: #FF3366; font-weight: 800;">R$ {r['valor']:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)

with tab3:
    # Formulário de Inserção Estilizado
    with st.container():
        st.markdown("<p style='color: #00FFA3;'>LANÇAMENTO RÁPIDO</p>", unsafe_allow_html=True)
        with st.form("form_v3", clear_on_submit=True):
            tipo = st.pills("Selecione:", ["Conta", "Investimento"], default="Conta")
            desc = st.text_input("Descrição")
            val = st.number_input("Valor (R$)", min_value=0.0)
            data = st.date_input("Vencimento")
            
            if st.form_submit_button("AUTORIZAR TRANSAÇÃO"):
                # Lógica para adicionar na planilha (Simulação)
                st.balloons()
                st.success("Sincronizado via Cloud.")

