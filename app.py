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

# --- UI/UX VERTICAL PARA CELULAR ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; background-color: #FFFFFF !important; color: #000000 !important; }
    header, footer, #MainMenu {visibility: hidden;}
    .block-container {padding: 1rem; max-width: 500px; margin: auto;}
    .section-title { color: #001f3f; font-weight: 900; font-size: 22px; margin-top: 15px; border-bottom: 3px solid #001f3f; padding-bottom: 5px;}
    .expense-card { background: #F9F9F9; border-radius: 10px; padding: 15px; margin-bottom: 5px; border: 2px solid #000000;}
    .card-price { font-size: 20px; font-weight: 900; color: #D32F2F; }
    
    /* BOTÕES VERTICAIS LARGOS */
    .stButton>button { 
        border: 2px solid #000000; 
        border-radius: 8px; 
        font-weight: 900; 
        height: 3.8rem; 
        background-color: #FFFFFF; 
        color: #000000; 
        box-shadow: 3px 3px 0px #000000; 
        width: 100% !important; 
        margin-bottom: 12px !important;
    }
    .stTabs [data-baseweb="tab-list"] { background-color: #001f3f; border-radius: 10px; padding: 5px; width: 100%;}
    .stTabs [data-baseweb="tab"] { color: #FFFFFF !important; font-size: 11px; padding: 0px 8px;}
    </style>
    """, unsafe_allow_html=True)

# --- BANCO DE DADOS ---
conn = sqlite3.connect("familybank_v14.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS contas (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, categoria TEXT, valor REAL, vencimento TEXT, pago INTEGER DEFAULT 0, responsavel TEXT, data_pagamento TEXT, comprovante TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS investimentos (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, categoria TEXT, valor REAL, data TEXT)")
conn.commit()

# --- DADOS ---
df_c = pd.read_sql("SELECT * FROM contas", conn)
df_i = pd.read_sql("SELECT * FROM investimentos", conn)
hoje = datetime.date.today()
mes_atual = hoje.strftime("%m")

# --- HEADER ---
st.markdown("<h1 style='text-align: center; color: #001f3f; font-weight: 900; margin:0;'>FamilyBank</h1>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["⚡ PAINEL", "📊 DASH", "📈 INVEST", "🔮 PROJ.", "📑 HIST.", "➕ NOVO"])

with tab1:
    # Resumo do Mês
    t_mes = df_c[(df_c['pago'] == 0) & (df_c['vencimento'].str.contains(f"/{mes_atual}"))]['valor'].sum()
    t_inv = df_i['valor'].sum()
    st.markdown(f"<div style='background:#000;color:#fff;padding:10px;border-radius:10px;text-align:center;'><b>PENDENTE NO MÊS</b><br><span style='font-size:20px;'>R$ {t_mes:,.2f}</span><br><small>INVESTIDO: R$ {t_inv:,.2f}</small></div>", unsafe_allow_html=True)

    for resp in ["Fernanda", "Jonathan"]:
        st.markdown(f"<div class='section-title'>{resp.upper()}</div>", unsafe_allow_html=True)
        # Filtra apenas o mês atual para o painel
        df_p = df_c[(df_c['responsavel'] == resp) & (df_c['pago'] == 0) & (df_c['vencimento'].str.contains(f"/{mes_atual}"))]
        
        if df_p.empty:
            st.write("✓ Tudo em dia este mês.")
        else:
            for _, r in df_p.iterrows():
                st.markdown(f"<div class='expense-card'><b>{r['descricao']}</b><br><span class='card-price'>R$ {r['valor']:,.2f}</span><br><small>Venc: {r['vencimento']}</small></div>", unsafe_allow_html=True)
                
                # Elementos Verticais
                comp_file = st.file_uploader("Subir Comprovante", type=['png','jpg','pdf'], key=f"f_{r['id']}")
                
                if st.button("LIQUIDADO ✅", key=f"b_{r['id']}"):
                    img_data = base64.b64encode(comp_file.read()).decode() if comp_file else ""
                    cursor.execute("UPDATE contas SET pago = 1, data_pagamento = ?, comprovante = ? WHERE id = ?", (hoje.strftime("%d/%m/%Y"), img_data, r['id']))
                    conn.commit()
                    st.rerun()
                
                if st.button("REMOVER 🗑️", key=f"del_{r['id']}"):
                    cursor.execute("DELETE FROM contas WHERE id = ?", (r['id'],))
                    conn.commit()
                    st.rerun()

with tab2:
    st.markdown("<div class='section-title'>DASHBOARD</div>", unsafe_allow_html=True)
    df_pago = df_c[df_c['pago'] == 1]
    if not df_pago.empty:
        fig = px.pie(df_pago, values='valor', names='categoria', hole=.4, title="Gastos por Categoria")
        st.plotly_chart(fig, use_container_width=True)
        
        # --- GERADOR DE PDF PREENCHIDO ---
        if st.button("📄 GERAR RELATÓRIO PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 15, f"Relatorio FamilyBank - {hoje.strftime('%m/%Y')}", ln=True, align='C')
            pdf.ln(5)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 10, f"Total Pago: R$ {df_pago['valor'].sum():,.2f}", ln=True)
            pdf.ln(5)
            
            # Cabeçalho
            pdf.set_fill_color(0, 31, 63)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(30, 10, "Venc.", 1, 0, 'C', True)
            pdf.cell(80, 10, "Descricao", 1, 0, 'C', True)
            pdf.cell(40, 10, "Quem", 1, 0, 'C', True)
            pdf.cell(40, 10, "Valor", 1, 1, 'C', True)
            
            # Linhas
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", '', 10)
            for _, row in df_pago.iterrows():
                pdf.cell(30, 10, str(row['vencimento']), 1)
                pdf.cell(80, 10, str(row['descricao'])[:35], 1)
                pdf.cell(40, 10, str(row['responsavel']), 1)
                pdf.cell(40, 10, f"R$ {row['valor']:.2f}", 1, 1)
            
            pdf_data = pdf.output(dest='S').encode('latin-1')
            st.download_button("📥 Baixar PDF Agora", pdf_data, f"Relatorio_{hoje.strftime('%m_%Y')}.pdf", "application/pdf")
    else:
        st.info("Liquide contas para ver os gráficos e gerar relatórios.")

with tab3:
    st.markdown("<div class='section-title'>PATRIMÔNIO</div>", unsafe_allow_html=True)
    st.metric("Total Investido", f"R$ {t_inv:,.2f}")
    if not df_i.empty:
        for cat in df_i['categoria'].unique():
            with st.expander(f"📁 {cat.upper()}"):
                df_sub = df_i[df_i['categoria'] == cat]
                for _, inv in df_sub.iterrows():
                    st.write(f"**{inv['descricao']}**: R$ {inv['valor']:,.2f}")
                    if st.button("Excluir", key=f"inv_{inv['id']}"):
                        cursor.execute("DELETE FROM investimentos WHERE id = ?", (inv['id'],))
                        conn.commit()
                        st.rerun()

with tab4:
    st.markdown("<div class='section-title'>PROJEÇÕES FUTURAS</div>", unsafe_allow_html=True)
    # Mostra meses 1 a 6 a frente
    for i in range(1, 7):
        data_f = hoje + relativedelta(months=i)
        mes_f = data_f.strftime("%m")
        df_f = df_c[(df_c['pago'] == 0) & (df_c['vencimento'].str.contains(f"/{mes_f}"))]
        if not df_f.empty:
            with st.expander(f"📅 {data_f.strftime('%B/%Y').upper()} - R$ {df_f['valor'].sum():,.2f}"):
                for _, fut in df_f.iterrows():
                    st.write(f"{fut['responsavel']}: {fut['descricao']} - R$ {fut['valor']:,.2f}")

with tab5:
    st.markdown("<div class='section-title'>HISTÓRICO</div>", unsafe_allow_html=True)
    if not df_pago.empty:
        for _, h in df_pago.sort_values('id', ascending=False).iterrows():
            with st.expander(f"{h['vencimento']} - {h['descricao']}"):
                st.write(f"**Valor:** R$ {h['valor']:.2f} | **Quem:** {h['responsavel']}")
                st.write(f"**Pago em:** {h['data_pagamento']}")
                if h['comprovante']:
                    st.image(base64.b64decode(h['comprovante']), caption="Comprovante", use_container_width=True)
    else:
        st.write("Nenhum registro no histórico.")

with tab6:
    with st.form("form_novo", clear_on_submit=True):
        tipo = st.radio("Registrar:", ["Saída", "Investimento"], horizontal=True)
        des = st.text_input("Descrição / Nome")
        cat = st.selectbox("Categoria", ["Mercado", "Lazer", "Contas Fixas", "Saúde", "Educação", "Outros"])
        val = st.number_input("Valor R$", min_value=0.0)
        dat = st.date_input("Data de Vencimento")
        res = st.selectbox("Dono", ["Fernanda", "Jonathan"])
        rep = st.number_input("Parcelas (repetir meses)", min_value=1, value=1)
        
        if st.form_submit_button("REGISTRAR"):
            if tipo == "Saída":
                for i in range(int(rep)):
                    v_p = dat + relativedelta(months=i)
                    d_p = f"{des} ({i})" if rep > 1 else des
                    cursor.execute("INSERT INTO contas (descricao, categoria, valor, vencimento, responsavel) VALUES (?, ?, ?, ?, ?)", (d_p, cat, val, v_p.strftime("%d/%m"), res))
            else:
                cursor.execute("INSERT INTO investimentos (descricao, categoria, valor, data) VALUES (?, ?, ?, ?)", (des, cat, val, dat.strftime("%d/%m")))
            conn.commit()
            st.rerun()

