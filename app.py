import streamlit as st
import time
import calendar
import json
import os
from datetime import datetime

# --- Configuração Inicial ---
st.set_page_config(page_title="StudyHub Pro", page_icon="🎓", layout="wide")

# ==========================================
# 🔐 SISTEMA DE LOGIN (NOVO)
# ==========================================

# Credenciais Definidas
CREDENCIAIS = {
    "Odecielisom": "Fernanda",
    "Fernanda": "Odecielisom"
}

# Inicializa estado de login
if 'logado' not in st.session_state:
    st.session_state.logado = False
if 'usuario_atual' not in st.session_state:
    st.session_state.usuario_atual = ""

def verificar_login():
    """Verifica usuário e senha"""
    user = st.session_state.input_usuario
    pwd = st.session_state.input_senha
    
    if user in CREDENCIAIS and CREDENCIAIS[user] == pwd:
        st.session_state.logado = True
        st.session_state.usuario_atual = user
    else:
        st.session_state.logado = False
        st.error("Usuário ou Senha incorretos")

# SE NÃO ESTIVER LOGADO, MOSTRA TELA DE LOGIN E PARA TUDO
if not st.session_state.logado:
    st.markdown("""
    <style>
        .login-box {
            max-width: 400px;
            margin: 100px auto;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            background-color: white;
            text-align: center;
        }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='text-align: center;'><h1>🔐 Acesso Restrito</h1><p>StudyHub Pro</p></div>", unsafe_allow_html=True)
        st.text_input("Usuário", key="input_usuario")
        st.text_input("Senha", type="password", key="input_senha")
        st.button("Entrar", on_click=verificar_login, type="primary", use_container_width=True)
    
    # O COMANDO MÁGICO: Para a execução aqui se não estiver logado
    st.stop()

# ==========================================
# 🚀 APLICAÇÃO PRINCIPAL (SÓ CARREGA SE LOGADO)
# ==========================================

# --- ARQUIVO DE BANCO DE DADOS ---
# Dica: No futuro podemos criar um arquivo diferente para cada usuário
ARQUIVO_DB = "dados_estudos.json"

# --- Funções de Persistência ---
def carregar_dados():
    if not os.path.exists(ARQUIVO_DB):
        return {"materias": {}, "historico": {}, "ciclo": []}
    try:
        with open(ARQUIVO_DB, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"materias": {}, "historico": {}, "ciclo": []}

def salvar_dados():
    dados = {
        "materias": st.session_state.materias,
        "historico": st.session_state.historico_estudos,
        "ciclo": st.session_state.ciclo_estudos
    }
    with open(ARQUIVO_DB, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# --- Inicialização ---
if 'dados_carregados' not in st.session_state:
    db = carregar_dados()
    st.session_state.materias = db.get("materias", {})
    st.session_state.historico_estudos = db.get("historico", {})
    st.session_state.ciclo_estudos = db.get("ciclo", [])
    st.session_state.dados_carregados = True

if 'sessao_estudo' not in st.session_state: st.session_state.sessao_estudo = None 

# --- CSS ---
st.markdown("""
<style>
    .stSelectbox label { display: none; }
    div[data-testid="stExpander"] { border: 1px solid #e2e8f0; border-radius: 8px; }
    .progress-bg { background-color: #f1f3f5; border-radius: 10px; height: 10px; width: 100%; margin: 5px 0; }
    .progress-fill { background-color: #ffeb3b; height: 100%; border-radius: 10px; transition: width 0.5s ease-in-out; }
    .big-percent { font-size: 3rem; font-weight: bold; color: #333; line-height: 1;}
    .meta-text { font-size: 0.85rem; color: #888; text-align: right; }
    .item-title { font-size: 1.1rem; font-weight: 600; color: #444; }
    .etapa-card { background-color: white; padding: 15px; border-radius: 10px; border: 1px solid #eee; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
</style>
""", unsafe_allow_html=True)

MESES_PT = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}

# --- Funções Visuais ---
def formatar_tempo(segundos):
    segundos = int(segundos)
    h, m = seconds_to_hm(segundos)
    return f"{h}h {m}m" if h > 0 else f"{m}m"

def seconds_to_hm(segundos):
    h = segundos // 3600
    m = (segundos % 3600) // 60
    return int(h), int(m)

def formatar_relogio(segundos):
    s = int(segundos)
    return f"{s//3600:02d}:{(s%3600)//60:02d}:{s%60:02d}"

def desenhar_calendario(ano, mes):
    cal = calendar.Calendar(firstweekday=6)
    mes_days = cal.monthdayscalendar(ano, mes)
    dias = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
    cols = st.columns(7)
    for i, d in enumerate(dias): cols[i].markdown(f"**{d}**", unsafe_allow_html=True)
    for semana in mes_days:
        cols = st.columns(7)
        for i, dia in enumerate(semana):
            with cols[i]:
                if dia != 0:
                    chave = f"{ano}-{mes:02d}-{dia:02d}"
                    val = st.session_state.historico_estudos.get(chave, [0, 0])
                    h_val, a_val = (val[0], val[1]) if isinstance(val, list) else (0,0)
                    if h_val > 0:
                        h, m = seconds_to_hm(h_val * 3600)
                        st.markdown(f"""<div style="background-color:#eafce0;border-radius:6px;padding:8px;height:90px;">
                            <div style="font-weight:bold;color:#666;">{dia}</div>
                            <div style="font-size:12px;">📖 {a_val}<br>⏱️ {h}h{m:02d}m</div></div>""", unsafe_allow_html=True)
                    else:
                        st.markdown(f"""<div style="background-color:#f9f9f9;border-radius:6px;padding:8px;height:90px;"><div style="color:#ccc;">{dia}</div></div>""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.title("StudyHub Pro")

# Mostra quem está logado
st.sidebar.caption(f"👤 Olá, **{st.session_state.usuario_atual}**")

# Botão de Sair (Logout)
if st.sidebar.button("🚪 Sair"):
    st.session_state.logado = False
    st.session_state.usuario_atual = ""
    st.rerun()

st.sidebar.divider()

menu = st.sidebar.radio("Menu", ["🏠 Home", "⏳ Pomodoro", "✅ Tarefas"])
st.sidebar.divider()
if st.sidebar.button("🗑️ Resetar Tudo"):
    if os.path.exists(ARQUIVO_DB): os.remove(ARQUIVO_DB)
    st.session_state.clear()
    st.rerun()

if st.session_state.sessao_estudo:
    status = "🟢 Estudando" if st.session_state.sessao_estudo['rodando'] else "🟡 Pausado"
    st.sidebar.info(f"{status}: {st.session_state.sessao_estudo['materia']}")
    if st.session_state.sessao_estudo['rodando']:
        idx = st.session_state.sessao_estudo.get('index_ciclo')
        if idx is not None and 0 <= idx < len(st.session_state.ciclo_estudos):
            delta = (datetime.now() - st.session_state.sessao_estudo['inicio']).total_seconds()
            st.session_state.ciclo_estudos[idx]['cumprido'] = (st.session_state.sessao_estudo['acumulado'] + delta) / 60

# --- Home ---
if menu == "🏠 Home":
    st.title("🎓 Dashboard")
    
    if 'ano_cal' not in st.session_state: st.session_state.ano_cal = datetime.now().year; st.session_state.mes_cal = datetime.now().month
    with st.expander("📅 Calendário", expanded=True):
        c_prev, c_mes, c_next = st.columns([1, 6, 1])
        if c_prev.button("⬅️"): st.session_state.mes_cal -= 1
        c_mes.markdown(f"<h4 style='text-align:center'>{MESES_PT.get(st.session_state.mes_cal, 'Mês')} {st.session_state.ano_cal}</h4>", unsafe_allow_html=True)
        if c_next.button("➡️"): st.session_state.mes_cal += 1
        desenhar_calendario(st.session_state.ano_cal, st.session_state.mes_cal)
    st.divider()

    lista_materias = list(st.session_state.materias.keys())
    
    if not lista_materias:
        st.info("👋 Cadastre sua primeira matéria abaixo para começar!")
        c1, c2, c3 = st.columns([3,3,2])
        nm = c1.text_input("Nome da Matéria", key="init_nome")
        nc = c2.text_input("Primeiro Conteúdo", key="init_cont")
        if c3.button("Salvar Inicial", key="init_btn", type="primary"):
            if nm and nc: st.session_state.materias[nm] = [nc]; salvar_dados(); st.rerun()
    else:
        st.subheader("🚀 Sessão Ativa")
        with st.container(border=True):
            if st.session_state.sessao_estudo is None:
                c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
                m_rap = c1.selectbox("Matéria", lista_materias, key="sessao_mat")
                c_rap = c2.selectbox("Conteúdo", st.session_state.materias.get(m_rap, ["Geral"]), key="sessao_cont")
                meta_rap = c3.number_input("Meta", 5, 120, 45, key="sessao_meta", label_visibility="collapsed")
                if c4.button("▶ Iniciar", key="sessao_btn", type="primary", use_container_width=True):
                    st.session_state.sessao_estudo = {
                        "materia": m_rap, "conteudo": c_rap, "meta": meta_rap, 
                        "inicio": datetime.now(), "acumulado": 0, "rodando": True, "index_ciclo": None
                    }
                    st.rerun()
                
                with st.expander("⚙️ Gerenciar Matérias"):
                    t1, t2, t3 = st.tabs(["Add", "Edit", "Del"])
                    with t1:
                        ca1, ca2, ca3 = st.columns([3,3,2])
                        nm = ca1.text_input("Nova Matéria", key="add_nm")
                        nt = ca2.text_input("Tópico", key="add_nt")
                        if ca3.button("Salvar", key="add_btn"):
                            if nm and nt: st.session_state.materias[nm] = [nt]; salvar_dados(); st.rerun()
                    with t3:
                        md = st.selectbox("Excluir", lista_materias, key="del_sel")
                        if st.button("Confirmar", key="del_btn"): del st.session_state.materias[md]; salvar_dados(); st.rerun()
            else:
                d = st.session_state.sessao_estudo
                total = d['acumulado'] + ((datetime.now()-d['inicio']).total_seconds() if d['rodando'] else 0)
                
                c_txt, c_time, c_act = st.columns([3, 4, 3])
                with c_txt:
                    st.markdown(f"### {d['materia']}")
                    st.progress(min(total / (d['meta']*60), 1.0))
                with c_time:
                    st.markdown(f"<h1 style='color:{'#48bb78' if d['rodando'] else '#ecc94b'};text-align:center;margin:0'>{formatar_relogio(total)}</h1>", unsafe_allow_html=True)
                with c_act:
                    st.write(""); kp, ks = st.columns(2)
                    if d['rodando']:
                        if kp.button("⏸ Pausar", use_container_width=True):
                            st.session_state.sessao_estudo['acumulado'] = total; st.session_state.sessao_estudo['rodando'] = False; st.rerun()
                    else:
                        if kp.button("▶ Retomar", use_container_width=True):
                            st.session_state.sessao_estudo['inicio'] = datetime.now(); st.session_state.sessao_estudo['rodando'] = True; st.rerun()
                    if ks.button("⏹ Finalizar", type="primary", use_container_width=True):
                        hj = datetime.now().strftime("%Y-%m-%d")
                        val = st.session_state.historico_estudos.get(hj, [0, 0])
                        h_val = val[0] if isinstance(val, list) else 0
                        a_val = val[1] if isinstance(val, list) else 0
                        
                        st.session_state.historico_estudos[hj] = [h_val + (total/3600), a_val + 1]
                        if d.get('index_ciclo') is not None:
                            st.session_state.ciclo_estudos[d['index_ciclo']]['cumprido'] = total / 60
                            st.session_state.ciclo_estudos[d['index_ciclo']]['status'] = 'done'
                        st.session_state.sessao_estudo = None; salvar_dados(); st.rerun()
                if d['rodando']: time.sleep(1); st.rerun()
        st.write("##")

        # Ciclo
        total_meta = sum([i['meta'] for i in st.session_state.ciclo_estudos])
        total_cump = sum([i.get('cumprido', 0) for i in st.session_state.ciclo_estudos])
        percent = (total_cump / total_meta * 100) if total_meta > 0 else 0
        
        cL, cR = st.columns([2, 1])
        with cL: st.subheader("🔁 Ciclo de Estudos")
        with cR:
             with st.popover("➕ Adicionar ao Ciclo"):
                m_c = st.selectbox("Matéria", lista_materias, key="ciclo_add_mat")
                meta_c = st.number_input("Meta (min)", 15, 120, 45, step=5, key="ciclo_add_meta")
                if st.button("Adicionar", key="ciclo_add_btn"):
                    st.session_state.ciclo_estudos.append({"materia": m_c, "meta": meta_c, "cumprido": 0, "status": "pending"})
                    salvar_dados(); st.rerun()

        if st.session_state.ciclo_estudos:
            st.markdown(f"""<div style="margin-bottom: 30px;"><div style="display:flex; justify-content:space-between;">
                <span class="big-percent">{percent:.1f}%</span><span class="meta-text">Meta Global: {formatar_tempo(total_meta*60)}</span></div>
                <div class="progress-bg"><div class="progress-fill" style="width: {min(percent, 100)}%; background-color: #ffeb3b;"></div></div></div>""", unsafe_allow_html=True)
            
            for i, item in enumerate(st.session_state.ciclo_estudos):
                p_item = (item.get('cumprido', 0) / item['meta'] * 100)
                cor = "#48bb78" if p_item >= 100 else "#4299e1" if item['status'] == 'active' else "#cbd5e0"
                c_card, c_btn = st.columns([5, 1])
                with c_card:
                    st.markdown(f"""<div class="etapa-card"><div style="display:flex; justify-content:space-between;"><span class="item-title">{item['materia']}</span>
                        <span class="meta-text">Meta: {item['meta']}m</span></div><div class="progress-bg" style="height:6px;"><div class="progress-fill" style="width:{min(p_item, 100)}%;background-color:{cor}"></div></div></div>""", unsafe_allow_html=True)
                with c_btn:
                    st.write(""); st.write("")
                    dis = True if (st.session_state.sessao_estudo or p_item >= 100) else False
                    if not dis and st.button("▶", key=f"play_ciclo_{i}"):
                        st.session_state.sessao_estudo = {
                            "materia": item['materia'], "meta": item['meta'], "inicio": datetime.now(), 
                            "acumulado": item.get('cumprido',0)*60, "rodando": True, "index_ciclo": i, "conteudo": "Ciclo"
                        }
                        item['status'] = 'active'; salvar_dados(); st.rerun()
            
            if st.button("🗑️ Limpar Ciclo"): st.session_state.ciclo_estudos = []; salvar_dados(); st.rerun()

elif menu == "⏳ Pomodoro": st.header("Pomodoro")
elif menu == "✅ Tarefas": st.header("Tarefas")
