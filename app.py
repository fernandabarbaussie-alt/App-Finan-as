import streamlit as st
import sqlite3
import pandas as pd
import datetime
import base64
from dateutil.relativedelta import relativedelta
import plotly.express as px

# --- CONFIGURAÇÃO ---
SENHA_ACESSO = "1234" 
st.set_page_config(page_title="FamilyBank", page_icon="💍", layout="wide")

# --- UI/UX ALTO CONTRASTE ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; background-color: #FFFFFF !important; color: #000000 !important; }
    header, footer, #MainMenu {visibility: hidden;}
    .block-container {padding-top: 1rem; max-width: 600px; margin: auto;}
    .section-title { color: #001f3f; font-weight: 900; font-size: 24px; margin-top: 20px; border-bottom: 4px solid #001f3f; padding-bottom: 5px; margin-bottom: 15px;}
    .expense-card { background: #F9F9F9; border-radius: 10px; padding: 15px; margin-bottom: 8px; border: 2px solid #000000;}
    .card-price { font-size: 20px; font-weight: 900; color: #D32F2F; }
    .stTabs [data-baseweb="tab-list"] { background-color: #001f3f; border-radius: 10px; padding: 5px; }
    .stTabs [data-baseweb="tab"] { color: #FFFFFF !important; font-weight: bold; }
    .stButton>button { border: 2px solid #000000; border-radius: 8px; font-weight: 900; height: 3.5rem; background-color: #FFFFFF; color: #000000; box-shadow: 3px 3px 0px #000000; width: 100%;}
    input, select { border: 2px solid #000000 !important; border-radius: 8px !important; }
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

# --- BANCO DE DADOS (v10) ---
conn = sqlite3.connect("familybank_v10.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS contas (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        descricao TEXT, categoria TEXT, valor REAL, vencimento TEXT, 
        pago INTEGER DEFAULT 0, responsavel TEXT, data_pagamento TEXT, comprovante TEXT
    )
""")
cursor.execute("CREATE TABLE IF NOT EXISTS investimentos (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, categoria TEXT, valor REAL, data TEXT)")

# Proteção para coluna categoria nas saídas
try: cursor.execute("ALTER TABLE contas ADD COLUMN categoria TEXT DEFAULT 'Outros'")
except: pass
conn.commit()

# --- DADOS ---
df_c = pd.read_sql("SELECT * FROM contas", conn)
df_i = pd.read_sql("SELECT * FROM investimentos", conn)

hoje = datetime.date.today()
mes_atual = hoje.strftime("%m")
t_saidas_mes = df_c[(df_c['pago'] == 0) & (df_c['vencimento'].str.contains(f"/{mes_atual}"))]['valor'].sum()
t_investido = df_i['valor'].sum()

st.markdown("<h1 style='text-align: center; color: #001f3f; font-weight: 900; margin:0;'>FamilyBank</h1>", unsafe_allow_html=True)

# --- NAVEGAÇÃO ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["⚡ PAINEL", "📊 DASHBOARD", "📈 INVEST", "🔮 PROJEÇÃO", "📑 HISTÓRICO", "➕ NOVO"])

with tab1:
    st.markdown(f"""<div style="background-color:#000;padding:15px;border-radius:12px;color:white;text-align:center;border:2px solid #001f3f;margin-bottom:10px;"><div style="display:flex;justify-content:space-around;"><div><small>SAÍDAS DO MÊS</small><br><b style="font-size:22px;">R$ {t_saidas_mes:,.2f}</b></div><div style="border-left:1px solid #333;"></div><div><small>PATRIMÔNIO</small><br><b style="font-size:22px;color:#94a3b8;">R$ {t_investido:,.2f}</b></div></div></div>""", unsafe_allow_html=True)
    
    # Calendário Compacto (Item 3)
    st.markdown("##### 📅 Vencimentos da Semana")
    prox_7_dias = [(hoje + datetime.timedelta(days=d)).strftime("%d/%m") for d in range(7)]
    df_semana = df_c[(df_c['vencimento'].isin(prox_7_dias)) & (df_c['pago'] == 0)]
    if not df_semana.empty:
        st.dataframe(df_semana[['vencimento', 'descricao', 'valor']].sort_values('vencimento'), hide_index=True, use_container_width=True)
    else:
        st.write("Sem contas vencendo nos próximos 7 dias.")

    for resp in ["Fernanda", "Jonathan"]:
        st.markdown(f"<div class='section-title'>{resp.upper()}</div>", unsafe_allow_html=True)
        df_p = df_c[(df_c['responsavel'] == resp) & (df_c['pago'] == 0) & (df_c['vencimento'].str.contains(f"/{mes_atual}"))]
        if df_p.empty: st.write("✓ Tudo em dia.")
        else:
            for _, r in df_p.iterrows():
                st.markdown(f"<div class='expense-card'><div style='display:flex;justify-content:space-between;'><span class='card-desc'>{r['descricao']}</span><span class='card-price'>R$ {r['valor']:,.2f}</span></div><small>{r['categoria']} | Venc: {r['vencimento']}</small></div>", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                comp = c1.file_uploader("Comprovante", type=['png','jpg','pdf'], key=f"f_{r['id']}")
                if c1.button("LIQUIDADO ✅", key=f"b_{r['id']}"):
                    img = base64.b64encode(comp.read()).decode() if comp else ""
                    cursor.execute("UPDATE contas SET pago = 1, data_pagamento = ?, comprovante = ? WHERE id = ?", (hoje.strftime("%d/%m/%Y"), img, r['id']))
                    conn.commit()
                    st.rerun()
                if c2.button("REMOVER 🗑️", key=f"del_{r['id']}"):
                    cursor.execute("DELETE FROM contas WHERE id = ?", (r['id'],))
                    conn.commit()
                    st.rerun()

with tab2:
    st.markdown("<div class='section-title'>DASHBOARD FINANCEIRO</div>", unsafe_allow_html=True)
    # Gráfico de Pizza (Item 4)
    df_pizza = df_c[df_c['pago'] == 1] if not df_c[df_c['pago'] == 1].empty else df_c
    if not df_pizza.empty:
        fig = px.pie(df_pizza, values='valor', names='categoria', title="Onde vai o dinheiro?", 
                     color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig, use_container_width=True)
        
        # Comparativo entre Fernanda e Jonathan
        fig2 = px.bar(df_pizza, x='responsavel', y='valor', color='categoria', title="Gastos por Pessoa", barmode='stack')
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Adicione e liquide saídas para ver os gráficos.")

with tab3:
    st.markdown("<div class='section-title'>PATRIMÔNIO</div>", unsafe_allow_html=True)
    st.metric("Total Acumulado", f"R$ {t_investido:,.2f}")
    cats_inv = ["Renda Fixa", "Renda Variável", "Tesouro Direto", "Cripto", "COE", "Previdência Privada", "Outros"]
    for cat in cats_inv:
        df_cat = df_i[df_i['categoria'] == cat]
        if not df_cat.empty:
            with st.expander(f"📁 {cat.upper()} - R$ {df_cat['valor'].sum():,.2f}"):
                for _, inv in df_cat.iterrows():
                    st.write(f"**{inv['descricao']}** - R$ {inv['valor']:,.2f}")
                    if st.button("Remover", key=f"di_{inv['id']}"):
                        cursor.execute("DELETE FROM investimentos WHERE id = ?", (inv['id'],))
                        conn.commit()
                        st.rerun()

with tab4:
    st.markdown("<div class='section-title'>PROJEÇÃO FUTURA</div>", unsafe_allow_html=True)
    for i in range(1, 7):
        data_f = hoje + relativedelta(months=i)
        mes_f = data_f.strftime("%m")
        df_futuro = df_c[(df_c['pago'] == 0) & (df_c['vencimento'].str.contains(f"/{mes_f}"))]
        if not df_futuro.empty:
            with st.expander(f"📅 {data_f.strftime('%B/%Y').upper()} - R$ {df_futuro['valor'].sum():,.2f}"):
                for _, fut in df_futuro.iterrows():
                    st.write(f"{fut['responsavel']}: {fut['descricao']} - R$ {fut['valor']:,.2f}")

with tab5:
    st.markdown("<div class='section-title'>HISTÓRICO</div>", unsafe_allow_html=True)
    df_h = df_c[df_c['pago'] == 1].copy()
    for _, h in df_h.iterrows():
        with st.expander(f"{h['vencimento']} - {h['descricao']} (R$ {h['valor']:.2f})"):
            st.write(f"Pago em: {h['data_pagamento']}")
            if h['comprovante']: st.image(base64.b64decode(h['comprovante']), use_container_width=True)

with tab6:
    tipo = st.radio("Registrar:", ["Saída", "Investimento"], horizontal=True)
    with st.form("add_form", clear_on_submit=True):
        if tipo == "Saída":
            res = st.selectbox("Dono", ["Fernanda", "Jonathan"])
            cat = st.selectbox("Categoria", ["Mercado", "Lazer", "Saúde", "Moradia", "Transporte", "Educação", "Contas Fixas", "Outros"])
            des = st.text_input("Descrição")
            rep = st.number_input("Repetir por meses?", min_value=1, value=1)
        else:
            cat = st.selectbox("Tipo de Investimento", cats_inv)
            des, res, rep = st.text_input("Nome do Ativo"), "Geral", 1
        val = st.number_input("Valor R$", min_value=0.0)
        dat = st.date_input("Data de Vencimento")
        if st.form_submit_button("REGISTRAR"):
            if tipo == "Saída":
                for i in range(int(rep)):
                    v_p = dat + relativedelta(months=i)
                    d_parc = f"{des} ({i})" if rep > 1 else des
                    cursor.execute("INSERT INTO contas (descricao, categoria, valor, vencimento, responsavel) VALUES (?, ?, ?, ?, ?)", (d_parc, cat, val, v_p.strftime("%d/%m"), res))
            else:
                cursor.execute("INSERT INTO investimentos (descricao, categoria, valor, data) VALUES (?, ?, ?, ?)", (des, cat, val, dat.strftime("%d/%m")))
            conn.commit()
            st.rerun()
