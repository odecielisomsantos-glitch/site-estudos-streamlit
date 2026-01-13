import streamlit as st
import time, calendar, json, os, random, pytz
from datetime import datetime, timedelta

st.set_page_config(page_title="StudyHub Pro", page_icon="🎓", layout="wide")

def agora_br():
    return datetime.now(pytz.timezone('America/Sao_Paulo'))

CREDENCIAIS = {"Odecielisom": "Fernanda", "Fernanda": "Odecielisom"}
if 'logado' not in st.session_state: st.session_state.logado = False
if 'usuario_atual' not in st.session_state: st.session_state.usuario_atual = ""

def carregar_dados_usuario():
    arq = f"dados_{st.session_state.usuario_atual}.json"
    st.session_state.materias, st.session_state.historico_estudos = {}, {}
    st.session_state.ciclo_estudos, st.session_state.flashcards = [], []
    st.session_state.revisoes, st.session_state.xp, st.session_state.nivel = [], 0, 1
    if os.path.exists(arq):
        try:
            with open(arq, "r", encoding="utf-8") as f:
                d = json.load(f)
                st.session_state.update(d)
        except: pass

def salvar_dados():
    if not st.session_state.logado: return
    arq = f"dados_{st.session_state.usuario_atual}.json"
    d = {k: st.session_state[k] for k in ["materias", "historico", "ciclo_estudos", "flashcards", "revisoes", "xp", "nivel"] if k in st.session_state}
    with open(arq, "w", encoding="utf-8") as f: json.dump(d, f, ensure_ascii=False, indent=4)

if not st.session_state.logado:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.title("🔐 StudyHub")
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.button("Entrar", use_container_width=True):
            if u in CREDENCIAIS and CREDENCIAIS[u] == p:
                st.session_state.logado, st.session_state.usuario_atual = True, u
                carregar_dados_usuario(); st.rerun()
            else: st.error("Dados incorretos")
    st.stop()

st.markdown("""<style>
    div[data-testid="stExpander"] { border: 1px solid #e2e8f0; border-radius: 8px; }
    div[data-testid="stColumn"] > div > div > button { height: 110px; width: 100%; border-radius: 0px; border: 1px solid #e0e0e0; display: flex; flex-direction: column; align-items: flex-start !important; justify-content: flex-start !important; padding: 8px !important; font-size: 0.9rem; }
    div[data-testid="stColumn"] > div > div > button[kind="primary"] { background-color: #e6fffa !important; border: 1px solid #b2f5ea !important; color: #234e52 !important; }
    .mission-gallery-card { background-color: #fff; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid #e5e7eb; margin-bottom: 10px; text-align: center; }
    .mission-card-header { background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%); padding: 20px; font-size: 2rem; color: white; border-radius: 12px 12px 0 0; }
    .mission-card-body { padding: 10px; font-weight: bold; color: #1f2937; }
    @media (prefers-color-scheme: dark) {
        div[data-testid="stColumn"] > div > div > button[kind="primary"] { background-color: #064e3b !important; color: #ecfdf5 !important; }
        .mission-gallery-card { background-color: #262730; } .mission-card-body { color: #eee; }
    }
    .rpg-card { background: linear-gradient(135deg, #ffffff 0%, #f3f4f6 100%); padding: 40px; border-radius: 20px; text-align: center; min-height: 250px; display: flex; flex-direction: column; justify-content: center; border: 1px solid #e5e7eb; color: #1f2937; }
</style>""", unsafe_allow_html=True)

@st.dialog("📅 Detalhes")
def show_dia(dt, d, m):
    v = st.session_state.historico_estudos.get(dt, [0, 0, []])
    st.write(f"### {d} de {m}"); st.metric("Tempo", f"{int(v[0])}h {int((v[0]%1)*60)}m")
    for i in (v[2] if len(v)>2 else []): st.success(i)

st.sidebar.title("StudyHub Pro")
st.sidebar.caption(f"👤 {st.session_state.usuario_atual}")
if st.session_state.get('sessao_estudo') and st.session_state.sessao_estudo['rodando']:
    sec = (agora_br() - st.session_state.sessao_estudo['inicio']).total_seconds() + st.session_state.sessao_estudo['acumulado']
    st.sidebar.success(f"⏱️ {st.session_state.sessao_estudo['materia']}\n\n{int(sec//3600):02d}:{int((sec%3600)//60):02d}:{int(sec%60):02d}")
menu = st.sidebar.radio("Menu", ["🏠 Home", "🔄 Revisões", "⚖️ Lei Seca", "🧠 Flashcards", "📊 Dados"])
if st.sidebar.button("Sair"): 
    st.session_state.logado = False; st.rerun()

if menu == "🏠 Home":
    hj = agora_br()
    if 'ano_cal' not in st.session_state: st.session_state.ano_cal, st.session_state.mes_cal = hj.year, hj.month
    with st.expander("📅 Calendário", expanded=True):
        c_p, c_m, c_n = st.columns([1, 6, 1])
        if c_p.button("⬅️"): st.session_state.mes_cal -= 1
        c_m.markdown(f"<h3 style='text-align:center'>{MESES_PT[st.session_state.mes_cal]} {st.session_state.ano_cal}</h3>", unsafe_allow_html=True)
        if c_n.button("➡️"): st.session_state.mes_cal += 1
        cal_obj = calendar.Calendar(firstweekday=6)
        for sem in cal_obj.monthdayscalendar(st.session_state.ano_cal, st.session_state.mes_cal):
            cols = st.columns(7)
            for i, d in enumerate(sem):
                if d:
                    key = f"{st.session_state.ano_cal}-{st.session_state.mes_cal:02d}-{d:02d}"
                    v = st.session_state.historico_estudos.get(key, [0])
                    if cols[i].button(f"{d}" + (f"\n\n⏱️{int(v[0])}h" if v[0]>0 else ""), key=f"c_{key}", type="primary" if v[0]>0 else "secondary"):
                        show_dia(key, d, MESES_PT[st.session_state.mes_cal])
    st.divider()
    mats = list(st.session_state.materias.keys())
    if not mats:
        nm = st.text_input("Nova Matéria"); nc = st.text_input("Tópico")
        if st.button("Salvar"): st.session_state.materias[nm] = [nc]; salvar_dados(); st.rerun()
    else:
        if not st.session_state.get('sessao_estudo'):
            c1, c2, c3 = st.columns([3, 2, 1])
            m = c1.selectbox("Matéria", mats); mt = c2.number_input("Meta (min)", 5, 120, 45)
            if c3.button("▶ Iniciar", use_container_width=True):
                st.session_state.sessao_estudo = {"materia": m, "inicio": agora_br(), "acumulado": 0, "rodando": True, "meta": mt}
                st.rerun()
        else:
            s = st.session_state.sessao_estudo
            total = s['acumulado'] + (agora_br() - s['inicio']).total_seconds()
            st.subheader(f"Estudando: {s['materia']}")
            st.title(f"{int(total//3600):02d}:{int((total%3600)//60):02d}:{int(total%60):02d}")
            if st.button("⏹ Finalizar"):
                data_hj = agora_br().strftime("%Y-%m-%d")
                v = st.session_state.historico_estudos.get(data_hj, [0, 0, []])
                v[0] += total/3600; v[1] += 1; v[2].append(f"{s['materia']} - {int(total//60)}m")
                st.session_state.historico_estudos[data_hj] = v
                st.session_state.sessao_estudo = None; salvar_dados(); st.rerun()
            time.sleep(1); st.rerun()

elif menu == "🧠 Flashcards":
    tab1, tab2 = st.tabs(["⚔️ Arena", "⚒️ Forja"])
    with tab2:
        p = st.text_input("Pasta/Concurso")
        m = st.selectbox("Matéria", list(st.session_state.materias.keys()) if st.session_state.materias else ["Geral"])
        perg = st.text_area("Pergunta")
        resp = st.text_area("Resposta")
        if st.button("Forjar"):
            st.session_state.flashcards.append({"concurso": p or "Geral", "materia": m, "pergunta": perg, "resposta": resp, "proxima": agora_br().strftime("%Y-%m-%d"), "int": 1})
            salvar_dados(); st.success("Salvo!")
    with tab1:
        if not st.session_state.get('p_sel'):
            pastas = list(set(c.get('concurso', 'Geral') for c in st.session_state.flashcards))
            cols = st.columns(4)
            for i, pst in enumerate(pastas):
                with cols[i%4]:
                    st.markdown(f'<div class="mission-gallery-card"><div class="mission-card-header">🛡️</div><div class="mission-card-body">{pst}</div></div>', unsafe_allow_html=True)
                    if st.button("Iniciar", key=f"p_{pst}", use_container_width=True): st.session_state.p_sel = pst; st.rerun()
        else:
            if st.button("⬅️ Voltar"): st.session_state.p_sel = None; st.rerun()
            hoje = agora_br().strftime("%Y-%m-%d")
            pend = [c for c in st.session_state.flashcards if c.get('concurso') == st.session_state.p_sel and c.get('proxima', '2000-01-01') <= hoje]
            if not pend: st.success("Missão cumprida!")
            else:
                card = pend[0]
                st.markdown(f'<div class="rpg-card">{card["pergunta"]}</div>', unsafe_allow_html=True)
                if st.button("Revelar Resposta"): st.info(card["resposta"])
                c1, c2, c3 = st.columns(3)
                if c1.button("🔴 Errei"):
                    card['proxima'] = (agora_br() + timedelta(days=1)).strftime("%Y-%m-%d")
                    salvar_dados(); st.rerun()
                if c2.button("🟡 Bom"):
                    card['int'] = int(card.get('int', 1)*2); card['proxima'] = (agora_br() + timedelta(days=card['int'])).strftime("%Y-%m-%d")
                    salvar_dados(); st.rerun()
                if c3.button("🟢 Fácil"):
                    card['int'] = int(card.get('int', 1)*4); card['proxima'] = (agora_br() + timedelta(days=card['int'])).strftime("%Y-%m-%d")
                    salvar_dados(); st.rerun()

elif menu == "📊 Dados":
    st.title("Estatísticas")
    total = sum(v[0] for v in st.session_state.historico_estudos.values())
    st.metric("Total de Horas", f"{int(total)}h")
    if st.button("Resetar Tudo"): st.session_state.clear(); st.rerun()
