import streamlit as st
import sqlite3
import pandas as pd
import datetime

# --- CONFIGURAÇÃO ELITE PRO ---
st.set_page_config(
    page_title="Elite Finance Pro", 
    page_icon="💳", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- UI/UX PREMIUM (CSS INJECTION) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;500;800&display=swap');
    
    /* Configuração Geral */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #0A0E14; 
        color: #E2E8F0;
    }

    /* Ocultar elementos padrão do Streamlit */
    header, footer, #MainMenu {visibility: hidden;}
    .block-container {padding-top: 1.5rem; max-width: 600px; margin: auto;}

    /* Cards de Resumo (Glow verde) */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.01) 100%);
        border: 1px solid rgba(0, 255, 163, 0.2);
        backdrop-filter: blur(15px);
        padding: 20px;
        border-radius: 24px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }

    /* Cores das Métricas */
    div[data-testid="stMetricValue"] {
        color: #00FFA3 !important;
        font-weight: 800;
        font-size: 1.8rem !important;
    }

    /* Estilo das Abas Modernas */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #141B26;
        padding: 8px;
        border-radius: 20px;
        border: 1px solid #1E293B;
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #94A3B8;
        font-weight: 500;
        border-radius: 15px;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00FFA3 !important;
        color: #050505 !important;
    }

    /* Card de Transação Estilizado */
    .expense-card {
        background: #141B26;
        border-radius: 18px;
        padding: 18px;
        margin-bottom: 12px;
        border: 1px solid #1E293B;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-left: 5px solid #FF3366; /* Rosa para pendente */
    }

    /* Botão Principal Estilo Apple */
    .stButton>button {
        background: linear-gradient(90deg, #00FFA3 0%, #00D1FF 100%);
        color: #000;
        border: none;
        border-radius: 16px;
        font-weight: 800;
        height: 3.8rem;
        width: 100%;
        transition: 0.3s;
        box-shadow: 0 4px 15px rgba(0, 255, 163, 0.2);
    }
    .stButton>button:active {
        transform: scale(0.98);
    }
    </style>
    """, unsafe_allow_html=True)

# --- BANCO DE DADOS LOCAL (SQLite) ---
conn = sqlite3.connect("financas_elite.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS contas (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, valor REAL, vencimento TEXT, pago INTEGER DEFAULT 0)")
cursor.execute("CREATE TABLE IF NOT EXISTS investimentos (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, valor REAL, data TEXT, categoria TEXT)")
conn.commit()

# --- HEADER PREMIUM ---
st.markdown("<p style='text-align: center; color: #00FFA3; font-weight: 800; font-size: 26px; margin-bottom: 0;'>PRIVATE<span style='color: white;'>BANKING</span></p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94A3B8; font-size: 13px; margin-top: 0; letter-spacing: 2px;'>ULTRA-PREMIUM SYSTEM</p>", unsafe_allow_html=True)

# --- NAVEGAÇÃO POR ABAS ---
tab_dash, tab_lista, tab_novo = st.tabs(["⚡ DASHBOARD", "📑 LISTA", "💎 NOVO"])

# --- CARREGAR DADOS ---
df_c = pd.read_sql("SELECT * FROM contas", conn)
df_i = pd.read_sql("SELECT * FROM investimentos", conn)

with tab_dash:
    # Métricas de Impacto
    c1, c2 = st.columns(2)
    pendente = df_c[df_c['pago'] == 0]['valor'].sum()
    investido = df_i['valor'].sum()
    
    c1.metric("PENDENTE", f"R$ {pendente:,.2f}")
    c2.metric("PATRIMÔNIO", f"R$ {investido:,.2f}")

    st.markdown("<br><p style='color: #94A3B8; font-weight: 600; font-size: 14px;'>PRÓXIMOS VENCIMENTOS</p>", unsafe_allow_html=True)
    
    # Filtrar apenas as pendentes
    contas_pendentes = df_c[df_c['pago'] == 0]
    if contas_pendentes.empty:
        st.success("Tudo pago! Você está no controle. ✨")
    else:
        for _, r in contas_pendentes.iterrows():
            st.markdown(f"""
                <div class="expense-card">
                    <div>
                        <span style="color: white; font-weight: 600; font-size: 16px;">{r['descricao']}</span><br>
                        <span style="color: #64748B; font-size: 12px;">Data: {r['vencimento']}</span>
                    </div>
                    <div style="color: #FF3366; font-weight: 800; font-size: 18px;">R$ {r['valor']:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)

with tab_lista:
    st.markdown("### Histórico de Contas")
    if not df_c.empty:
        # Tabela simplificada e moderna
        st.dataframe(df_c[['descricao', 'valor', 'vencimento', 'pago']], use_container_width=True, hide_index=True)
        if st.button("Limpar Banco de Dados (CUIDADO)"):
            cursor.execute("DELETE FROM contas")
            conn.commit()
            st.rerun()
    else:
        st.info("Nenhum dado registrado.")

with tab_novo:
    st.markdown("<p style='color: #00FFA3; font-weight: 700;'>LANÇAMENTO INTELIGENTE</p>", unsafe_allow_html=True)
    
    with st.container():
        with st.form("form_v3", clear_on_submit=True):
            tipo = st.selectbox("O que deseja registrar?", ["Conta", "Investimento"])
            desc = st.text_input("Descrição (Ex: Aluguel, Ações...)")
            val = st.number_input("Valor (R$)", min_value=0.0, step=10.0)
            data = st.date_input("Data do Registro", datetime.date.today())
            
            if st.form_submit_button("AUTORIZAR REGISTRO"):
                if tipo == "Conta":
                    cursor.execute("INSERT INTO contas (descricao, valor, vencimento) VALUES (?, ?, ?)", 
                                 (desc, val, data.strftime("%d/%m")))
                else:
                    cursor.execute("INSERT INTO investimentos (descricao, valor, data, categoria) VALUES (?, ?, ?, ?)", 
                                 (desc, val, data.strftime("%d/%m"), "Geral"))
                conn.commit()
                st.balloons()
                st.success("Sincronizado localmente!")
                st.rerun()

# --- RODAPÉ ---
st.markdown("<p style='text-align: center; color: #334155; font-size: 10px; margin-top: 50px;'>ELITE FINANCE V4.0 | SECURE LOCAL STORAGE</p>", unsafe_allow_html=True)

