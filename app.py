import streamlit as st
import sqlite3
import pandas as pd
import datetime
import base64
from dateutil.relativedelta import relativedelta
import plotly.express as px
from fpdf import FPDF

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="FamilyBank", page_icon="💎", layout="wide")

# --- UI/UX PREMIUM ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #F4F7F9 !important; }
    header, footer, #MainMenu {visibility: hidden;}
    .block-container {padding: 1rem; max-width: 500px; margin: auto;}

    @keyframes pulse {
        0% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.02); opacity: 0.9; }
        100% { transform: scale(1); opacity: 1; }
    }
    .alert-today {
        background-color: #FFEBEE; border: 2px solid #D32F2F; color: #D32F2F;
        padding: 12px; border-radius: 15px; text-align: center; font-weight: 800;
        margin-bottom: 20px; animation: pulse 2s infinite;
    }
    
    .summary-card {
        background: linear-gradient(135deg, #001f3f 0%, #003366 100%);
        color: white; padding: 22px; border-radius: 20px;
        text-align: center; box-shadow: 0 10px 20px rgba(0,0,0,0.1); margin-bottom: 25px;
    }

    .expense-card-fernanda { border-left: 10px solid #E91E63; background: white; padding: 18px; border-radius: 18px; margin-bottom: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
    .expense-card-jonathan { border-left: 10px solid #2196F3; background: white; padding: 18px; border-radius: 18px; margin-bottom: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
    
    .card-header { display: flex; justify-content: space-between; align-items: center; }
    .card-title { font-weight: 800; font-size: 19px; color: #222; }
    .card-price { font-weight: 800; font-size: 21px; color: #000; }
    
    div.stButton > button {
        border: none !important; border-radius: 14px !important;
        font-weight: 700 !important; height: 3.8rem !important; width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES ---
def get_icon(categoria):
    icons = {"Mercado": "🛒", "Lazer": "🎡", "Saúde": "💊", "Fixas": "🏠", "Educação": "📚", "Outros": "📦"}
    return icons.get(categoria, "💰")

# --- BANCO DE DADOS ---
conn = sqlite3.connect("familybank_v23.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS contas (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, categoria TEXT, valor REAL, vencimento TEXT, pago INTEGER DEFAULT 0, responsavel TEXT, data_pagamento TEXT, comprovante TEXT)")
conn.commit()

df_c = pd.read_sql("SELECT * FROM contas", conn)
hoje = datetime.date.today()
dia_hoje_str = hoje.strftime("%d/%m")
mes_atual_str = hoje.strftime("/%m")

st.markdown("<h2 style='text-align: center; color: #001f3f; font-weight: 800;'>FamilyBank 💎</h2>", unsafe_allow_html=True)
tab1, tab2, tab3, tab4, tab5 = st.tabs(["⚡ PAINEL", "📊 DASH", "🔮 PROJ.", "📑 HIST.", "➕ NOVO"])

with tab1:
    df_aberto = df_c[df_c['pago'] == 0]
    contas_hoje = df_aberto[df_aberto['vencimento'] == dia_hoje_str]
    if not contas_hoje.empty:
        st.markdown(f'<div class="alert-today">🚨 VENCENDO HOJE: {len(contas_hoje)} CONTA(S)</div>', unsafe_allow_html=True)

    t_mes = df_aberto[df_aberto['vencimento'].str.contains(mes_atual_str, na=False)]['valor'].sum()
    st.markdown(f"""<div class="summary-card"><small>PENDENTE ({hoje.strftime('%B')})</small><div style="font-size: 34px; font-weight: 800;">R$ {t_mes:,.2f}</div></div>""", unsafe_allow_html=True)

    for resp in ["Fernanda", "Jonathan"]:
        st.markdown(f"<div style='font-weight:800; color:#555; margin-bottom:12px;'>{resp.upper()}</div>", unsafe_allow_html=True)
        df_resp = df_aberto[(df_aberto['responsavel'] == resp) & (df_aberto['vencimento'].str.contains(mes_atual_str, na=False))]
        if df_resp.empty:
            st.info(f"Tudo em dia!")
        else:
            for _, r in df_resp.iterrows():
                classe = "expense-card-fernanda" if resp == "Fernanda" else "expense-card-jonathan"
                st.markdown(f"""<div class="{classe}"><div class="card-header"><span class="card-title">{get_icon(r['categoria'])} {r['descricao']}</span><span class="card-price">R$ {r['valor']:,.2f}</span></div><div style="color:#777; font-size:13px; font-weight:600;">VENCIMENTO: {r['vencimento']}</div></div>""", unsafe_allow_html=True)
                comp = st.file_uploader("Anexar", type=['png','jpg','pdf'], key=f"u_{r['id']}", label_visibility="collapsed")
                if st.button("LIQUIDAR ✅", key=f"liq_{r['id']}"):
                    img_data = base64.b64encode(comp.read()).decode() if comp else ""
                    cursor.execute("UPDATE contas SET pago = 1, data_pagamento = ?, comprovante = ? WHERE id = ?", (hoje.strftime("%d/%m/%Y"), img_data, r['id']))
                    conn.commit()
                    st.rerun()
                st.markdown("<br>", unsafe_allow_html=True)

with tab2:
    st.markdown("<div class='section-title'>Análise</div>", unsafe_allow_html=True)
    df_pago = df_c[df_c['pago'] == 1]
    if not df_pago.empty:
        fig = px.pie(df_pago, values='valor', names='categoria', hole=.4)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("<div class='section-title'>Projeções</div>", unsafe_allow_html=True)
    for i in range(1, 6):
        d_f = hoje + relativedelta(months=i)
        df_f = df_c[(df_c['pago'] == 0) & (df_c['vencimento'].str.contains(d_f.strftime("/%m"), na=False))]
        with st.expander(f"📅 {d_f.strftime('%B / %Y').upper()}"):
            if not df_f.empty:
                # Formatando a tabela de projeção também
                df_exibir = df_f[['vencimento', 'descricao', 'valor', 'responsavel']].copy()
                df_exibir['valor'] = df_exibir['valor'].map('R$ {:,.2f}'.format)
                st.table(df_exibir)

with tab4:
    st.markdown("<div class='section-title'>Histórico de Pagos</div>", unsafe_allow_html=True)
    df_hist = df_c[df_c['pago'] == 1].sort_values('id', ascending=False)
    busca = st.text_input("🔍 Buscar no histórico")
    if busca: df_hist = df_hist[df_hist['descricao'].str.contains(busca, case=False)]
    
    for _, h in df_hist.iterrows():
        # AQUI ESTÁ O AJUSTE DE 2 CASAS DECIMAIS NO TÍTULO
        valor_formatado = f"{h['valor']:,.2f}"
        with st.expander(f"✅ {h['descricao']} (R$ {valor_formatado})"):
            st.write(f"**Pago por:** {h['responsavel']} em {h['data_pagamento']}")
            if h['comprovante']: st.image(base64.b64decode(h['comprovante']), use_container_width=True)

with tab5:
    with st.form("add_v23"):
        st.markdown("<b>Novo Registro</b>", unsafe_allow_html=True)
        des = st.text_input("Descrição")
        cat = st.selectbox("Categoria", ["Mercado", "Lazer", "Fixas", "Saúde", "Educação", "Outros"])
        val = st.number_input("Valor", min_value=0.0, step=0.01)
        res = st.selectbox("Dono", ["Fernanda", "Jonathan"])
        rep = st.number_input("Repetir meses", min_value=1, value=1)
        dat = st.date_input("Vencimento")
        if st.form_submit_button("SALVAR"):
            for i in range(int(rep)):
                v_p = dat + relativedelta(months=i)
                d_p = f"{des} ({i})" if rep > 1 else des
                cursor.execute("INSERT INTO contas (descricao, categoria, valor, vencimento, responsavel) VALUES (?, ?, ?, ?, ?)", (d_p, cat, val, v_p.strftime("%d/%m"), res))
            conn.commit()
            st.rerun()
