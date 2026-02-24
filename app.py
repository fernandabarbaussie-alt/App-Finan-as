import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Meu Controle Financeiro", layout="wide")

st.title("💰 Painel de Controle Financeiro")
st.markdown("---")

# 1. Sidebar para Entrada de Dados
st.sidebar.header("Novo Lançamento")
with st.sidebar.form("form_financeiro"):
    descricao = st.text_input("Descrição do gasto")
    valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
    categoria = st.selectbox("Categoria", ["Aluguel", "Alimentação", "Lazer", "Transporte", "Outros"])
    botao_adicionar = st.form_submit_button("Adicionar")

# 2. Dados de Exemplo (Para o gráfico aparecer)
# Dica: No futuro, podemos conectar isso a um arquivo Excel ou Google Sheets
dados_iniciais = {
    'Mês': ['Jan', 'Jan', 'Fev', 'Fev', 'Mar', 'Mar'],
    'Categoria': ['Alimentação', 'Lazer', 'Alimentação', 'Lazer', 'Alimentação', 'Lazer'],
    'Valor': [800, 300, 750, 450, 900, 200]
}
df = pd.DataFrame(dados_iniciais)

# 3. Layout de Colunas para Gráficos
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Distribuição por Categoria")
    fig_pizza = px.pie(df, values='Valor', names='Categoria', hole=0.3)
    st.plotly_chart(fig_pizza, use_container_width=True)

with col2:
    st.subheader("📈 Evolução Mensal")
    fig_linha = px.line(df, x='Mês', y='Valor', color='Categoria', markers=True)
    st.plotly_chart(fig_linha, use_container_width=True)

# 4. Tabela de Registros
st.subheader("📝 Últimos Lançamentos")
st.dataframe(df, use_container_width=True)
