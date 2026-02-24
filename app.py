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

# --- UI/UX VERTICAL (CORRIGIDO) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; background-color: #FFFFFF !important; color: #000000 !important; }
    header, footer, #MainMenu {visibility: hidden;}
    .block-container {padding: 1rem; max-width: 500px; margin: auto;}
    .section-title { color: #001f3f; font-weight: 900; font-size: 22px; margin-top: 15px; border-bottom: 3px solid #001f3f; padding-bottom: 5px; margin-bottom: 10px;}
    .expense-card { background: #F9F9F9; border-radius: 10px; padding: 15px; margin-bottom: 5px; border: 2px solid #000000;}
    
    div.stButton > button {
        display: block !important;
        width: 100% !important;
        height: 3.8rem !important;
        margin-bottom: 12px !important;
        border: 2px solid #000000 !important;
        border-radius: 10px !important;
        background-color: #FFFFFF !important;
        font-weight: 900 !important;
        box-shadow: 3px 3px 0px #000000 !important;
    }
    .stTabs [data-baseweb="tab-list"] { background-color: #001f3f; border-radius: 10px; padding: 5px; width: 100%;}
    .stTabs [data-baseweb="tab"] { color: #FFFFFF !important; font-size: 11px; padding: 0px 8px;}
    </style>
    """, unsafe_allow_html=True)

# --- BANCO DE DADOS ---
conn = sqlite3.connect("familybank_v18.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS contas (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, categoria TEXT, valor REAL, vencimento TEXT, pago INTEGER DEFAULT 0, responsavel TEXT, data_pagamento TEXT, comprovante TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS investimentos (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, categoria TEXT, valor REAL, data TEXT)")
conn.commit()

# --- CARGA DE DADOS ---
df_c = pd.read_sql("SELECT * FROM contas", conn)
df_i = pd.read_sql("SELECT * FROM investimentos", conn)
hoje = datetime.date.today()
mes_atual_str = hoje.strftime("/%m") 

st.markdown("<h1 style='text-align: center; color: #001f3f; font-weight: 900; margin:0;'>FamilyBank</h1>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["⚡ PAINEL", "📊 DASH", "📈 INVEST", "🔮 PROJ.", "📑 HIST.", "➕ NOVO"])

# --- TAB 1: PAINEL ---
with tab1:
    df_aberto = df_c[(df_c['pago'] == 0) & (df_c['vencimento'].str.contains(mes_atual_str, na=False))]
    t_mes = df_aberto['valor'].sum()
    st.markdown(f"<div style='background:#000;color:#fff;padding:15px;border-radius:12px;text-align:center;'><b>PENDENTE EM {hoje.strftime('%B').upper()}</b><br><span style='font-size:24px;'>R$ {t_mes:,.2f}</span></div>", unsafe_allow_html=True)

    for resp in ["Fernanda", "Jonathan"]:
        st.markdown(f"<div class='section-title'>{resp.upper()}</div>", unsafe_allow_html=True)
        df_resp = df_aberto[df_aberto['responsavel'] == resp]
        
        if df_resp.empty:
            st.write("✓ Nada pendente.")
        else:
            for _, r in df_resp.iterrows():
                st.markdown(f"<div class='expense-card'><b>{r['descricao']}</b><br><span style='color:#D32F2F;font-size:20px;font-weight:900;'>R$ {r['valor']:,.2f}</span><br><small>Venc: {r['vencimento']}</small></div>", unsafe_allow_html=True)
                comp = st.file_uploader("Comprovante", type=['png','jpg','pdf'], key=f"up_{r['id']}")
                if st.button("LIQUIDADO ✅", key=f_liq_{r['id']}):
                    img_data = base64.b64encode(comp.read()).decode() if comp else ""
                    cursor.execute("UPDATE contas SET pago = 1, data_pagamento = ?, comprovante = ? WHERE id = ?", (hoje.strftime("%d/%m/%Y"), img_data, r['id']))
                    conn.commit()
                    st.rerun()
                if st.button("REMOVER 🗑️", key=f_del_{r['id']}):
                    cursor.execute("DELETE FROM contas WHERE id = ?", (r['id'],))
                    conn.commit()
                    st.rerun()

# --- TAB 4: PROJEÇÕES ---
with tab4:
    st.markdown("<div class='section-title'>PROJEÇÕES FUTURAS</div>", unsafe_allow_html=True)
    st.write("Contas parceladas ou fixas para os próximos meses:")
    for i in range(1, 7):
        data_f = hoje + relativedelta(months=i)
        mes_f_str = data_f.strftime("/%m")
        df_f = df_c[(df_c['pago'] == 0) & (df_c['vencimento'].str.contains(mes_f_str, na=False))]
        
        with st.expander(f"📅 {data_f.strftime('%B / %Y').upper()}"):
            if df_f.empty:
                st.write("Nenhuma conta prevista.")
            else:
                st.metric("Total Previsto", f"R$ {df_f['valor'].sum():,.2f}")
                st.table(df_f[['vencimento', 'descricao', 'valor', 'responsavel']])

# --- TAB 5: HISTÓRICO ---
with tab5:
    st.markdown("<div class='section-title'>HISTÓRICO DE PAGAMENTOS</div>", unsafe_allow_html=True)
    df_historico = df_c[df_c['pago'] == 1]
    
    if df_historico.empty:
        st.info("O histórico aparecerá aqui após a primeira baixa.")
    else:
        busca = st.text_input("🔍 Pesquisar despesa...")
        if busca:
            df_historico = df_historico[df_historico['descricao'].str.contains(busca, case=False, na=False)]
        
        for _, h in df_historico.sort_values('id', ascending=False).iterrows():
            with st.expander(f"{h['vencimento']} - {h['descricao']}"):
                st.write(f"**Pago por:** {h['responsavel']}")
                st.write(f"**Valor:** R$ {h['valor']:.2f}")
                st.write(f"**Data da Baixa:** {h['data_pagamento']}")
                if h['comprovante']:
                    st.image(base64.b64decode(h['comprovante']), use_container_width=True)
                if st.button("ESTORNAR ↩️", key=f"est_{h['id']}"):
                    cursor.execute("UPDATE contas SET pago = 0, data_pagamento = NULL, comprovante = NULL WHERE id = ?", (h['id'],))
                    conn.commit()
                    st.rerun()

# --- TAB 6: NOVO ---
with tab6:
    with st.form("form_v18", clear_on_submit=True):
        tipo = st.radio("Tipo:", ["Saída", "Investimento"], horizontal=True)
        des = st.text_input("Nome")
        cat = st.selectbox("Categoria", ["Mercado", "Lazer", "Fixas", "Saúde", "Outros"])
        val = st.number_input("Valor", min_value=0.0)
        dat = st.date_input("Vencimento")
        res = st.selectbox("Dono", ["Fernanda", "Jonathan"])
        rep = st.number_input("Parcelas", min_value=1, value=1)
        if st.form_submit_button("REGISTRAR"):
            for i in range(int(rep)):
                v_p = dat + relativedelta(months=i)
                d_p = f"{des} ({i})" if rep > 1 else des
                cursor.execute("INSERT INTO contas (descricao, categoria, valor, vencimento, responsavel) VALUES (?, ?, ?, ?, ?)", (d_p, cat, val, v_p.strftime("%d/%m"), res))
            conn.commit()
            st.rerun()
