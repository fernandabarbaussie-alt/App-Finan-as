import streamlit as st
import sqlite3
import pandas as pd
import datetime

# --- CONFIGURAÇÃO ---
SENHA_ACESSO = "1234" 

st.set_page_config(page_title="FamilyBank", page_icon="💍", layout="wide")

# --- UI/UX COM PALETA CORPORATIVA ---
# Primária: #1F3A93 | Secundária: #2ECC71 | Neutros: #F5F5F5, #4A4A4A | Destaque: #E67E22, #E74C3C
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #F5F5F5; color: #4A4A4A; }
    header, footer, #MainMenu {visibility: hidden;}
    .block-container {padding-top: 1rem; max-width: 600px; margin: auto;}

    /* Métricas */
    div[data-testid="stMetric"] { background-color: #FFFFFF; border: 1px solid #DEDEDE; border-radius: 15px; padding: 15px; }
    div[data-testid="stMetricValue"] { color: #1F3A93 !important; }

    /* Card de Gasto */
    .expense-card { 
        background: #FFFFFF; border-radius: 15px; padding: 15px; margin-bottom: 10px; 
        border: 1px solid #DEDEDE; border-left: 5px solid #E74C3C; 
    }
    .card-pago { border-left: 5px solid #2ECC71 !important; opacity: 0.8; }
    
    .owner-tag { 
        font-size: 10px; background: #2ECC71; padding: 2px 8px; 
        border-radius: 10px; color: #FFFFFF !important; font-weight: bold; 
    }
    
    /* Abas e Botões */
    .stTabs [data-baseweb="tab-list"] { background-color: #1F3A93; border-radius: 12px; }
    .stTabs [data-baseweb="tab"] { color: #FFFFFF; }
    .stTabs [aria-selected="true"] { background-color: #2ECC71 !important; }

    .stButton>button { border-radius: 10px; font-weight: bold; }
    .btn-pago>div>button { background-color: #2ECC71; color: white; border: none; }
    .btn-excluir>div>button { background-color: #E74C3C; color: white; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if "autenticado" not in st.session_state: st.session_state["autenticado"] = False
if not st.session_state["autenticado"]:
    st.markdown("<h2 style='text-align: center; color: #1F3A93;'>💍 FamilyBank</h2>", unsafe_allow_html=True)
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if senha == SENHA_ACESSO:
            st.session_state["autenticado"] = True
            st.rerun()
    st.stop()

# --- DB ---
conn = sqlite3.connect("financas_casal.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS contas (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, valor REAL, vencimento TEXT, pago INTEGER DEFAULT 0, responsavel TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS investimentos (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, valor REAL, data TEXT)")
conn.commit()

st.markdown("<h1 style='text-align: center; color: #1F3A93; margin-bottom: 0;'>Family<span style='color: #2ECC71;'>Bank</span></h1>", unsafe_allow_html=True)

# --- FUNÇÕES ---
def alterar_status(id_conta, novo_status):
    cursor.execute("UPDATE contas SET pago = ? WHERE id = ?", (novo_status, id_conta))
    conn.commit()
    st.rerun()

def excluir_conta(id_conta):
    cursor.execute("DELETE FROM contas WHERE id = ?", (id_conta,))
    conn.commit()
    st.rerun()

# --- CARGA ---
df_c = pd.read_sql("SELECT * FROM contas ORDER BY pago ASC, vencimento ASC", conn)

tab1, tab2, tab3 = st.tabs(["⚡ PAINEL", "📑 HISTÓRICO", "➕ NOVO"])

with tab1:
    c1, c2 = st.columns(2)
    pend_f = df_c[(df_c['responsavel'] == 'Fernanda') & (df_c['pago'] == 0)]['valor'].sum()
    pend_j = df_c[(df_c['responsavel'] == 'Jonathan') & (df_c['pago'] == 0)]['valor'].sum()
    c1.metric("FERNANDA", f"R$ {pend_f:,.2f}")
    c2.metric("JONATHAN", f"R$ {pend_j:,.2f}")

    st.markdown("---")
    
    filtro = st.radio("Mostrar:", ["A Pagar", "Pagas", "Todas"], horizontal=True)
    
    # Filtragem baseada no rádio
    if filtro == "A Pagar": df_mostrar = df_c[df_c['pago'] == 0]
    elif filtro == "Pagas": df_mostrar = df_c[df_c['pago'] == 1]
    else: df_mostrar = df_c

    for _, r in df_mostrar.iterrows():
        estilo_pago = "card-pago" if r['pago'] == 1 else ""
        label_pago = "✅" if r['pago'] == 1 else "⏳"
        
        st.markdown(f"""
            <div class='expense-card {estilo_pago}'>
                <span class='owner-tag'>{r['responsavel']}</span>
                <div style='display: flex; justify-content: space-between;'>
                    <b>{label_pago} {r['descricao']}</b>
                    <b style='color: #1F3A93;'>R$ {r['valor']:,.2f}</b>
                </div>
                <small>Vencimento: {r['vencimento']}</small>
            </div>
        """, unsafe_allow_html=True)
        
        col_btn1, col_btn2, col_btn3 = st.columns([1,1,1])
        with col_btn1:
            if r['pago'] == 0:
                if st.button(f"Pagar", key=f"pay_{r['id']}"): alterar_status(r['id'], 1)
            else:
                if st.button(f"Reabrir", key=f"unpay_{r['id']}"): alterar_status(r['id'], 0)
        
        with col_btn2:
            # Opção simplificada de edição via formulário no "Novo" ou expansor aqui
            if st.button(f"Excluir", key=f"del_{r['id']}"): excluir_conta(r['id'])
        st.markdown("<br>", unsafe_allow_html=True)

with tab3:
    with st.form("add_family", clear_on_submit=True):
        resp = st.selectbox("Responsável", ["Fernanda", "Jonathan"])
        desc = st.text_input("O que é?")
        val = st.number_input("Valor R$", min_value=0.0)
        dt = st.date_input("Vencimento")
        if st.form_submit_button("REGISTRAR GASTO"):
            cursor.execute("INSERT INTO contas (descricao, valor, vencimento, responsavel) VALUES (?, ?, ?, ?)", 
                         (desc, val, dt.strftime("%d/%m"), resp))
            conn.commit()
            st.rerun()
