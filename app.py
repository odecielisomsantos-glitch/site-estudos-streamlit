import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração de Layout
st.set_page_config(page_title="Equipe Atlas", page_icon="🌊", layout="wide", initial_sidebar_state="collapsed")

if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

def toggle_theme():
    st.session_state.dark_mode = not st.session_state.dark_mode

# Definição de Cores do Tema
is_dark = st.session_state.dark_mode
theme = {
    "bg": "#0E1117" if is_dark else "#FFFFFF",
    "text": "#F9FAFB" if is_dark else "#111827",
    "card": "#1F2937" if is_dark else "#F9FAFB",
    "border": "#374151" if is_dark else "#E5E7EB"
}

# 2. CSS Customizado para Header e Cards
st.markdown(f"""
    <style>
    header, footer, #MainMenu {{visibility: hidden;}}
    .stApp {{ background: {theme['bg']}; font-family: 'Inter', sans-serif; }}
    [data-testid="stSidebar"] {{ display: none; }}
    .main .block-container {{ padding: 0; max-width: 100%; }}
    .nav-main {{ position: fixed; top: 0; left: 0; width: 100%; height: 55px; background: {theme['bg']}; display: flex; align-items: center; justify-content: space-between; padding: 0 40px; z-index: 1001; border-bottom: 1px solid {theme['border']}; }}
    .metric-strip {{ margin-top: 55px; padding: 15px 40px; background: {theme['card']}; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid {theme['border']}; }}
    .main-content {{ margin-top: 20px; padding: 0 40px; }}
    
    .card {{ position: relative; padding: 18px; border-radius: 16px; border: 2px solid {theme['border']}; text-align: center; margin-bottom: 30px; height: 195px; background: {theme['card']}; }}
    .crown {{ position: absolute; top: -18px; left: 35%; font-size: 24px; animation: float 3s infinite ease-in-out; }}
    @keyframes float {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-7px) rotate(3deg); }} }}
    .av {{ width: 50px; height: 50px; background: #22D3EE; color: #083344 !important; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; font-weight: 800; }}
    .logout-btn {{ background: #EF4444; color: white !important; padding: 5px 12px; border-radius: 6px; font-weight: bold; font-size: 11px; text-decoration: none; }}
    </style>
""", unsafe_allow_html=True)

# Funções de Processamento
def clean_numeric(val):
    if pd.isna(val) or val == "" or str(val).strip() == "0%": return 0.0
    try: return float(str(val).replace('%', '').replace(',', '.').strip())
    except: return 0.0

def get_data(aba):
    conn = st.connection("gsheets", type=GSheetsConnection)
    return conn.read(worksheet=aba, ttl=0, header=None)

# --- LOGIN ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    col_l, _ = st.columns([1, 2])
    with col_l:
        with st.form("login"):
            u_in, p_in = st.text_input("Usuário").lower().strip(), st.text_input("Senha", type="password").strip()
            if st.form_submit_button("ACESSAR"):
                df_u = get_data("Usuarios").iloc[1:]
                df_u.columns = ['User', 'Pass', 'Nome', 'Func']
                m = df_u[(df_u['User'].astype(str).str.lower() == u_in) & (df_u['Pass'].astype(str) == p_in)]
                if not m.empty:
                    st.session_state.auth, st.session_state.user = True, m.iloc[0].to_dict()
                    st.rerun()
else:
    u = st.session_state.user
    p_match = str(u['Nome']).upper().split()[0]
    df_raw = get_data("DADOS-DIA")
    
    if df_raw is not None:
        # 3. RANKING (A1:B24) com Logica de Cores
        rk = df_raw.iloc[1:24, [0, 1]].dropna()
        rk.columns = ["Nome", "Meta_Str"]
        rk['Meta_Num'] = rk['Meta_Str'].apply(clean_numeric)
        rk = rk.sort_values(by='Meta_Num', ascending=False).reset_index(drop=True)

        # 4. EVOLUÇÃO (A27:AG211)
        df_hist = df_raw.iloc[26:211, 0:33].copy()
        df_hist.columns = ["Nome", "Metrica"] + [f"{i:02d}" for i in range(1, 32)]
        u_meta_row = df_hist[(df_hist['Nome'].astype(str).str.upper().str.contains(p_match)) & (df_hist['Metrica'].astype(str).str.upper() == "META")]
        
        pos = f"{rk[rk['Nome'].astype(str).str.upper().str.contains(p_match)].index[0] + 1}º" if not rk.empty else "N/A"

        # Navbar Superior
        st.markdown(f'''<div class="nav-main"><div class="brand-logo"><span style="color:#F97316; font-weight:900; font-size:22px;">ATLAS</span></div><div style="display:flex; align-items:center; gap:20px;"><div style="font-size:12px; font-weight:600;">{u["Nome"]} | 2026 ●</div><a href="/" target="_self" class="logout-btn">SAIR</a></div></div><div class="metric-strip">''', unsafe_allow_html=True)
        cs = st.columns([0.5, 1.5, 1.5, 1.5, 2.5, 0.5])
        with cs[0]: with st.popover("🔔"): st.info("Sem avisos.")
        with cs[1]: st.markdown(f'<div style="text-align:center;"><div style="font-size:10px; opacity:0.7;">SUA COLOCAÇÃO</div><div style="font-size:16px; font-weight:700;">🏆 {pos}</div></div>', unsafe_allow_html=True)
        with cs[2]: st.markdown(f'<div style="text-align:center;"><div style="font-size:10px; opacity:0.7;">PERÍODO</div><div style="font-size:16px; font-weight:700;">JANEIRO / 2026</div></div>', unsafe_allow_html=True)
        with cs[3]: st.markdown(f'<div style="text-align:center;"><div style="font-size:10px; opacity:0.7;">STATUS</div><div style="font-size:16px; font-weight:700;">🟢 ONLINE</div></div>', unsafe_allow_html=True)
        with cs[4]: st.markdown(f'<div style="text-align:center;"><div style="font-size:10px; opacity:0.7;">UNIDADE</div><div style="font-size:16px; font-weight:700;">CALL CENTER PDF</div></div>', unsafe_allow_html=True)
        with cs[5]: st.toggle("🌙", value=st.session_state.dark_mode, on_change=toggle_theme, key="t_dark")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        col_rk, col_chart = st.columns(2)
        
        with col_rk:
            st.markdown("### 🏆 Ranking da Equipe")
            # APLICAÇÃO DO PADRÃO DE CORES NO RANKING
            def style_ranking(row):
                val = clean_numeric(row['Meta_Str'])
                if val >= 90: color = 'background-color: #d1fae5; color: black' # Verde claro
                elif 70 <= val < 80: color = 'background-color: #fef3c7; color: black' # Amarelo claro
                elif val < 70: color = 'background-color: #fee2e2; color: black' # Vermelho claro
                else: color = '' # 80-89% (Branco/Cinza padrão)
                return [color] * len(row)

            st.dataframe(rk[["Nome", "Meta_Str"]].style.apply(style_ranking, axis=1), 
                         use_container_width=True, hide_index=True, height=400)
            
        with col_chart:
            st.markdown(f"### 📈 Evolução da Meta - {p_match.title()}")
            if not u_meta_row.empty:
                y_vals = [clean_numeric(v) for v in u_meta_row.iloc[0, 2:].values]
                x_days = [f"{i:02d}" for i in range(1, 32)]
                
                # GRÁFICO PRESERVADO: Laranja com Marcadores
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=x_days, y=y_vals, mode='lines+markers',
                    line=dict(color="#F97316", width=3),
                    marker=dict(size=8, color="#F97316", symbol='circle'),
                    hovertemplate='Dia %{x}<br>Valor: %{y}%<extra></extra>'
                ))
                fig.update_layout(
                    margin=dict(l=0, r=0, t=10, b=0), height=400,
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(showgrid=False, color=theme['text'], tickmode='linear'),
                    yaxis=dict(range=[0, 105], ticksuffix='%', color=theme['text'], gridcolor="rgba(0,0,0,0.1)", zeroline=False)
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # Cards Individuais com Coroa
        st.markdown("<br>### 📊 Performance Individual", unsafe_allow_html=True)
        cols_cards = st.columns(8)
        for idx, row in rk.iterrows():
            val = row['Meta_Num']
            crown = '<div class="crown">👑</div>' if val >= 80 else ''
            ini = "".join([n[0] for n in str(row['Nome']).split()[:2]]).upper()
            
            with cols_cards[idx % 8]:
                st.markdown(f'''
                    <div class="card">
                        {crown}<div class="av">{ini}</div>
                        <div style="font-size:10px; font-weight:700; height:35px; line-height:1.2; color:{theme['text']};">{" ".join(str(row["Nome"]).split()[:2])}</div>
                        <div style="font-size:22px; font-weight:800; color:#F97316;">{row["Meta_Str"]}</div>
                    </div>
                ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
