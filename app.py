import streamlit as st
import sqlite3
import pandas as pd
import datetime

# --- CONFIGURAÇÃO DE PÁGINA ---
st.set_page_config(
    page_title="Finanças Pro", 
    page_icon="💸", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- CSS AVANÇADO PARA LOOK & FEEL PROFISSIONAL ---
st.markdown("""
    <style>
    /* Fundo e Fonte */
    .main { background-color: #0E1117; }
    
    /* Esconder elementos desnecessários */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Estilização dos Cards de Métricas */
    div[data-testid="stMetric"] {
        background-color: #161B22;
        border: 1px solid #30363D;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
    }

    /* Estilo das Abas (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        justify-content: space-around;
        background-color: #0E1117;
        padding: 10px;
        position: sticky;
        top: 0;
        z-index: 999;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        border-radius: 20px;
        background-color: #21262D;
        color: #8B949E;
        border: none;
        padding: 0 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #238636 !important; /* Verde Sucesso */
        color: white !important;
    }

    /* Estilo dos Botões */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #238636;
        color: white;
        border: none;
        font-weight: bold;
    }
    
    /* Cards de Transações */
    .transaction-card {
        background-color: #161B22;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
        border-left: 5px solid #238636;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BANCO DE DADOS ---
conn = sqlite3.connect("financas.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS contas (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, valor REAL, vencimento TEXT, pago INTEGER DEFAULT 0)")
cursor.execute("CREATE TABLE IF NOT EXISTS investimentos (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, valor REAL, data TEXT, categoria TEXT)")
conn.commit()

# --- TÍTULO ---
st.markdown("<h2 style='text-align: center; color: #F0F6FC; margin-bottom: 20px;'>💰 My Wallet Pro</h2>", unsafe_allow_html=True)

# --- ABAS ---
tab_home, tab_contas, tab_invest, tab_add = st.tabs(["🏠 Home", "📑 Contas", "📈 Invest", "➕ Novo"])

with tab_home:
    df_c = pd.read_sql("SELECT * FROM contas", conn)
    pendente = df_c[df_c['pago'] == 0]['valor'].sum()
    pago = df_c[df_c['pago'] == 1]['valor'].sum()
    
    st.markdown("### Visão Geral")
    c1, c2 = st.columns(2)
    c1.metric("A PAGAR", f"R$ {pendente:.2f}")
    c2.metric("PAGO", f"R$ {pago:.2f}")
    
    st.markdown("---")
    st.markdown("#### Próximos Vencimentos")
    hoje = datetime.date.today().strftime("%d/%m")
    vencendo = df_c[(df_c['vencimento'] == hoje) & (df_c['pago'] == 0)]
    if not vencendo.empty:
        for _, r in vencendo.iterrows():
            st.error(f"⚠️ **{r['descricao']}** vence hoje!")
    else:
        st.success("Tudo em dia para hoje! 🎉")

with tab_contas:
    mes = st.select_slider("Mês de Referência", options=[f"{i:02d}" for i in range(1, 13)], value=datetime.date.today().strftime("%02m"))
    
    df_c['mes'] = df_c['vencimento'].str.split("/").str[1]
    df_mes = df_c[df_c['mes'] == mes]
    
    for _, row in df_mes.iterrows():
        with st.container():
            # Criando um card visual via Markdown + HTML
            color = "#238636" if row['pago'] == 1 else "#DA3633"
            st.markdown(f"""
                <div style="background-color: #161B22; padding: 12px; border-radius: 10px; border-left: 5px solid {color}; margin-bottom: 5px;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: white; font-weight: bold;">{row['descricao']}</span>
                        <span style="color: white;">R$ {row['valor']:.2f}</span>
                    </div>
                    <div style="color: #8B949E; font-size: 0.8em;">Vence em: {row['vencimento']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            col_b1, col_b2 = st.columns(2)
            if row['pago'] == 0:
                if col_b1.button("✅ Pagar", key=f"p_{row['id']}"):
                    cursor.execute("UPDATE contas SET pago=1 WHERE id=?", (row['id'],))
                    conn.commit()
                    st.rerun()
            if col_b2.button("🗑️", key=f"d_{row['id']}"):
                cursor.execute("DELETE FROM contas WHERE id=?", (row['id'],))
                conn.commit()
                st.rerun()

with tab_add:
    st.markdown("### Novo Registro")
    tipo = st.toggle("É um investimento?", value=False)
    
    with st.form("add_form", clear_on_submit=True):
        nome = st.text_input("Nome / Descrição")
        valor = st.number_input("Valor", min_value=0.0, format="%.2f")
        data = st.date_input("Data", datetime.date.today())
        
        if st.form_submit_button("Salvar no Banco"):
            if not tipo:
                cursor.execute("INSERT INTO contas (descricao, valor, vencimento) VALUES (?, ?, ?)", 
                             (nome, valor, data.strftime("%d/%m")))
            else:
                cursor.execute("INSERT INTO investimentos (descricao, valor, data, categoria) VALUES (?, ?, ?, ?)", 
                             (nome, valor, data.strftime("%d/%m"), "Geral"))
            conn.commit()
            st.balloons()
            st.rerun()

