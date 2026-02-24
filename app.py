import streamlit as st
import sqlite3
import pandas as pd
import datetime
import requests

# Configuração para celular e desktop
st.set_page_config(page_title="Finanças Mobile", layout="wide")

# -----------------------
# FUNÇÃO DE NOTIFICAÇÃO (WhatsApp)
# -----------------------
def enviar_whatsapp(mensagem):
    # Substitua pelos dados da sua API
    url = "SUA_URL_DA_API/sendText"
    headers = {
        "apikey": "SUA_CHAVE_AQUI",
        "Content-Type": "application/json"
    }
    payload = {
        "number": "55XXXXXXXXXXX", # Seu número com DDD (ex: 5511999999999)
        "text": mensagem
    }
    try:
        requests.post(url, json=payload, headers=headers, timeout=10)
    except:
        pass # Silencia erros de conexão para não travar o app

# -----------------------
# CONEXÃO COM BANCO
# -----------------------
conn = sqlite3.connect("financas.db", check_same_thread=False)
cursor = conn.cursor()

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

st.title("💰 Meu Controle Financeiro")

# -----------------------
# INTERFACE EM ABAS (Melhor para Celular)
# -----------------------
tab_contas, tab_invest, tab_add = st.tabs(["📋 Contas", "💹 Investimentos", "➕ Novo"])

# --- ABA DE CONTAS ---
with tab_contas:
    st.subheader("Controle Mensal")
    meses = [f"{i:02d}" for i in range(1, 13)]
    mes_sel = st.selectbox("Selecione o Mês", meses, index=datetime.date.today().month - 1)
    
    df_contas = pd.read_sql("SELECT * FROM contas", conn)
    
    if not df_contas.empty:
        df_contas['mes'] = df_contas['vencimento'].str.split("/").str[1]
        df_mes = df_contas[df_contas['mes'] == mes_sel]
        
        # Métricas rápidas
        c1, c2 = st.columns(2)
        c1.metric("Pendente", f"R$ {df_mes[df_mes['pago']==0]['valor'].sum():.2f}")
        c2.metric("Pago", f"R$ {df_mes[df_mes['pago']==1]['valor'].sum():.2f}")
        
        st.divider()

        for index, row in df_mes.iterrows():
            with st.container(border=True):
                col_info, col_btn = st.columns([3, 1])
                status = "✅" if row['pago'] == 1 else "❌"
                col_info.write(f"{status} **{row['descricao']}**")
                col_info.caption(f"Vencimento: {row['vencimento']} | R$ {row['valor']:.2f}")
                
                if row['pago'] == 0:
                    if col_btn.button("Pagar", key=f"pg_{row['id']}"):
                        cursor.execute("UPDATE contas SET pago=1 WHERE id=?", (row['id'],))
                        conn.commit()
                        st.rerun()
                
                if col_btn.button("🗑️", key=f"del_{row['id']}"):
                    cursor.execute("DELETE FROM contas WHERE id=?", (row['id'],))
                    conn.commit()
                    st.rerun()

# --- ABA DE INVESTIMENTOS ---
with tab_invest:
    st.subheader("Meus Investimentos")
    df_invest = pd.read_sql("SELECT * FROM investimentos", conn)
    if not df_invest.empty:
        st.dataframe(df_invest, use_container_width=True)
        st.metric("Total Investido", f"R$ {df_invest['valor'].sum():.2f}")
    else:
        st.info("Nenhum investimento registrado.")

# --- ABA DE CADASTRO ---
with tab_add:
    st.subheader("Adicionar Registro")
    
    tipo = st.radio("O que deseja adicionar?", ["Conta/Gasto", "Investimento"])
    
    if tipo == "Conta/Gasto":
        with st.form("form_conta"):
            desc = st.text_input("Descrição")
            val = st.number_input("Valor", min_value=0.0)
            venc = st.date_input("Vencimento")
            if st.form_submit_button("Salvar Conta"):
                venc_formatado = venc.strftime("%d/%m")
                cursor.execute("INSERT INTO contas (descricao, valor, vencimento) VALUES (?, ?, ?)", (desc, val, venc_formatado))
                conn.commit()
                # Notifica se o vencimento for para hoje
                if venc_formatado ==
        )

else:
    st.info("Nenhuma conta ou investimento cadastrado ainda.")

