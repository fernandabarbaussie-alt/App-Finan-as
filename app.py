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

    .section-title { 
        color: #001f3f; 
        font-weight: 900; 
        font-size: 24px; 
        margin-top: 20px; 
        border-bottom: 4px solid #001f3f;
        width: 100%;
        padding-bottom: 5px;
        margin-bottom: 15px;
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

    .stTabs [data-baseweb="tab-list"] { background-color: #001f3f; border-radius: 10px; padding: 5px; }
    .stTabs [data-baseweb="tab"] { color: #FFFFFF !important; font-weight: bold; }
    .stTabs [aria-selected="true"] { background-color: #334e68 !important; border-radius: 8px; }

    .stButton>button { 
        border: 2px solid #000000; 
        border-radius: 8px; 
        font-weight: 900; 
        height: 3.5rem;
        background-color: #FFFFFF;
        color: #000000;
        box-shadow: 3px 3px 0px #000000;
    }
    
    input, select { border: 2px solid #000000 !important; border-radius: 8px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE LOGIN ---
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
        descricao TEXT, valor REAL, vencimento TEXT, 
        pago INTEGER DEFAULT 0, responsavel TEXT, data_pagamento TEXT
    )
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS investimentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        descricao TEXT, categoria TEXT, valor REAL, data TEXT
    )
""")
conn.commit()

# --- FUNÇÕES ---
def acao_pagar(id_conta):
    data_hoje = datetime.date.today().strftime("%d/%m/%Y")
    cursor.execute("UPDATE contas SET pago = 1, data_pagamento = ? WHERE id = ?", (data_hoje, id_conta))
    conn.commit()
    st.rerun()

def acao_excluir(id_item, tabela="contas"):
    cursor.execute(f"DELETE FROM {tabela} WHERE id = ?", (id_item,))
    conn.commit()
    st.rerun()

# --- CARREGAMENTO DE DADOS ---
df_c = pd.read_sql("SELECT * FROM contas", conn)
df_i = pd.read_sql("SELECT * FROM investimentos", conn)

total_a_pagar = df_c[df_c['pago'] == 0]['valor'].sum()
total_investido = df_i['valor'].sum()

# --- HEADER ---
st.markdown("<h1 style='text-align: center; color: #001f3f; font-weight: 900; margin:0;'>FamilyBank</h1>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["⚡ PAINEL", "📈 INVEST", "📑 HISTÓRICO", "➕ NOVO"])

with tab1:
    st.markdown(f"""
    <div style="background-color: #000000; padding: 15px; border-radius: 12px; color: white; text-align: center; border: 2px solid #001f3f;">
        <div style="display: flex; justify-content: space-around;">
            <div><small>A PAGAR</small><br><b style="font-size: 22px; color: #FFFFFF;">R$ {total_a_pagar:,.2f}</b></div>
            <div style="border-left: 1px solid #333;"></div>
            <div><small>PATRIMÔNIO</small><br><b style="font-size: 22px; color: #94a3b8;">R$ {total_investido:,.2f}</b></div>
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
    st.markdown("<div class='section-title'>MEUS INVESTIMENTOS</div>", unsafe_allow_html=True)
    st.metric("Total Acumulado", f"R$ {total_investido:,.2f}")
    
    categorias = ["Renda Fixa", "Renda Variável", "Tesouro Direto", "Cripto", "COE", "Previdência Privada", "Outros"]
    
    for cat in categorias:
        df_cat = df_i[df_i['categoria'] == cat]
        if not df_cat.empty:
            soma_cat = df_cat['valor'].sum()
            with st.expander(f"📁 {cat.upper()} - R$ {soma_cat:,.2f}"):
                for _, inv in df_cat.iterrows():
                    st.markdown(f"""
                        <div style='border-bottom: 1px solid #eee; padding: 10px 0; display: flex; justify-content: space-between;'>
                            <span><b>{inv['descricao']}</b><br><small>{inv['data']}</small></span>
                            <span style='color: #001f3f; font-weight: 900;'>R$ {inv['valor']:,.2f}</span>
                        </div>
                    """, unsafe_allow_html=True)
                    st.button("Excluir", key=f"del_inv_{inv['id']}", on_click=acao_excluir, args=(inv['id'], "investimentos"))

with tab3:
    st.markdown("<div class='section-title'>CONTAS PAGAS</div>", unsafe_allow_html=True)
    pesquisa = st.text_input("🔍 Pesquisar conta ou pessoa...")
    df_historico = df_c[df_c['pago'] == 1].copy()
    if pesquisa:
        df_historico = df_historico[df_historico['descricao'].str.contains(pesquisa, case=False) | df_historico['responsavel'].str.contains(pesquisa, case=False)]
    
    if not df_historico.empty:
        df_show = df_historico[['responsavel', 'descricao', 'valor', 'vencimento', 'data_pagamento']].rename(columns={
            'responsavel': 'Quem', 'descricao': 'Conta', 'valor': 'R$', 'vencimento': 'Venc.', 'data_pagamento': 'Pago em'
        })
        st.table(df_show)

with tab4:
    tipo = st.radio("O que deseja registrar?", ["Conta", "Investimento"], horizontal=True)
    with st.form("add_form", clear_on_submit=True):
        if tipo == "Conta":
            res = st.selectbox("Responsável", ["Fernanda", "Jonathan"])
            cat_inv = "N/A"
            des = st.text_input("Nome da Conta (Ex: Aluguel)")
        else:
            cat_inv = st.selectbox("Tipo de Investimento", ["Renda Fixa", "Renda Variável", "Tesouro Direto", "Cripto", "COE", "Previdência Privada", "Outros"])
            des = st.text_input("Nome do Título/Ativo (Ex: CDB Banco X)")
            res = "Geral"
            
        val = st.number_input("Valor R$", min_value=0.0, step=0.01)
        dat = st.date_input("Data")
        
        if st.form_submit_button("SALVAR REGISTRO"):
            if tipo == "Conta":
                cursor.execute("INSERT INTO contas (descricao, valor, vencimento, responsavel) VALUES (?, ?, ?, ?)", (des, val, dat.strftime("%d/%m"), res))
            else:
                cursor.execute("INSERT INTO investimentos (descricao, categoria, valor, data) VALUES (?, ?, ?, ?)", (des, cat_inv, val, dat.strftime("%d/%m/%Y")))
            conn.commit()
            st.success("Registrado com sucesso!")
            st.rerun()
