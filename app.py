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

# --- UI/UX ALTO CONTRASTE (SEM VERDE) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700;900&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Roboto', sans-serif; 
        background-color: #FFFFFF !important; 
        color: #000000 !important; 
    }

    header, footer, #MainMenu {visibility: hidden;}
    .block-container {padding-top: 1rem; max-width: 600px; margin: auto;}

    /* Títulos em Azul Marinho Profundo */
    .section-title { 
        color: #001f3f; 
        font-weight: 900; 
        font-size: 24px; 
        margin-top: 20px; 
        border-bottom: 4px solid #001f3f;
        width: 100%;
        padding-bottom: 5px;
    }

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

    /* Abas em Azul Marinho */
    .stTabs [data-baseweb="tab-list"] { background-color: #001f3f; border-radius: 10px; padding: 5px; }
    .stTabs [data-baseweb="tab"] { color: #FFFFFF !important; font-weight: bold; }
    .stTabs [aria-selected="true"] { background-color: #334e68 !important; border-radius: 8px; }

    /* Botões em Branco e Preto */
    .stButton>button { 
        border: 2px solid #000000; 
        border-radius: 8px; 
        font-weight: 900; 
        height: 3.5rem;
        background-color: #FFFFFF;
        color: #000000;
        box-shadow: 3px 3px 0px #000000;
    }
    
    input { border: 2px solid #000000 !important; border-radius: 8px !important; height: 3rem; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("<h2 style='text-align: center; color: #001f3f; font-weight: 900;'>🔐 FamilyBank</h2>", unsafe_allow_html=True)
    senha = st.text_input("Senha da Família", type="password")
    if st.button("ENTRAR NO PAINEL"):
        if senha == SENHA_ACESSO:
            st.session_state["autenticado"] = True
            st.rerun()
    st.stop()

# --- BANCO DE DADOS ---
conn = sqlite3.connect("familybank_v3.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS contas (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        descricao TEXT, 
        valor REAL, 
        vencimento TEXT, 
        pago INTEGER DEFAULT 0, 
        responsavel TEXT,
        data_pagamento TEXT
    )
""")
conn.commit()

# --- FUNÇÕES ---
def acao_pagar(id_conta):
    data_hoje = datetime.date.today().strftime("%d/%m/%Y")
    cursor.execute("UPDATE contas SET pago = 1, data_pagamento = ? WHERE id = ?", (data_hoje, id_conta))
    conn.commit()
    st.rerun()

def acao_excluir(id_conta):
    cursor.execute("DELETE FROM contas WHERE id = ?", (id_conta,))
    conn.commit()
    st.rerun()

# --- HEADER E RESUMO ---
st.markdown("<h1 style='text-align: center; color: #001f3f; font-weight: 900; margin:0;'>FamilyBank</h1>", unsafe_allow_html=True)

df_c = pd.read_sql("SELECT * FROM contas", conn)
total_a_pagar = df_c[df_c['pago'] == 0]['valor'].sum()
total_pago = df_c[df_c['pago'] == 1]['valor'].sum()

tab1, tab2, tab3 = st.tabs(["⚡ PAINEL", "📑 HISTÓRICO", "➕ NOVO"])

with tab1:
    # Resumo em Preto e Branco (Alto Contraste)
    st.markdown(f"""
    <div style="background-color: #000000; padding: 15px; border-radius: 12px; color: white; text-align: center; border: 2px solid #001f3f;">
        <div style="display: flex; justify-content: space-around;">
            <div><small>FALTA PAGAR</small><br><b style="font-size: 22px; color: #FFFFFF;">R$ {total_a_pagar:,.2f}</b></div>
            <div style="border-left: 1px solid #333;"></div>
            <div><small>JÁ PAGO</small><br><b style="font-size: 22px; color: #94a3b8;">R$ {total_pago:,.2f}</b></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    for responsavel in ["Fernanda", "Jonathan"]:
        st.markdown(f"<div class='section-title'>{responsavel.upper()}</div>", unsafe_allow_html=True)
        df_resp = df_c[(df_c['responsavel'] == responsavel) & (df_c['pago'] == 0)]
        
        if df_resp.empty:
            st.write("✓ Tudo em dia.")
        else:
            for _, r in df_resp.iterrows():
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
                c1.button("MARCAR PAGO", key=f"p_{r['id']}", on_click=acao_pagar, args=(r['id'],))
                c2.button("EXCLUIR", key=f"e_{r['id']}", on_click=acao_excluir, args=(r['id'],))

with tab2:
    st.markdown("<div class='section-title'>HISTÓRICO DE PAGOS</div>", unsafe_allow_html=True)
    pesquisa = st.text_input("🔍 Buscar no histórico...")
    
    df_historico = df_c[df_c['pago'] == 1].copy()
    if pesquisa:
        df_historico = df_historico[
            df_historico['descricao'].str.contains(pesquisa, case=False) | 
            df_historico['responsavel'].str.contains(pesquisa, case=False)
        ]

    if df_historico.empty:
        st.info("Nenhum registro.")
    else:
        df_show = df_historico[['responsavel', 'descricao', 'valor', 'vencimento', 'data_pagamento']].rename(columns={
            'responsavel': 'Quem', 'descricao': 'Conta', 'valor': 'R$', 'vencimento': 'Venc.', 'data_pagamento': 'Pago em'
        })
        st.table(df_show)

with tab3:
    st.markdown("<div class='section-title'>ADICIONAR CONTA</div>", unsafe_allow_html=True)
    with st.form("add_form", clear_on_submit=True):
        res = st.selectbox("Responsável", ["Fernanda", "Jonathan"])
        des = st.text_input("Nome da Conta")
        val = st.number_input("Valor R$", min_value=0.0, step=0.01)
        dat = st.date_input("Vencimento")
        if st.form_submit_button("REGISTRAR"):
            cursor.execute("INSERT INTO contas (descricao, valor, vencimento, responsavel) VALUES (?, ?, ?, ?)", 
                         (des, val, dat.strftime("%d/%m"), res))
            conn.commit()
            st.rerun()
