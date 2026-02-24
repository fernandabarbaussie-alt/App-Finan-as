import streamlit as st
import sqlite3
import pandas as pd
import datetime
import io

# --- CONFIGURAÇÃO ELITE PRO ---
st.set_page_config(
    page_title="Elite Finance Pro", 
    page_icon="💳", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- UI/UX PREMIUM (CSS INJECTION) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;500;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #0A0E14; 
        color: #E2E8F0;
    }

    header, footer, #MainMenu {visibility: hidden;}
    .block-container {padding-top: 1.5rem; max-width: 600px; margin: auto;}

    /* Cards de Resumo */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.01) 100%);
        border: 1px solid rgba(0, 255, 163, 0.2);
        backdrop-filter: blur(15px);
        padding: 20px;
        border-radius: 24px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }

    div[data-testid="stMetricValue"] {
        color: #00FFA3 !important;
        font-weight: 800;
        font-size: 1.8rem !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #141B26;
        padding: 8px;
        border-radius: 20px;
        border: 1px solid #1E293B;
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #94A3B8;
        border-radius: 15px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00FFA3 !important;
        color: #050505 !important;
    }

    /* Botões */
    .stButton>button {
        background: linear-gradient(90deg, #00FFA3 0%, #00D1FF 100%);
        color: #000;
        border: none;
        border-radius: 16px;
        font-weight: 800;
        height: 3.5rem;
        width: 100%;
        transition: 0.3s;
    }

    /* Botão de Apagar (Danger Zone) */
    .btn-danger>button {
        background: linear-gradient(90deg, #FF3366 0%, #FF0000 100%) !important;
        color: white !important;
    }

    .expense-card {
        background: #141B26;
        border-radius: 18px;
        padding: 18px;
        margin-bottom: 12px;
        border: 1px solid #1E293B;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-left: 5px solid #FF3366;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BANCO DE DADOS ---
conn = sqlite3.connect("financas_elite.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS contas (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, valor REAL, vencimento TEXT, pago INTEGER DEFAULT 0)")
cursor.execute("CREATE TABLE IF NOT EXISTS investimentos (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, valor REAL, data TEXT, categoria TEXT)")
conn.commit()

# --- HEADER ---
st.markdown("<p style='text-align: center; color: #00FFA3; font-weight: 800; font-size: 26px; margin-bottom: 0;'>PRIVATE<span style='color: white;'>BANKING</span></p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94A3B8; font-size: 11px; margin-top: 0; letter-spacing: 2px;'>ELITE DATA MANAGEMENT</p>", unsafe_allow_html=True)

tab_dash, tab_lista, tab_novo, tab_config = st.tabs(["⚡ DASH", "📑 LISTA", "💎 NOVO", "⚙️ ADM"])

df_c = pd.read_sql("SELECT * FROM contas", conn)
df_i = pd.read_sql("SELECT * FROM investimentos", conn)

with tab_dash:
    c1, c2 = st.columns(2)
    pendente = df_c[df_c['pago'] == 0]['valor'].sum()
    investido = df_i['valor'].sum()
    c1.metric("A PAGAR", f"R$ {pendente:,.2f}")
    c2.metric("INVESTIDO", f"R$ {investido:,.2f}")

    st.markdown("<br><p style='color: #94A3B8; font-weight: 600; font-size: 14px;'>PENDÊNCIAS</p>", unsafe_allow_html=True)
    contas_p = df_c[df_c['pago'] == 0]
    if contas_p.empty:
        st.success("Tudo em ordem! ✨")
    else:
        for _, r in contas_p.iterrows():
            st.markdown(f"<div class='expense-card'><div><span style='color: white; font-weight: 600;'>{r['descricao']}</span><br><span style='color: #64748B; font-size: 12px;'>Venc: {r['vencimento']}</span></div><div style='color: #FF3366; font-weight: 800;'>R$ {r['valor']:,.2f}</div></div>", unsafe_allow_html=True)

with tab_lista:
    st.markdown("### Histórico Completo")
    if not df_c.empty:
        st.dataframe(df_c[['descricao', 'valor', 'vencimento', 'pago']], use_container_width=True, hide_index=True)
        
        # --- BOTÃO DE EXPORTAÇÃO ---
        buffer = io.BytesIO()
        df_c.to_excel(buffer, index=False, engine='openpyxl')
        st.download_button(
            label="📤 Baixar Relatório Excel",
            data=buffer.getvalue(),
            file_name=f"Relatorio_Elite_{datetime.date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("Nenhum dado para exibir.")

with tab_novo:
    with st.form("form_v4", clear_on_submit=True):
        tipo = st.selectbox("Tipo", ["Conta", "Investimento"])
        desc = st.text_input("Descrição")
        val = st.number_input("Valor", min_value=0.0)
        dt = st.date_input("Data", datetime.date.today())
        if st.form_submit_button("REGISTRAR"):
            if tipo == "Conta":
                cursor.execute("INSERT INTO contas (descricao, valor, vencimento) VALUES (?, ?, ?)", (desc, val, dt.strftime("%d/%m")))
            else:
                cursor.execute("INSERT INTO investimentos (descricao, valor, data, categoria) VALUES (?, ?, ?, ?)", (desc, val, dt.strftime("%d/%m"), "Geral"))
            conn.commit()
            st.balloons()
            st.rerun()

with tab_config:
    st.markdown("### Zona de Risco")
    st.warning("As ações abaixo são irreversíveis.")
    
    # --- BOTÃO DE APAGAR COM CONFIRMAÇÃO ---
    confirmar = st.checkbox("Eu desejo apagar todos os dados permanentemente")
    st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
    if st.button("🚨 LIMPAR BANCO DE DADOS"):
        if confirmar:
            cursor.execute("DELETE FROM contas")
            cursor.execute("DELETE FROM investimentos")
            conn.commit()
            st.success("Dados eliminados.")
            st.rerun()
        else:
            st.error("Marque a caixa de confirmação primeiro.")
    st.markdown('</div>', unsafe_allow_html=True)
