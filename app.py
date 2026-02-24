import streamlit as st
import sqlite3
import pandas as pd
import datetime
import base64
from dateutil.relativedelta import relativedelta
import plotly.express as px
from fpdf import FPDF

# --- CONFIGURAÇÃO ---
SENHA_ACESSO = "1234" 
st.set_page_config(page_title="FamilyBank", page_icon="💍", layout="wide")

# --- UI/UX ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; background-color: #FFFFFF !important; color: #000000 !important; }
    header, footer, #MainMenu {visibility: hidden;}
    .block-container {padding-top: 1rem; max-width: 600px; margin: auto;}
    .section-title { color: #001f3f; font-weight: 900; font-size: 24px; margin-top: 20px; border-bottom: 4px solid #001f3f; padding-bottom: 5px; margin-bottom: 15px;}
    .expense-card { background: #F9F9F9; border-radius: 10px; padding: 15px; margin-bottom: 8px; border: 2px solid #000000;}
    .stButton>button { border: 2px solid #000000; border-radius: 8px; font-weight: 900; background-color: #FFFFFF; color: #000000; box-shadow: 3px 3px 0px #000000; width: 100%;}
    .metric-box { background: #001f3f; color: white; padding: 15px; border-radius: 10px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if "autenticado" not in st.session_state: st.session_state["autenticado"] = False
if not st.session_state["autenticado"]:
    st.markdown("<h2 style='text-align: center; color: #001f3f; font-weight: 900;'>🔐 FamilyBank</h2>", unsafe_allow_html=True)
    senha = st.text_input("Senha", type="password")
    if st.button("ENTRAR"):
        if senha == SENHA_ACESSO:
            st.session_state["autenticado"] = True
            st.rerun()
    st.stop()

# --- BANCO DE DADOS (v11) ---
conn = sqlite3.connect("familybank_v11.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS contas (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, categoria TEXT, valor REAL, vencimento TEXT, pago INTEGER DEFAULT 0, responsavel TEXT, data_pagamento TEXT, comprovante TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS investimentos (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, categoria TEXT, valor REAL, data TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS metas (id INTEGER PRIMARY KEY AUTOINCREMENT, objetivo TEXT, valor_alvo REAL, valor_atual REAL)")
conn.commit()

# --- CARGA DE DADOS ---
df_c = pd.read_sql("SELECT * FROM contas", conn)
df_i = pd.read_sql("SELECT * FROM investimentos", conn)
df_m = pd.read_sql("SELECT * FROM metas", conn)

hoje = datetime.date.today()
mes_atual = hoje.strftime("%m")
t_saidas_mes = df_c[(df_c['pago'] == 0) & (df_c['vencimento'].str.contains(f"/{mes_atual}"))]['valor'].sum()
t_investido = df_i['valor'].sum()

st.markdown("<h1 style='text-align: center; color: #001f3f; font-weight: 900; margin:0;'>FamilyBank</h1>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["⚡ PAINEL", "🎯 METAS", "📊 DASHBOARD", "📈 INVEST", "🔮 PROJEÇÃO", "➕ NOVO"])

with tab1:
    st.markdown(f"""<div class='metric-box'><small>PENDENTE ESTE MÊS</small><br><b style='font-size:24px;'>R$ {t_saidas_mes:,.2f}</b></div>""", unsafe_allow_html=True)
    
    # Calculadora Independência (Regra dos 4%)
    rendimento_est = (t_investido * 0.04) / 12
    custo_medio = df_c[df_c['pago']==1]['valor'].mean() if not df_c[df_c['pago']==1].empty else 1
    progresso_liberdade = min((rendimento_est / custo_medio) * 100, 100.0)
    
    st.write(f"🕊️ **Independência Financeira:** Seus investimentos pagam {progresso_liberdade:.1f}% do seu custo de vida.")
    st.progress(progresso_liberdade/100)

    for resp in ["Fernanda", "Jonathan"]:
        st.markdown(f"<div class='section-title'>{resp.upper()}</div>", unsafe_allow_html=True)
        df_p = df_c[(df_c['responsavel'] == resp) & (df_c['pago'] == 0) & (df_c['vencimento'].str.contains(f"/{mes_atual}"))]
        if df_p.empty: st.write("✓ Tudo pago.")
        else:
            for _, r in df_p.iterrows():
                st.markdown(f"<div class='expense-card'><b>{r['descricao']}</b><br><span style='color:red'>R$ {r['valor']:,.2f}</span><br><small>Venc: {r['vencimento']}</small></div>", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                comp = c1.file_uploader("Comprovante", type=['png','jpg'], key=f"f_{r['id']}")
                if c1.button("LIQUIDAR ✅", key=f"b_{r['id']}"):
                    img = base64.b64encode(comp.read()).decode() if comp else ""
                    cursor.execute("UPDATE contas SET pago = 1, data_pagamento = ?, comprovante = ? WHERE id = ?", (hoje.strftime("%d/%m/%Y"), img, r['id']))
                    conn.commit()
                    st.rerun()
                if c2.button("REMOVER 🗑️", key=f"del_{r['id']}"):
                    cursor.execute("DELETE FROM contas WHERE id = ?", (r['id'],))
                    conn.commit()
                    st.rerun()

with tab2:
    st.markdown("<div class='section-title'>NOSSAS METAS</div>", unsafe_allow_html=True)
    with st.form("nova_meta"):
        obj = st.text_input("Objetivo (ex: Viagem)")
        alvo = st.number_input("Valor Alvo R$", min_value=0.0)
        atual = st.number_input("Já temos R$", min_value=0.0)
        if st.form_submit_button("CRIAR META"):
            cursor.execute("INSERT INTO metas (objetivo, valor_alvo, valor_atual) VALUES (?, ?, ?)", (obj, alvo, atual))
            conn.commit()
            st.rerun()
    
    for _, m in df_m.iterrows():
        perc = min(m['valor_atual'] / m['valor_alvo'], 1.0) if m['valor_alvo'] > 0 else 0
        st.write(f"🚀 **{m['objetivo']}** ({perc*100:.1f}%)")
        st.progress(perc)
        st.write(f"R$ {m['valor_atual']:,.2f} de R$ {m['valor_alvo']:,.2f}")
        if st.button("Remover Meta", key=f"dm_{m['id']}"):
            cursor.execute("DELETE FROM metas WHERE id = ?", (m['id'],))
            conn.commit()
            st.rerun()

with tab3:
    st.markdown("<div class='section-title'>DASHBOARD</div>", unsafe_allow_html=True)
    if not df_c.empty:
        fig = px.pie(df_c[df_c['pago']==1], values='valor', names='categoria', hole=.4)
        st.plotly_chart(fig, use_container_width=True)
    
    # Botão Relatório PDF
    if st.button("📄 GERAR RELATÓRIO MENSAL (PDF)"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, f"Relatorio FamilyBank - {hoje.strftime('%m/%Y')}", ln=True, align='C')
        pdf.set_font("Arial", '', 12)
        pdf.cell(200, 10, f"Total Pago: R$ {df_c[df_c['pago']==1]['valor'].sum():,.2f}", ln=True)
        pdf.output("relatorio_mensal.pdf")
        with open("relatorio_mensal.pdf", "rb") as f:
            st.download_button("Baixar PDF", f, "relatorio_mensal.pdf")

with tab4:
    st.markdown("<div class='section-title'>INVESTIMENTOS</div>", unsafe_allow_html=True)
    st.metric("Patrimônio Total", f"R$ {t_investido:,.2f}")
    for cat in df_i['categoria'].unique():
        with st.expander(f"📁 {cat}"):
            df_cat = df_i[df_i['categoria'] == cat]
            for _, inv in df_cat.iterrows():
                st.write(f"{inv['descricao']}: R$ {inv['valor']:,.2f}")

with tab5:
    st.markdown("<div class='section-title'>PROJEÇÃO</div>", unsafe_allow_html=True)
    for i in range(1, 4):
        f_date = hoje + relativedelta(months=i)
        mes_f = f_date.strftime("%m")
        val_f = df_c[(df_c['pago']==0) & (df_c['vencimento'].str.contains(f"/{mes_f}"))]['valor'].sum()
        st.metric(f"Previsão {f_date.strftime('%B')}", f"R$ {val_f:,.2f}")

with tab6:
    tipo = st.radio("Tipo:", ["Saída", "Investimento"], horizontal=True)
    with st.form("main_add"):
        des = st.text_input("Descrição / Nome")
        val = st.number_input("Valor", min_value=0.0)
        dat = st.date_input("Data de Vencimento")
        if tipo == "Saída":
            res = st.selectbox("Dono", ["Fernanda", "Jonathan"])
            cat = st.selectbox("Categoria", ["Mercado", "Lazer", "Contas Fixas", "Saúde", "Outros"])
            rep = st.number_input("Parcelas (0 para à vista)", min_value=1, value=1)
        else:
            cat = st.selectbox("Tipo", ["Renda Fixa", "Cripto", "Outros"])
            res, rep = "Geral", 1
        
        if st.form_submit_button("SALVAR"):
            if tipo == "Saída":
                for i in range(int(rep)):
                    v_p = dat + relativedelta(months=i)
                    d_p = f"{des} ({i})" if rep > 1 else des
                    cursor.execute("INSERT INTO contas (descricao, categoria, valor, vencimento, responsavel) VALUES (?, ?, ?, ?, ?)", (d_p, cat, val, v_p.strftime("%d/%m"), res))
            else:
                cursor.execute("INSERT INTO investimentos (descricao, categoria, valor, data) VALUES (?, ?, ?, ?)", (des, cat, val, dat.strftime("%d/%m")))
            conn.commit()
            st.rerun()
