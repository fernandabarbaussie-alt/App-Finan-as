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

# --- UI/UX ALTO CONTRASTE (FOCO EM LEITURA NO CELULAR) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700;900&display=swap');
    
    /* Cores de Alto Contraste */
    html, body, [class*="css"] { 
        font-family: 'Roboto', sans-serif; 
        background-color: #FFFFFF !important; 
        color: #000000 !important; 
    }

    header, footer, #MainMenu {visibility: hidden;}
    .block-container {padding-top: 1rem; max-width: 600px; margin: auto;}

    /* Títulos das Seções (Nomes) */
    .section-title { 
        color: #002366; 
        font-weight: 900; 
        font-size: 24px; 
        margin-top: 20px; 
        border-bottom: 4px solid #00C853;
        width: 100%;
        padding-bottom: 5px;
    }

    /* Cards de Contas */
    .expense-card { 
        background: #F9F9F9; 
        border-radius: 10px; 
        padding: 15px; 
        margin-bottom: 8px; 
        border: 2px solid #000000;
    }
    
    .card-desc { font-size: 18px; font-weight: 700; color: #000000; }
    .card-price { font-size: 20px; font-weight: 900; color: #D32F2F; }
    .card-date { font-size: 14px; color: #444444; font-weight: bold; }

    /* Estilo das Abas */
    .stTabs [data-baseweb="tab-list"] { background-color: #002366; border-radius: 10px; padding: 5px; }
    .stTabs [data-baseweb="tab"] { color: #FFFFFF !important; font-weight: bold; }
    .stTabs [aria-selected="true"] { background-color: #00C853 !important; border-radius: 8px; }

    /* Botões Grandes */
    .stButton>button { 
        border: 2px solid #000000; 
        border-radius: 8px; 
        font-weight: 900; 
        height: 3.5rem;
        background-color: #FFFFFF;
        color: #000000;
        box-shadow: 3px 3px 0px #000000;
    }
    
    /* Input de Senha e Forms */
    input { border: 2px solid #000000 !important; border-radius: 8px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("<h2 style='text-align: center; color: #002366; font-weight: 900;'>🔐 FamilyBank</h2>", unsafe_allow_html=True)
    senha = st.text_input("Senha da Família", type="password")
    if st.button("ENTRAR NO PAINEL"):
        if senha == SENHA_ACESSO:
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.error("Senha incorreta.")
    st.stop()

# --- BANCO DE DADOS ---
conn = sqlite3.connect("familybank_v2.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS contas (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, valor REAL, vencimento TEXT, pago INTEGER DEFAULT 0, responsavel TEXT)")
conn.commit()

# --- FUNÇÕES DE GESTÃO ---
def acao_pagar(id_conta):
    cursor.execute("UPDATE contas SET pago = 1 WHERE id = ?", (id_conta,))
    conn.commit()
    st.rerun()

def acao_excluir(id_conta):
    cursor.execute("DELETE FROM contas WHERE id = ?", (id_conta,))
    conn.commit()
    st.rerun()

# --- HEADER E RESUMO ---
st.markdown("<h1 style='text-align: center; color: #002366; font-weight: 900; margin:0;'>FamilyBank</h1>", unsafe_allow_html=True)

df_c = pd.read_sql("SELECT * FROM contas", conn)
total_a_pagar = df_c[df_c['pago'] == 0]['valor'].sum()
total_pago = df_c[df_c['pago'] == 1]['valor'].sum()

# --- NAVEGAÇÃO ---
tab1, tab2, tab3 = st.tabs(["⚡ PAINEL", "📑 HISTÓRICO", "➕ NOVO"])

with tab1:
    # Resumo de Totais (Fundo Preto para contraste máximo)
    st.markdown(f"""
    <div style="background-color: #000000; padding: 15px; border-radius: 12px; color: white; text-align: center; border: 2px solid #00C853;">
        <div style="display: flex; justify-content: space-around;">
            <div><small>A PAGAR</small><br><b style="font-size: 22px; color: #FFD700;">R$ {total_a_pagar:,.2f}</b></div>
            <div style="border-left: 1px solid #333;"></div>
            <div><small>PAGO</small><br><b style="font-size: 22px; color: #00FFA3;">R$ {total_pago:,.2f}</b></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- SEÇÃO FERNANDA ---
    st.markdown("<div class='section-title'>FERNANDA</div>", unsafe_allow_html=True)
    df_f = df_c[(df_c['responsavel'] == 'Fernanda') & (df_c['pago'] == 0)]
    if df_f.empty:
        st.write("✅ Nenhuma conta pendente.")
    else:
        for _, r in df_f.iterrows():
            st.markdown(f"""
                <div class='expense-card'>
                    <div style='display: flex; justify-content: space-between;'>
                        <span class='card-desc'>{r['descricao']}</span>
                        <span class='card-price'>R$ {r['valor']:,.2f}</span>
                    </div>
                    <span class='card-date'>Vencimento: {r['vencimento']}</span>
                </div>
            """, unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            c1.button("PAGO ✅", key=f"p_f_{r['id']}", on_click=acao_pagar, args=(r['id'],))
            c2.button("EXCLUIR 🗑️", key=f"e_f_{r['id']}", on_click=acao_excluir, args=(r['id'],))

    # --- SEÇÃO JONATHAN ---
    st.markdown("<div class='section-title'>JONATHAN</div>", unsafe_allow_html=True)
    df_j = df_c[(df_c['responsavel'] == 'Jonathan') & (df_c['pago'] == 0)]
    if df_j.empty:
        st.write("✅ Nenhuma conta pendente.")
    else:
        for _, r in df_j.iterrows():
            st.markdown(f"""
                <div class='expense-card'>
                    <div style='display: flex; justify-content: space-between;'>
                        <span class='card-desc'>{r['descricao']}</span>
                        <span class='card-price'>R$ {r['valor']:,.2f}</span>
                    </div>
                    <span class='card-date'>Vencimento: {r['vencimento']}</span>
                </div>
            """, unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            c1.button("PAGO ✅", key=f"p_j_{r['id']}", on_click=acao_pagar, args=(r['id'],))
            c2.button("EXCLUIR 🗑️", key=f"e_j_{r['id']}", on_click=acao_excluir, args=(r['id'],))

with tab2:
    st.markdown(f"### 📑 Contas Pagas (Total: R$ {total_pago:,.2f})")
    df_pagas = df_c[df_c['pago'] == 1]
    if df_pagas.empty:
        st.info("O histórico está vazio.")
    else:
        # Tabela em alto contraste
        st.table(df_pagas[['responsavel', 'descricao', 'valor', 'vencimento']])
        if st.button("LIMPAR HISTÓRICO"):
            cursor.execute("DELETE FROM contas WHERE pago = 1")
            conn.commit()
            st.rerun()

with tab3:
    st.markdown("<div class='section-title'>NOVO GASTO</div>", unsafe_allow_html=True)
    with st.form("add_form", clear_on_submit=True):
        res = st.selectbox("Quem é o dono?", ["Fernanda", "Jonathan"])
        des = st.text_input("O que é?")
        val = st.number_input("Valor R$", min_value=0.0, step=0.01)
        dat = st.date_input("Data do Vencimento")
        if st.form_submit_button("REGISTRAR NO SISTEMA"):
            data_simples = dat.strftime("%d/%m")
            cursor.execute("INSERT INTO contas (descricao, valor, vencimento, responsavel) VALUES (?, ?, ?, ?)", 
                         (des, val, data_simples, res))
            conn.commit()
            st.balloons()
            st.rerun()
