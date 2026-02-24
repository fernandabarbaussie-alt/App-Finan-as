import streamlit as st
import sqlite3
import pandas as pd
import datetime

# --- CONFIGURAÇÃO ---
SENHA_ACESSO = "1234" 

st.set_page_config(page_title="FamilyBank", page_icon="💍", layout="wide")

# --- UI/UX CORPORATIVA ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #F5F5F5; color: #4A4A4A; }
    header, footer, #MainMenu {visibility: hidden;}
    .block-container {padding-top: 1rem; max-width: 600px; margin: auto;}

    /* Títulos de Seção */
    .section-title { 
        color: #1F3A93; font-weight: 800; font-size: 20px; 
        margin-top: 20px; margin-bottom: 10px; border-bottom: 2px solid #2ECC71; width: fit-content;
    }

    /* Card de Gasto */
    .expense-card { 
        background: #FFFFFF; border-radius: 12px; padding: 12px; margin-bottom: 8px; 
        border: 1px solid #DEDEDE; border-left: 5px solid #E74C3C; 
    }
    
    .stTabs [data-baseweb="tab-list"] { background-color: #1F3A93; border-radius: 12px; }
    .stTabs [data-baseweb="tab"] { color: #FFFFFF; }
    .stTabs [aria-selected="true"] { background-color: #2ECC71 !important; }

    .stButton>button { border-radius: 8px; font-weight: bold; width: 100%; }
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

# --- BANCO DE DADOS ---
conn = sqlite3.connect("financas_casal.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS contas (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, valor REAL, vencimento TEXT, pago INTEGER DEFAULT 0, responsavel TEXT)")
conn.commit()

# --- FUNÇÕES ---
def marcar_pago(id_conta):
    cursor.execute("UPDATE contas SET pago = 1 WHERE id = ?", (id_conta,))
    conn.commit()
    st.rerun()

def excluir_conta(id_conta):
    cursor.execute("DELETE FROM contas WHERE id = ?", (id_conta,))
    conn.commit()
    st.rerun()

# --- HEADER ---
st.markdown("<h1 style='text-align: center; color: #1F3A93; margin:0;'>Family<span style='color: #2ECC71;'>Bank</span></h1>", unsafe_allow_html=True)

df_c = pd.read_sql("SELECT * FROM contas", conn)

tab1, tab2, tab3 = st.tabs(["⚡ PAINEL", "📑 HISTÓRICO", "➕ NOVO"])

with tab1:
    # --- SEÇÃO FERNANDA ---
    st.markdown("<div class='section-title'>FERNANDA</div>", unsafe_allow_html=True)
    contas_f = df_c[(df_c['responsavel'] == 'Fernanda') & (df_c['pago'] == 0)]
    
    if contas_f.empty:
        st.write("✨ Nenhuma conta pendente.")
    else:
        for _, r in contas_f.iterrows():
            st.markdown(f"""
                <div class='expense-card'>
                    <div style='display: flex; justify-content: space-between;'>
                        <b>{r['descricao']}</b>
                        <b style='color: #1F3A93;'>R$ {r['valor']:,.2f}</b>
                    </div>
                    <small>Vencimento: {r['vencimento']}</small>
                </div>
            """, unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1: st.button("✅ Pagar", key=f"f_p_{r['id']}", on_click=marcar_pago, args=(r['id'],))
            with c2: st.button("🗑️ Excluir", key=f"f_e_{r['id']}", on_click=excluir_conta, args=(r['id'],))

    # --- SEÇÃO JONATHAN ---
    st.markdown("<div class='section-title'>JONATHAN</div>", unsafe_allow_html=True)
    contas_j = df_c[(df_c['responsavel'] == 'Jonathan') & (df_c['pago'] == 0)]
    
    if contas_j.empty:
        st.write("✨ Nenhuma conta pendente.")
    else:
        for _, r in contas_j.iterrows():
            st.markdown(f"""
                <div class='expense-card'>
                    <div style='display: flex; justify-content: space-between;'>
                        <b>{r['descricao']}</b>
                        <b style='color: #1F3A93;'>R$ {r['valor']:,.2f}</b>
                    </div>
                    <small>Vencimento: {r['vencimento']}</small>
                </div>
            """, unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1: st.button("✅ Pagar", key=f"j_p_{r['id']}", on_click=marcar_pago, args=(r['id'],))
            with c2: st.button("🗑️ Excluir", key=f"j_e_{r['id']}", on_click=excluir_conta, args=(r['id'],))

with tab2:
    st.markdown("### 📑 Histórico (Pagas)")
    df_pagas = df_c[df_c['pago'] == 1].copy()
    if df_pagas.empty:
        st.info("Nenhuma conta paga no histórico ainda.")
    else:
        st.dataframe(df_pagas[['responsavel', 'descricao', 'valor', 'vencimento']], use_container_width=True, hide_index=True)
        if st.button("Limpar Histórico"):
            cursor.execute("DELETE FROM contas WHERE pago = 1")
            conn.commit()
            st.rerun()

with tab3:
    with st.form("add_family", clear_on_submit=True):
        st.markdown("##### ➕ Novo Gasto")
        resp = st.selectbox("Responsável", ["Fernanda", "Jonathan"])
        desc = st.text_input("O que é?")
        val = st.number_input("Valor R$", min_value=0.0)
        dt = st.date_input("Vencimento")
        if st.form_submit_button("SALVAR"):
            # Salva apenas dia/mês no banco
            data_formatada = dt.strftime("%d/%m")
            cursor.execute("INSERT INTO contas (descricao, valor, vencimento, responsavel) VALUES (?, ?, ?, ?)", 
                         (desc, val, data_formatada, resp))
            conn.commit()
            st.rerun()
