import streamlit as st
import sqlite3
import pandas as pd
import datetime

st.set_page_config(page_title="Controle Financeiro Completo", layout="wide")

# -----------------------
# CONEXÃO COM BANCO
# -----------------------
conn = sqlite3.connect("financas.db", check_same_thread=False)
cursor = conn.cursor()

# Tabela de contas (vencimento agora é DD/MM)
cursor.execute("""
CREATE TABLE IF NOT EXISTS contas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descricao TEXT,
    valor REAL,
    vencimento TEXT,
    pago INTEGER DEFAULT 0
)
""")

# Tabela de investimentos com categoria
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

st.title("💰 Controle Financeiro Completo")

# -----------------------
# FORMULÁRIO DE NOVA CONTA
# -----------------------
with st.form("nova_conta"):
    st.subheader("➕ Adicionar Conta")
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
            (descricao, valor, vencimento.strftime("%d/%m"))
        )
        conn.commit()
        st.success("Conta adicionada com sucesso!")

# -----------------------
# FORMULÁRIO DE INVESTIMENTO
# -----------------------
categorias = ["Renda Fixa", "Renda Variável", "Cripto", "Previdência", "Tesouro Direto", "Fundos", "COE"]

with st.form("novo_investimento"):
    st.subheader("💹 Adicionar Investimento")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1: descricao_inv = st.text_input("Descrição", key="desc_inv")
    with col2: valor_inv = st.number_input("Valor", min_value=0.0, format="%.2f", key="valor_inv")
    with col3: data_inv = st.date_input("Data (DD/MM)", key="data_inv")
    with col4: categoria_inv = st.selectbox("Categoria", categorias, key="cat_inv")
    with col5: rent_inv = st.number_input("Rentabilidade (%)", min_value=0.0, format="%.2f", key="rent_inv")
    submitted_inv = st.form_submit_button("Adicionar Investimento")
    if submitted_inv and descricao_inv:
        cursor.execute(
            "INSERT INTO investimentos (descricao, valor, data, categoria, rentabilidade) VALUES (?, ?, ?, ?, ?)",
            (descricao_inv, valor_inv, data_inv.strftime("%d/%m"), categoria_inv, rent_inv)
        )
        conn.commit()
        st.success("Investimento adicionado com sucesso!")

# -----------------------
# CARREGAR DADOS
# -----------------------
df_contas = pd.read_sql("SELECT * FROM contas", conn)
df_invest = pd.read_sql("SELECT * FROM investimentos", conn)

if not df_contas.empty or not df_invest.empty:

    st.subheader("📅 Controle Anual e Mensal")
    anos = [ "2025", "2026", "2027", "2028", "2029", "2030"] 
    ano_selecionado = st.selectbox("Escolha o ano", anos, index=anos.index("2025"))
    meses = [f"{i:02d}" for i in range(1, 13)]
    mes_selecionado = st.selectbox("Escolha o mês", meses)

    # -----------------------
    # TRATAR DATAS DE FORMA SEGURA
    # -----------------------
    # Contas
    df_contas = df_contas.dropna(subset=['vencimento'])
    df_contas = df_contas[df_contas['vencimento'].str.contains("/")]
    df_contas['mes'] = pd.to_numeric(df_contas['vencimento'].str.split("/").str[1], errors='coerce')
    df_contas = df_contas.dropna(subset=['mes'])
    df_contas['mes'] = df_contas['mes'].astype(int)

    # Investimentos
    df_invest = df_invest.dropna(subset=['data'])
    df_invest = df_invest[df_invest['data'].str.contains("/")]
    df_invest['mes'] = pd.to_numeric(df_invest['data'].str.split("/").str[1], errors='coerce')
    df_invest = df_invest.dropna(subset=['mes'])
    df_invest['mes'] = df_invest['mes'].astype(int)

    # Filtrar pelo mês selecionado
    df_contas_mes = df_contas[df_contas['mes'] == int(mes_selecionado)]
    df_invest_mes = df_invest[df_invest['mes'] == int(mes_selecionado)]

    # -----------------------
    # MÉTRICAS
    # -----------------------
    total_pago = df_contas_mes[df_contas_mes["pago"]==1]["valor"].sum()
    total_pendente = df_contas_mes[df_contas_mes["pago"]==0]["valor"].sum()
    total_geral = df_contas_mes["valor"].sum()
    total_invest = df_invest_mes["valor"].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Total Pago", f"R$ {total_pago:.2f}")
    col2.metric("📌 Total Pendente", f"R$ {total_pendente:.2f}")
    col3.metric("📊 Total Geral", f"R$ {total_geral:.2f}")
    col4.metric("💹 Total Investimentos", f"R$ {total_invest:.2f}")

    # -----------------------
    # TABELA DE CONTAS
    # -----------------------
    st.subheader("📋 Contas")
    for index, row in df_contas_mes.iterrows():
        col1, col2, col3, col4, col5, col6 = st.columns([2,1,1,1,1,1])
        col1.write(row["descricao"])
        col2.write(f"R$ {row['valor']:.2f}")
        col3.write(row["vencimento"])
        col4.write("✅ Pago" if row["pago"]==1 else "❌ Pendente")

        if row["pago"] == 0:
            if col5.button("Marcar como Pago", key=f"pago_{row['id']}"):
                cursor.execute("UPDATE contas SET pago=1 WHERE id=?", (row["id"],))
                conn.commit()
                st.experimental_rerun()

        if col6.button("Editar", key=f"edit_{row['id']}"):
            nova_desc = st.text_input("Nova descrição", value=row['descricao'], key=f"desc_{row['id']}")
            novo_valor = st.number_input("Novo valor", value=row['valor'], key=f"valor_{row['id']}")
            nova_data = st.date_input("Nova data", value=datetime.datetime.strptime(row['vencimento'], "%d/%m"), key=f"data_{row['id']}")
            if st.button("Salvar Alterações", key=f"save_{row['id']}"):
                cursor.execute(
                    "UPDATE contas SET descricao=?, valor=?, vencimento=? WHERE id=?",
                    (nova_desc, novo_valor, nova_data.strftime("%d/%m"), row['id'])
                )
                conn.commit()
                st.experimental_rerun()

        if col5.button("Apagar", key=f"del_{row['id']}"):
            cursor.execute("DELETE FROM contas WHERE id=?", (row["id"],))
            conn.commit()
            st.experimental_rerun()

    # -----------------------
    # TABELA DE INVESTIMENTOS
    # -----------------------
    st.subheader("💹 Investimentos")
    for cat in categorias:
        st.markdown(f"**{cat}**")
        df_cat = df_invest_mes[df_invest_mes["categoria"] == cat]
        for index, row in df_cat.iterrows():
            col1, col2, col3, col4, col5 = st.columns([2,1,1,1,1])
            col1.write(row["descricao"])
            col2.write(f"R$ {row['valor']:.2f}")
            col3.write(row["data"])
            col4.write(f"{row['rentabilidade']}%")
            if col5.button("Apagar", key=f"del_inv_{row['id']}"):
                cursor.execute("DELETE FROM investimentos WHERE id=?", (row["id"],))
                conn.commit()
                st.experimental_rerun()

    # -----------------------
    # GRÁFICOS OCULTOS
    # -----------------------
    with st.expander("📈 Gráficos Financeiros Combinados"):
        st.markdown("**Contas Pagas vs Pendentes por Mês**")
        resumo_contas = df_contas.groupby(['mes','pago'])['valor'].sum().unstack(fill_value=0)
        resumo_contas.rename(columns={0:'Pendente',1:'Pago'}, inplace=True)
        st.line_chart(resumo_contas)

        st.markdown("**Investimentos por Categoria por Mês**")
        resumo_inv = df_invest.groupby(['mes','categoria'])['valor'].sum().unstack(fill_value=0)
        st.line_chart(resumo_inv)

    # -----------------------
    # EXPORTAR RELATÓRIO
    # -----------------------
    st.subheader("📤 Exportar Relatório")
    relatorio = pd.concat([df_contas_mes, df_invest_mes], ignore_index=True)
    relatorio.to_excel("relatorio.xlsx", index=False)
    with open("relatorio.xlsx", "rb") as f:
        st.download_button(
            label="Baixar Relatório em Excel",
            data=f,
            file_name="relatorio_financeiro.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

else:
    st.info("Nenhuma conta ou investimento cadastrado ainda.")

