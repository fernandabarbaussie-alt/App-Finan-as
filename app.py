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

# --- UI/UX PREMIUM COM ALERTAS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #F4F7F9 !important; }
    header, footer, #MainMenu {visibility: hidden;}
    .block-container {padding: 1rem; max-width: 500px; margin: auto;}

    /* Alerta de Vencimento Hoje (Pulsante) */
    @keyframes pulse {
        0% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.02); opacity: 0.9; }
        100% { transform: scale(1); opacity: 1; }
    }
    .alert-today {
        background-color: #FFEBEE;
        border: 2px solid #D32F2F;
        color: #D32F2F;
        padding: 12px;
        border-radius: 15px;
        text-align: center;
        font-weight: 800;
        margin-bottom: 20px;
        animation: pulse 2s infinite;
        box-shadow: 0 4px 15px rgba(211, 47, 47, 0.2);
    }
    
    .badge-vence-hoje {
        background-color: #D32F2F;
        color: white;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 11px;
        font-weight: 800;
        display: inline-block;
        margin-top: 8px;
    }

    /* Cards de Resumo */
    .summary-card {
        background: linear-gradient(135deg, #001f3f 0%, #003366 100%);
        color: white; padding: 22px; border-radius: 20px;
        text-align: center; box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        margin-bottom: 25px;
    }

    /* Cards de Despesa */
    .expense-card-fernanda { border-left: 10px solid #E91E63; background: white; padding: 18px; border-radius: 18px; margin-bottom: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
    .expense-card-jonathan { border-left: 10px solid #2196F3; background: white; padding: 18px; border-radius: 18px; margin-bottom: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
    
    .card-header { display: flex; justify-content: space-between; align-items: center; }
    .card-title { font-weight: 800; font-size: 19px; color: #222; }
    .card-price { font-weight: 800; font-size: 21px; color: #000; }
    .card-date { color: #777; font-size: 13px; font-weight: 600; margin-top: 4px; }

    /* Botões Modernos */
    div.stButton > button {
        border: none !important;
        border-radius: 14px !important;
        font-weight: 700 !important;
        height: 3.8rem !important;
        width: 100% !important;
        transition: all 0.2s;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Botão Liquidar */
    div.stButton > button[key*="liq_"] {
        background-color: #E3F2FD !important; color: #1976D2 !important;
        border: 1px solid #BBDEFB !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; gap: 8px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #E0E0E0; border-radius: 15px; 
        color: #555 !important; padding: 10px 18px; font-weight: 600;
    }
    .stTabs [aria-selected="true"] { background-color: #001f3f !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES ---
def get_icon(categoria):
    icons = {"Mercado": "🛒", "Lazer": "🎡", "Saúde": "💊", "Fixas": "🏠", "Educação": "📚", "Outros": "📦"}
    return icons.get(categoria, "💰")

# --- BANCO DE DADOS ---
conn = sqlite3.connect("familybank_v22.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS contas (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, categoria TEXT, valor REAL, vencimento TEXT, pago INTEGER DEFAULT 0, responsavel TEXT, data_pagamento TEXT, comprovante TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS investimentos (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, categoria TEXT, valor REAL, data TEXT)")
conn.commit()

# --- CARGA ---
df_c = pd.read_sql("SELECT * FROM contas", conn)
df_i = pd.read_sql("SELECT * FROM investimentos", conn)
hoje = datetime.date.today()
dia_hoje_str = hoje.strftime("%d/%m")
mes_atual_str = hoje.strftime("/%m")

st.markdown("<h2 style='text-align: center; color: #001f3f; font-weight: 800;'>FamilyBank 💎</h2>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["⚡ PAINEL", "📊 DASH", "🔮 PROJ.", "📑 HIST.", "➕ NOVO"])

with tab1:
    df_aberto = df_c[df_c['pago'] == 0]
    
    # Alerta de Vencimento Hoje
    contas_hoje = df_aberto[df_aberto['vencimento'] == dia_hoje_str]
    if not contas_hoje.empty:
        st.markdown(f'<div class="alert-today">🚨 VENCENDO HOJE: {len(contas_hoje)} CONTA(S)</div>', unsafe_allow_html=True)

    # Resumo
    t_mes = df_aberto[df_aberto['vencimento'].str.contains(mes_atual_str, na=False)]['valor'].sum()
    st.markdown(f"""<div class="summary-card"><small>TOTAL EM ABERTO ({hoje.strftime('%B')})</small><div style="font-size: 34px; font-weight: 800;">R$ {t_mes:,.2f}</div></div>""", unsafe_allow_html=True)

    for resp in ["Fernanda", "Jonathan"]:
        st.markdown(f"<div style='font-weight:800; color:#555; margin-bottom:12px; font-size:14px;'>{resp.upper()}</div>", unsafe_allow_html=True)
        df_resp = df_aberto[(df_aberto['responsavel'] == resp) & (df_aberto['vencimento'].str.contains(mes_atual_str, na=False))]
        
        if df_resp.empty:
            st.info(f"Nenhuma conta pendente para {resp}.")
        else:
            for _, r in df_resp.iterrows():
                classe = "expense-card-fernanda" if resp == "Fernanda" else "expense-card-jonathan"
                vence_hoje = r['vencimento'] == dia_hoje_str
                alerta_html = '<div class="badge-vence-hoje">VENCE HOJE 🚨</div>' if vence_hoje else ''
                
                st.markdown(f"""
                    <div class="{classe}">
                        <div class="card-header">
                            <span class="card-title">{get_icon(r['categoria'])} {r['descricao']}</span>
                            <span class="card-price">R$ {r['valor']:,.2f}</span>
                        </div>
                        <div class="card-date">VENCIMENTO: {r['vencimento']}</div>
                        {alerta_html}
                    </div>
                """, unsafe_allow_html=True)
                
                comp = st.file_uploader("Anexar Comprovante", type=['png','jpg','pdf'], key=f"u_{r['id']}", label_visibility="collapsed")
                
                if st.button("LIQUIDAR ✅", key=f"liq_{r['id']}"):
                    img_data = base64.b64encode(comp.read()).decode() if comp else ""
                    cursor.execute("UPDATE contas SET pago = 1, data_pagamento = ?, comprovante = ? WHERE id = ?", (hoje.strftime("%d/%m/%Y"), img_data, r['id']))
                    conn.commit()
                    st.rerun()
                
                if st.button("REMOVER 🗑️", key=f"del_{r['id']}"):
                    cursor.execute("DELETE FROM contas WHERE id = ?", (r['id'],))
                    conn.commit()
                    st.rerun()
                st.markdown("<br>", unsafe_allow_html=True)

with tab2: # DASHBOARD
    st.markdown("<div class='section-title'>Análise Mensal</div>", unsafe_allow_html=True)
    df_pago = df_c[df_c['pago'] == 1]
    if not df_pago.empty:
        fig = px.pie(df_pago, values='valor', names='categoria', hole=.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
        
        if st.button("📄 EXPORTAR PDF COMPLETO"):
            pdf = FPDF(orientation='L')
            pdf.add_page(); pdf.set_font("Arial", 'B', 16)
            pdf.cell(280, 15, f"Relatorio FamilyBank - {hoje.strftime('%m/%Y')}", ln=True, align='C')
            pdf.set_font("Arial", '', 10)
            for _, row in df_pago.iterrows():
                pdf.cell(190, 10, f"{row['vencimento']} - {row['descricao']} - {row['responsavel']} - R$ {row['valor']:.2f}", 1, 1)
            pdf_data = pdf.output(dest='S').encode('latin-1')
            st.download_button("📥 Baixar PDF", pdf_data, "relatorio.pdf", "application/pdf")

with tab3: # PROJEÇÕES
    st.markdown("<div class='section-title'>Projeções Futuras</div>", unsafe_allow_html=True)
    for i in range(1, 6):
        d_futura = hoje + relativedelta(months=i)
        mes_f = d_futura.strftime("/%m")
        df_f = df_c[(df_c['pago'] == 0) & (df_c['vencimento'].str.contains(mes_f, na=False))]
        with st.expander(f"📅 {d_futura.strftime('%B / %Y').upper()}"):
            if df_f.empty: st.write("Tudo limpo!")
            else: st.table(df_f[['vencimento', 'descricao', 'valor', 'responsavel']])

with tab4: # HISTÓRICO
    st.markdown("<div class='section-title'>Histórico de Pagos</div>", unsafe_allow_html=True)
    df_hist = df_c[df_c['pago'] == 1].sort_values('id', ascending=False)
    busca = st.text_input("🔍 Buscar no histórico")
    if busca: df_hist = df_hist[df_hist['descricao'].str.contains(busca, case=False)]
    for _, h in df_hist.iterrows():
        with st.expander(f"✅ {h['descricao']} (R$ {h['valor']:.2f})"):
            st.write(f"Pago por: {h['responsavel']} em {h['data_pagamento']}")
            if h['comprovante']: st.image(base64.b64decode(h['comprovante']), use_container_width=True)

with tab5: # NOVO
    with st.form("add_v22"):
        st.markdown("<b>Novo Registro</b>", unsafe_allow_html=True)
        des = st.text_input("Descrição")
        cat = st.selectbox("Categoria", ["Mercado", "Lazer", "Fixas", "Saúde", "Educação", "Outros"])
        val = st.number_input("Valor", min_value=0.0)
        res = st.selectbox("Dono", ["Fernanda", "Jonathan"])
        rep = st.number_input("Repetir por quantos meses?", min_value=1, value=1)
        dat = st.date_input("Data de Vencimento")
        if st.form_submit_button("SALVAR"):
            for i in range(int(rep)):
                v_p = dat + relativedelta(months=i)
                d_p = f"{des} ({i})" if rep > 1 else des
                cursor.execute("INSERT INTO contas (descricao, categoria, valor, vencimento, responsavel) VALUES (?, ?, ?, ?, ?)", (d_p, cat, val, v_p.strftime("%d/%m"), res))
            conn.commit()
            st.rerun()
