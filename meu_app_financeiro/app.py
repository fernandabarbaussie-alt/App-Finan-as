import streamlit as st
import sqlite3
import pandas as pd
import datetime

st.set_page_config(page_title="Controle Financeiro", layout="wide")

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
conn.commit()

st.title("💰 Controle Financeiro Inteligente")

# -----------------------
# FORMULÁRIO
# -----------------------
with st.form("nova_conta"):
    col1, col2, col3 = st.columns(3)

    with col1:
        descricao = st.text_input("Descrição")

    with col2:
        valor = st.number_input("Valor", min_value=0.0, format="%.2f")

    with col3:
        vencimento = st.date_input("Data de vencimento")

    submitted = st.form_submit_button("Adicionar Conta")

    if submitted and descricao:
        cursor.execute(
            "INSERT INTO contas (descricao, valor, vencimento) VALUES (?, ?, ?)",
            (descricao, valor, vencimento.strftime("%Y-%m-%d"))
        )
        conn.commit()
        st.success("Conta adicionada com sucesso!")

# -----------------------
# CARREGAR DADOS
# -----------------------
df = pd.read_sql("SELECT * FROM contas", conn)

if not df.empty:

    df["vencimento"] = pd.to_datetime(df["vencimento"])

    # -----------------------
    # FILTRO POR MÊS
    # -----------------------
    st.subheader("📅 Filtro por Mês")

    mes_selecionado = st.selectbox(
        "Escolha o mês",
        sorted(df["vencimento"].dt.to_period("M").astype(str).unique())
    )

    df_filtrado = df[df["vencimento"].dt.to_period("M").astype(str) == mes_selecionado]

    # -----------------------
    # MÉTRICAS
    # -----------------------
    total_pago = df_filtrado[df_filtrado["pago"] == 1]["valor"].sum()
    total_pendente = df_filtrado[df_filtrado["pago"] == 0]["valor"].sum()
    total_geral = df_filtrado["valor"].sum()

    col1, col2, col3 = st.columns(3)

    col1.metric("💰 Total Pago", f"R$ {total_pago:.2f}")
    col2.metric("📌 Total Pendente", f"R$ {total_pendente:.2f}")
    col3.metric("📊 Total Geral", f"R$ {total_geral:.2f}")

    # -----------------------
    # TABELA + BOTÃO PAGAR
    # -----------------------
    st.subheader("📋 Contas")

    for index, row in df_filtrado.iterrows():
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])

        col1.write(row["descricao"])
        col2.write(f"R$ {row['valor']:.2f}")
        col3.write(row["vencimento"].strftime("%d/%m/%Y"))
        col4.write("✅ Pago" if row["pago"] == 1 else "❌ Pendente")

        if row["pago"] == 0:
            if col5.button("Marcar como Pago", key=row["id"]):
                cursor.execute(
                    "UPDATE contas SET pago = 1 WHERE id = ?",
                    (row["id"],)
                )
                conn.commit()
                st.rerun()

    # -----------------------
    # GRÁFICO
    # -----------------------
    st.subheader("📈 Gráfico Financeiro")

    grafico = df_filtrado.groupby("pago")["valor"].sum()
    grafico.index = ["Pago" if i == 1 else "Pendente" for i in grafico.index]

    st.bar_chart(grafico)

    # -----------------------
    # EXPORTAR EXCEL
    # -----------------------
    st.subheader("📤 Exportar")

    excel = df_filtrado.to_excel("relatorio.xlsx", index=False)
    with open("relatorio.xlsx", "rb") as f:
        st.download_button(
            label="Baixar Relatório em Excel",
            data=f,
            file_name="relatorio_financeiro.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

else:
    st.info("Nenhuma conta cadastrada ainda.")
    

