import streamlit as st
import sqlite3
import pandas as pd
import datetime
import base64
from dateutil.relativedelta import relativedelta

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

# --- BANCO DE DADOS ---
conn = sqlite3.connect("familybank_v8.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS contas (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, valor REAL, vencimento TEXT, pago INTEGER DEFAULT 0, responsavel TEXT, data_pagamento TEXT, comprovante TEXT, mes_ref TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS investimentos (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, categoria TEXT, valor REAL, data TEXT)")
conn.commit()

# --- DADOS ---
df_c = pd.read_sql("SELECT * FROM contas", conn)
df_i = pd.read_sql("SELECT * FROM investimentos", conn)

# Filtro de Mês Atual para o Painel
mes_atual = datetime.date.today().strftime("%m")
t_saidas_mes = df_c[(df_c['pago'] == 0) & (df_c['vencimento'].str.contains(f"/{mes_atual}"))]['valor'].sum()
t_investido = df_i['valor'].sum()

st.markdown("<h1 style='text-align: center; color: #001f3f; font-weight: 900; margin:0;'>FamilyBank</h1>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["⚡ PAINEL", "📈 INVEST", "🔮 PROJEÇÃO", "📑 HISTÓRICO", "➕ NOVO"])

with tab1:
    st.markdown(f"""<div style="background-color:#000;padding:15px;border-radius:12px;color:white;text-align:center;border:2px solid #001f3f;margin-bottom:10px;"><div style="display:flex;justify-content:space-around;"><div><small>SAÍDAS DO MÊS</small><br><b style="font-size:22px;">R$ {t_saidas_mes:,.2f}</b></div><div style="border-left:1px solid #333;"></div><div><small>PATRIMÔNIO</small><br><b style="font-size:22px;color:#94a3b8;">R$ {t_investido:,.2f}</b></div></div></div>""", unsafe_allow_html=True)
    
    for resp in ["Fernanda", "Jonathan"]:
        st.markdown(f"<div class='section-title'>{resp.upper()}</div>", unsafe_allow_html=True)
        # MOSTRA APENAS O QUE VENCE NO MÊS ATUAL
        df_p = df_c[(df_c['responsavel'] == resp) & (df_c['pago'] == 0) & (df_c['vencimento'].str.contains(f"/{mes_atual}"))]
        
        if df_p.empty: st.write("✓ Tudo em dia este mês.")
        else:
            for _, r in df_p.iterrows():
                st.markdown(f"<div class='expense-card'><div style='display:flex;justify-content:space-between;'><span class='card-desc'>{r['descricao']}</span><span class='card-price'>R$ {r['valor']:,.2f}</span></div><small>Vencimento: {r['vencimento']}</small></div>", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                foto = c1.file_uploader("Recibo", type=['png','jpg','pdf'], key=f"f_{r['id']}")
                if c1.button("LIQUIDADO ✅", key=f"b_{r['id']}"):
                    img_str = base64.b64encode(foto.read()).decode() if foto else ""
                    cursor.execute("UPDATE contas SET pago = 1, data_pagamento = ?, comprovante = ? WHERE id = ?", (datetime.date.today().strftime("%d/%m/%Y"), img_str, r['id']))
                    conn.commit()
                    st.rerun()
                if c2.button("REMOVER 🗑️", key=f"del_{r['id']}"):
                    cursor.execute("DELETE FROM contas WHERE id = ?", (r['id'],))
                    conn.commit()
                    st.rerun()

with tab3:
    st.markdown("<div class='section-title'>PROJEÇÃO FUTURA</div>", unsafe_allow_html=True)
    hoje = datetime.date.today()
    for i in range(1, 7): # Próximos 6 meses (excluindo o atual)
        data_f = hoje + relativedelta(months=i)
        mes_f_str = data_f.strftime("%m")
        df_futuro = df_c[(df_c['pago'] == 0) & (df_c['vencimento'].str.contains(f"/{mes_f_str}"))]
        if not df_futuro.empty:
            with st.expander(f"📅 {data_f.strftime('%B/%Y').upper()} - Total: R$ {df_futuro['valor'].sum():,.2f}"):
                for _, fut in df_futuro.iterrows():
                    st.write(f"**{fut['responsavel']}**: {fut['descricao']} - R$ {fut['valor']:,.2f} ({fut['vencimento']})")

with tab5:
    tipo = st.radio("Registrar:", ["Saída", "Investimento"], horizontal=True)
    with st.form("add_form", clear_on_submit=True):
        if tipo == "Saída":
            res = st.selectbox("Responsável", ["Fernanda", "Jonathan"])
            des = st.text_input("Descrição")
            rep = st.number_input("Repetir por meses?", min_value=1, value=1)
        else:
            cat_inv = st.selectbox("Tipo:", ["Renda Fixa", "Renda Variável", "Tesouro Direto", "Cripto", "COE", "Previdência Privada", "Outros"])
            des, res, rep = st.text_input("Título"), "Geral", 1
        val = st.number_input("Valor R$", min_value=0.0)
        dat = st.date_input("Data de Vencimento")
        if st.form_submit_button("REGISTRAR"):
            if tipo == "Saída":
                for i in range(int(rep)):
                    v_p = dat + relativedelta(months=i) # MANTÉM O MESMO DIA, MUDA O MÊS
                    cursor.execute("INSERT INTO contas (descricao, valor, vencimento, responsavel) VALUES (?, ?, ?, ?)", (des, val, v_p.strftime("%d/%m"), res))
            else:
                cursor.execute("INSERT INTO investimentos (descricao, categoria, valor, data) VALUES (?, ?, ?, ?)", (des, cat_inv, val, dat.strftime("%d/%m")))
            conn.commit()
            st.rerun()
