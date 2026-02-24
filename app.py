import streamlit as st
import sqlite3
import pandas as pd
import datetime

# --- CONFIGURAÇÃO DO NOME E ÍCONE ---
# Aqui você muda o nome que aparece no celular e na aba do navegador
st.set_page_config(
    page_title="Minhas Finanças Pro", 
    page_icon="💰", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- CSS PARA DEIXAR COM CARA DE APP PROFISSIONAL ---
st.markdown("""
    <style>
    /* Esconder o menu padrão do Streamlit e o rodapé */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Estilização dos Cards de Métricas */
    [data-testid="stMetricValue"] {
        font-size: 28px;
        color: #F0B000;
    }
    
    /* Estilo das Abas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        justify-content: center;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #1E1E1E;
        border-radius: 10px 10px 0px 0px;
        color: white;
        padding: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #F0B000 !important;
        color: black !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BANCO DE DADOS ---
conn = sqlite3.connect("financas.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS contas (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, valor REAL, vencimento TEXT, pago INTEGER DEFAULT 0)")
cursor.execute("CREATE TABLE IF NOT EXISTS investimentos (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, valor REAL, data TEXT, categoria TEXT, rentabilidade REAL)")
conn.commit()

# --- TÍTULO ---
st.markdown("<h1 style='text-align: center; color: white;'>🏦 Meu Banco Pessoal</h1>", unsafe_allow_html=True)

# --- NAVEGAÇÃO POR ABAS ---
tab_resumo, tab_contas, tab_invest, tab_novo = st.tabs(["📊 DASHBOARD", "📋 CONTAS", "💹 INVEST", "➕ ADICIONAR"])

with tab_resumo:
    df_c = pd.read_sql("SELECT * FROM contas", conn)
    df_i = pd.read_sql("SELECT * FROM investimentos", conn)
    
    # Cartões de Resumo Estilizados
    st.markdown("### Resumo Geral")
    c1, c2 = st.columns(2)
    pendente = df_c[df_c['pago'] == 0]['valor'].sum()
    c1.metric("A PAGAR", f"R$ {pendente:.2f}")
    c2.metric("INVESTIDO", f"R$ {df_i['valor'].sum():.2f}")

with tab_contas:
    st.markdown("### Suas Contas")
    mes_sel = st.selectbox("Mês", [f"{i:02d}" for i in range(1, 13)], index=datetime.date.today().month - 1)
    
    df_c['mes'] = df_c['vencimento'].str.split("/").str[1]
    df_mes = df_c[df_c['mes'] == mes_sel]

    for _, row in df_mes.iterrows():
        # Container com borda para parecer um card de app
        with st.container():
            col_a, col_b = st.columns([4, 1])
            with col_a:
                st.write(f"**{row['descricao']}**")
                st.caption(f"Vence {row['vencimento']} | R$ {row['valor']:.2f}")
            with col_b:
                if row['pago'] == 0:
                    if st.button("Pagar", key=f"p_{row['id']}"):
                        cursor.execute("UPDATE contas SET pago=1 WHERE id=?", (row['id'],))
                        conn.commit()
                        st.rerun()
                else:
                    st.write("✅")
            st.divider()

# --- ADICIONAR (LAYOUT COMPACTO) ---
with tab_novo:
    tipo = st.pills("Escolha o tipo:", ["Conta", "Investimento"], default="Conta")
    with st.form("form_add", clear_on_submit=True):
        d = st.text_input("Descrição")
        v = st.number_input("Valor R$", min_value=0.0)
        venc = st.date_input("Data")
        if st.form_submit_button("Confirmar Lançamento"):
            if tipo == "Conta":
                cursor.execute("INSERT INTO contas (descricao, valor, vencimento) VALUES (?, ?, ?)", (d, v, venc.strftime("%d/%m")))
            else:
                cursor.execute("INSERT INTO investimentos (descricao, valor, data) VALUES (?, ?, ?)", (d, v, venc.strftime("%d/%m")))
            conn.commit()
            st.success("Lançado com sucesso!")
            st.rerun()

