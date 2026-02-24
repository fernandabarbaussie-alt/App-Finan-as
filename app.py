import streamlit as st
import sqlite3
import pandas as pd
import datetime

# Configuração da página para Mobile e Desktop
st.set_page_config(page_title="Finanças Mobile", layout="wide", initial_sidebar_state="collapsed")

# -----------------------
# CONEXÃO COM BANCO
# -----------------------
conn = sqlite3.connect("financas.db", check_same_thread=False)
cursor = conn.cursor()

# Criar tabelas se não existirem
cursor.execute("""
CREATE TABLE IF NOT EXISTS contas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descricao TEXT,
    valor REAL,
    vencimento TEXT,
    pago INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS investimentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descricao TEXT,
    valor REAL,
    data TEXT,
    categoria TEXT,
    rentabilidade REAL
)
""")
conn.commit()

# -----------------------
# CABEÇALHO E ALERTAS
# -----------------------
st.title("💰 Meu Controle Financeiro")

hoje_str = datetime.date.today().strftime("%d/%m")
cursor.execute("SELECT descricao, valor FROM contas WHERE vencimento = ? AND pago = 0", (hoje_str,))
vencendo_hoje = cursor.fetchall()

if vencendo_hoje:
    with st.container():
        for c in vencendo_hoje:
            st.warning(f"⚠️ **Vence hoje:** {c[0]} (R$ {c[1]:.2f})")

# -----------------------
# INTERFACE EM ABAS (Navegação Mobile)
# -----------------------
tab_resumo, tab_contas, tab_invest, tab_add = st.tabs(["📊 Resumo", "📋 Contas", "💹 Invest", "➕ Novo"])

# --- ABA 1: RESUMO ---
with tab_resumo:
    df_c = pd.read_sql("SELECT * FROM contas", conn)
    df_i = pd.read_sql("SELECT * FROM investimentos", conn)
    
    col1, col2 = st.columns(2)
    with col1:
        pendente = df_c[df_c['pago'] == 0]['valor'].sum()
        st.metric("Pendente", f"R$ {pendente:.2f}", delta_color="inverse")
    with col2:
        investido = df_i['valor'].sum()
        st.metric("Total Investido", f"R$ {investido:.2f}")

# --- ABA 2: CONTAS ---
with tab_contas:
    meses = [f"{i:02d}" for i in range(1, 13)]
    mes_sel = st.selectbox("Filtrar Mês", meses, index=datetime.date.today().month - 1)
    
    df_c['mes'] = df_c['vencimento'].str.split("/").str[1]
    df_mes = df_c[df_c['mes'] == mes_sel]

    if df_mes.empty:
        st.info("Nenhuma conta para este mês.")
    else:
        for _, row in df_mes.iterrows():
            with st.container(border=True):
                c_inf, c_btn = st.columns([3, 1])
                status = "✅" if row['pago'] == 1 else "🔴"
                c_inf.write(f"{status} **{row['descricao']}**")
                c_inf.caption(f"Venc: {row['vencimento']} | R$ {row['valor']:.2f}")
                
                if row['pago'] == 0:
                    if c_btn.button("Pagar", key=f"pg_{row['id']}"):
                        cursor.execute("UPDATE contas SET pago=1 WHERE id=?", (row['id'],))
                        conn.commit()
                        st.rerun()
                
                if c_btn.button("🗑️", key=f"del_{row['id']}"):
                    cursor.execute("DELETE FROM contas WHERE id=?", (row['id'],))
                    conn.commit()
                    st.rerun()

# --- ABA 3: INVESTIMENTOS ---
with tab_invest:
    if not df_i.empty:
        st.dataframe(df_i[['descricao', 'valor', 'categoria', 'data']], use_container_width=True, hide_index=True)
    else:
        st.write("Sem investimentos.")

# --- ABA 4: ADICIONAR NOVO ---
with tab_add:
    opcao = st.segmented_control("Tipo", ["Conta", "Investimento"], default="Conta")
    
    if opcao == "Conta":
        with st.form("f_conta", clear_on_submit=True):
            d = st.text_input("Nome da Conta")
            v = st.number_input("Valor", min_value=0.0, step=0.01)
            dt = st.date_input("Vencimento")
            if st.form_submit_button("Salvar"):
                cursor.execute("INSERT INTO contas (descricao, valor, vencimento) VALUES (?, ?, ?)",
                             (d, v, dt.strftime("%d/%m")))
                conn.commit()
                st.success("Conta salva!")
                st.rerun()
    else:
        with st.form("f_inv", clear_on_submit=True):
            d_i = st.text_input("Onde investiu?")
            v_i = st.number_input("Valor", min_value=0.0)
            c_i = st.selectbox("Tipo", ["Renda Fixa", "Ações", "Cripto", "FIIs"])
            if st.form_submit_button("Salvar"):
                cursor.execute("INSERT INTO investimentos (descricao, valor, data, categoria) VALUES (?, ?, ?, ?)",
                             (d_i, v_i, hoje_str, c_i))
                conn.commit()
                st.success("Investimento salvo!")
                st.rerun()

