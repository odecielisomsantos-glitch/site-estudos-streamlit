import streamlit as st
import time
import calendar
import json
import os
import random
from datetime import datetime, timedelta

# --- Configuração Inicial ---
st.set_page_config(page_title="StudyHub Pro", page_icon="🎓", layout="wide")

# ==========================================
# 🔐 SISTEMA DE LOGIN & DADOS
# ==========================================

CREDENCIAIS = {
    "Odecielisom": "Fernanda",
    "Fernanda": "Odecielisom"
}

if 'logado' not in st.session_state: st.session_state.logado = False
if 'usuario_atual' not in st.session_state: st.session_state.usuario_atual = ""

def get_arquivo_db():
    if st.session_state.usuario_atual:
        return f"dados_{st.session_state.usuario_atual}.json"
    return "dados_temp.json"

def carregar_dados_usuario():
    arquivo = get_arquivo_db()
    st.session_state.materias = {}
    st.session_state.historico_estudos = {} 
    st.session_state.ciclo_estudos = []
    st.session_state.flashcards = []
    st.session_state.revisoes = []
    st.session_state.xp = 0
    st.session_state.nivel = 1

    if os.path.exists(arquivo):
        try:
            with open(arquivo, "r", encoding="utf-8") as f:
                dados = json.load(f)
                st.session_state.materias = dados.get("materias", {})
                st.session_state.historico_estudos = dados.get("historico", {})
                st.session_state.ciclo_estudos = dados.get("ciclo", [])
                st.session_state.flashcards = dados.get("flashcards", [])
                st.session_state.revisoes = dados.get("revisoes", [])
                st.session_state.xp = dados.get("xp", 0)
                st.session_state.nivel = dados.get("nivel", 1)
        except: pass

def salvar_dados():
    if not st.session_state.logado: return
    arquivo = get_arquivo_db()
    if 'flashcards' not in st.session_state: st.session_state.flashcards = []
    if 'revisoes' not in st.session_state: st.session_state.revisoes = []
    dados = {
        "materias": st.session_state.materias,
        "historico": st.session_state.historico_estudos,
        "ciclo": st.session_state.ciclo_estudos,
        "flashcards": st.session_state.flashcards,
        "revisoes": st.session_state.revisoes,
        "xp": st.session_state.xp,
        "nivel": st.session_state.nivel
    }
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

def verificar_login():
    user = st.session_state.input_usuario
    pwd = st.session_state.input_senha
    if user in CREDENCIAIS and CREDENCIAIS[user] == pwd:
        st.session_state.logado = True
        st.session_state.usuario_atual = user
        carregar_dados_usuario()
    else:
        st.error("Dados incorretos")

def fazer_logout():
    st.session_state.logado = False
    st.session_state.usuario_atual = ""
    st.rerun()

# --- TELA DE LOGIN ---
if not st.session_state.logado:
    st.markdown("""<style>.login-box {max-width: 400px; margin: 100px auto; text-align: center;}</style>""", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<h1 style='text-align: center;'>🔐 StudyHub</h1>", unsafe_allow_html=True)
        st.text_input("Usuário", key="input_usuario")
        st.text_input("Senha", type="password", key="input_senha")
        st.button("Entrar", on_click=verificar_login, type="primary", use_container_width=True)
    st.stop()

# ==========================================
# 🚀 APP PRINCIPAL
# ==========================================
if 'sessao_estudo' not in st.session_state: st.session_state.sessao_estudo = None 
if 'revisoes' not in st.session_state: st.session_state.revisoes = []

# --- CSS AVANÇADO (CALENDÁRIO ESTILO PLANNER) ---
st.markdown("""
<style>
    .stSelectbox label { display: none; }
    div[data-testid="stExpander"] { border: 1px solid #e2e8f0; border-radius: 8px; }
    
    /* 1. ESTILO GERAL DOS BOTÕES DO CALENDÁRIO */
    div[data-testid="stColumn"] > div > div > button {
        height: 110px; /* Altura fixa para ficar quadrado/retangular */
        width: 100%;
        border-radius: 0px; /* Bordas retas para parecer grade */
        border: 1px solid #e0e0e0;
        display: flex;
        flex-direction: column;
        align-items: flex-start !important; /* Alinha texto no topo esquerda */
        justify-content: flex-start !important;
        padding: 8px !important;
        font-size: 0.9rem;
        transition: all 0.2s;
    }

    /* 2. DIAS VAZIOS (Botão Secondary) */
    div[data-testid="stColumn"] > div > div > button[kind="secondary"] {
        background-color: #ffffff;
        color: #555;
    }
    div[data-testid="stColumn"] > div > div > button[kind="secondary"]:hover {
        background-color: #f7fafc;
        border-color: #cbd5e0;
    }

    /* 3. DIAS COM ESTUDO (Botão Primary - FORÇANDO VERDE) */
    div[data-testid="stColumn"] > div > div > button[kind="primary"] {
        background-color: #e6fffa !important; /* Verde claro fundo */
        border: 1px solid #b2f5ea !important;
        color: #234e52 !important; /* Verde escuro texto */
    }
    div[data-testid="stColumn"] > div > div > button[kind="primary"]:hover {
        background-color: #b2f5ea !important;
        transform: scale(1.02);
        z-index: 2;
    }
    div[data-testid="stColumn"] > div > div > button[kind="primary"] p {
        font-size: 0.8rem;
        line-height: 1.4;
    }

    /* --- DARK MODE ADJUSTMENTS --- */
    @media (prefers-color-scheme: dark) {
        /* Vazio Dark */
        div[data-testid="stColumn"] > div > div > button[kind="secondary"] {
            background-color: #1e1e1e;
            border-color: #333;
            color: #aaa;
        }
        /* Ativo Dark (Verde Musgo) */
        div[data-testid="stColumn"] > div > div > button[kind="primary"] {
            background-color: #064e3b !important;
            border-color: #059669 !important;
            color: #ecfdf5 !important;
        }
        .rpg-card { background: linear-gradient(135deg, #262730 0%, #1f1f1f 100%); color: #fafafa; border: 1px solid #444; }
        .mission-card { background-color: #262730; color: #fafafa; border-left: 5px solid #818cf8; }
        .etapa-card { background-color: #262730; color: #fafafa; border: 1px solid #444; }
    }

    /* Outros Estilos (RPG, Cards) */
    .rpg-card { background: linear-gradient(135deg, #ffffff 0%, #f3f4f6 100%); color: #1f2937; border: 1px solid #e5e7eb; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); padding: 40px; text-align: center; min-height: 300px; display: flex; flex-direction: column; justify-content: center; align-items: center; }
    .mission-card { background-color: white; color: #333; border-left: 5px solid #6366f1; padding: 15px; margin-bottom: 10px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); display: flex; justify-content: space-between; align-items: center; }
    .etapa-card { background-color: white; color: #333; padding: 15px; border-radius: 10px; border: 1px solid #eee; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
    .big-percent { font-size: 3rem; font-weight: bold; line-height: 1;}
    .progress-bg { background-color: #ddd; border-radius: 10px; height: 10px; width: 100%; margin: 5px 0; }
    .progress-fill { background-color: #ffeb3b; height: 100%; border-radius: 10px; transition: width 0.5s ease-in-out; }
</style>
""", unsafe_allow_html=True)

MESES_PT = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}

# --- Funções Visuais ---
def formatar_tempo(segundos):
    h, m = int(segundos // 3600), int((segundos % 3600) // 60)
    return f"{h}h {m}m" if h > 0 else f"{m}m"

def formatar_relogio(segundos):
    s = int(segundos)
    return f"{s//3600:02d}:{(s%3600)//60:02d}:{s%60:02d}"

# --- Pop-up do Calendário ---
@st.dialog("📅 Detalhes do Dia")
def mostrar_detalhes_dia(data_str, dia_num, mes_nome):
    val = st.session_state.historico_estudos.get(data_str, [0, 0, []])
    h_val = val[0]
    lista_detalhes = val[2] if len(val) > 2 else []
    
    st.markdown(f"### {dia_num} de {mes_nome}")
    
    if h_val == 0:
        st.info("Dia livre (sem registros).")
    else:
        h, m = int(h_val), int((h_val % 1) * 60)
        c1, c2 = st.columns(2)
        c1.metric("Tempo Total", f"{h}h {m}m")
        c2.metric("Sessões", val[1])
        
        st.divider()
        st.subheader("Histórico:")
        if lista_detalhes:
            for item in lista_detalhes:
                st.success(f"📚 {item}")
        else:
            st.caption("Sem detalhes salvos.")

def desenhar_calendario_interativo(ano, mes):
    cal = calendar.Calendar(firstweekday=6)
    mes_days = cal.monthdayscalendar(ano, mes)
    dias = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
    
    # Cabeçalho dos dias
    cols = st.columns(7)
    for i, d in enumerate(dias): 
        cols[i].markdown(f"<div style='text-align:center; font-weight:bold; color:#888; font-size:0.8rem; margin-bottom:5px'>{d}</div>", unsafe_allow_html=True)
    
    # Grade
    for semana in mes_days:
        cols = st.columns(7)
        for i, dia in enumerate(semana):
            if dia != 0:
                chave = f"{ano}-{mes:02d}-{dia:02d}"
                val = st.session_state.historico_estudos.get(chave, [0, 0])
                h_val = val[0]
                qtd_sess = val[1]
                
                # Configuração do Botão
                # Se tem estudo (>0), usamos type="primary" (que nosso CSS pinta de verde)
                # Se não, type="secondary" (branco/cinza)
                tipo_btn = "primary" if h_val > 0 else "secondary"
                
                # Texto do Botão
                if h_val > 0:
                    h, m = int(h_val), int((h_val % 1) * 60)
                    # \n\n força quebra de linha para empurrar infos para baixo
                    label = f"{dia}\n\n📖 {qtd_sess} Ativ.\n⏱️ {h}h{m:02d}m"
                else:
                    label = f"{dia}"
                
                if cols[i].button(label, key=f"cal_{chave}", type=tipo_btn, use_container_width=True):
                    mostrar_detalhes_dia(chave, dia, MESES_PT[mes])
            else:
                cols[i].write("") # Espaço vazio para dias de outros meses

# --- Sidebar ---
st.sidebar.title("StudyHub Pro")
st.sidebar.caption(f"👤 **{st.session_state.usuario_atual}**")

# TIMER NA SIDEBAR (Abaixo do Perfil)
if st.session_state.sessao_estudo and st.session_state.sessao_estudo['rodando']:
    delta = (datetime.now() - st.session_state.sessao_estudo['inicio']).total_seconds()
    total = st.session_state.sessao_estudo['acumulado'] + delta
    
    st.sidebar.markdown(f"""
    <div style="background-color:#1c4532; color:#4ade80; padding:15px; border-radius:10px; border:1px solid #22c55e; text-align:center; margin-bottom:20px;">
        <div style="font-size:0.8rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:5px;">Estudando</div>
        <div style="font-weight:bold; font-size:1.1rem; color:white; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{st.session_state.sessao_estudo['materia']}</div>
        <div style="font-size:1.8rem; font-weight:bold; margin-top:5px; font-family:monospace;">{formatar_relogio(total)}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Update Background
    idx = st.session_state.sessao_estudo.get('index_ciclo')
    if idx is not None and 0 <= idx < len(st.session_state.ciclo_estudos):
        st.session_state.ciclo_estudos[idx]['cumprido'] = total / 60
else:
    st.sidebar.info("💤 Nenhuma sessão ativa")

if st.sidebar.button("🚪 Sair"): fazer_logout()
st.sidebar.divider()

menu = st.sidebar.radio("Navegação", ["🏠 Home", "🔄 Revisões Táticas", "⚖️ Lei Seca", "🧠 Flashcards RPG", "📊 Acompanhamento"])
st.sidebar.divider()

with st.sidebar.expander("⚙️ Configurações"):
    st.warning("Zona de Perigo")
    if st.button("🗑️ Resetar Meus Dados", type="primary"):
        arquivo = get_arquivo_db()
        if os.path.exists(arquivo): os.remove(arquivo)
        st.session_state.clear()
        st.rerun()

# ==========================================
# 🏠 HOME
# ==========================================
if menu == "🏠 Home":
    st.title(f"Painel de {st.session_state.usuario_atual}")
    
    if 'ano_cal' not in st.session_state: st.session_state.ano_cal = datetime.now().year; st.session_state.mes_cal = datetime.now().month
    
    # Calendário mais limpo (sem a borda padrão do expander se possível, mas mantendo a função)
    with st.expander("📅 Calendário de Estudos", expanded=True):
        c_prev, c_mes, c_next = st.columns([1, 6, 1])
        if c_prev.button("⬅️"): st.session_state.mes_cal -= 1
        c_mes.markdown(f"<h3 style='text-align:center; margin:0'>{MESES_PT.get(st.session_state.mes_cal, 'Mês')} {st.session_state.ano_cal}</h3>", unsafe_allow_html=True)
        if c_next.button("➡️"): st.session_state.mes_cal += 1
        st.write("") # Espaçamento
        desenhar_calendario_interativo(st.session_state.ano_cal, st.session_state.mes_cal)
    
    st.divider()

    lista_materias = list(st.session_state.materias.keys())
    if not lista_materias:
        st.warning("Cadastre suas matérias abaixo para liberar o sistema.")
        c1, c2 = st.columns(2)
        nm = c1.text_input("Matéria")
        nc = c2.text_input("Conteúdo")
        if st.button("Salvar Inicial", type="primary"):
             if nm and nc: st.session_state.materias[nm] = [nc]; salvar_dados(); st.rerun()
    else:
        st.subheader("🚀 Sessão Ativa")
        with st.container(border=True):
            if st.session_state.sessao_estudo is None:
                c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
                m = c1.selectbox("Matéria", lista_materias, key="s_m")
                c = c2.selectbox("Conteúdo", st.session_state.materias.get(m, ["Geral"]), key="s_c")
                mt = c3.number_input("Meta", 5, 120, 45, key="s_mt", label_visibility="collapsed")
                if c4.button("▶ Iniciar", type="primary", use_container_width=True):
                    st.session_state.sessao_estudo = {"materia": m, "conteudo": c, "meta": mt, "inicio": datetime.now(), "acumulado": 0, "rodando": True, "index_ciclo": None}
                    st.rerun()
                
                with st.expander("⚙️ Gerenciar Matérias"):
                    t1, t3 = st.tabs(["➕ Adicionar", "🗑️ Excluir"])
                    with t1:
                        cx1, cx2, cx3 = st.columns([3,3,2])
                        n_m = cx1.text_input("Matéria", key="n_m")
                        n_t = cx2.text_input("Tópico", key="n_t")
                        if cx3.button("Salvar", key="b_sv"):
                            if n_m and n_t: st.session_state.materias[n_m] = [n_t]; salvar_dados(); st.rerun()
                    with t3:
                        md = st.selectbox("Excluir", lista_materias, key="d_sl")
                        if st.button("Confirmar", key="b_dl"): del st.session_state.materias[md]; salvar_dados(); st.rerun()
            else:
                d = st.session_state.sessao_estudo
                total = d['acumulado'] + ((datetime.now()-d['inicio']).total_seconds() if d['rodando'] else 0)
                c1, c2, c3 = st.columns([3, 4, 3])
                c1.markdown(f"### {d['materia']}"); c1.progress(min(total / (d['meta']*60), 1.0))
                c2.markdown(f"<h1 style='color:{'#48bb78' if d['rodando'] else '#ecc94b'};text-align:center;margin:0'>{formatar_relogio(total)}</h1>", unsafe_allow_html=True)
                c3.write(""); k1, k2 = c3.columns(2)
                if d['rodando']:
                    if k1.button("⏸", use_container_width=True): d['acumulado'] = total; d['rodando'] = False; st.rerun()
                else:
                    if k1.button("▶", use_container_width=True): d['inicio'] = datetime.now(); d['rodando'] = True; st.rerun()
                
                if k2.button("⏹", type="primary", use_container_width=True):
                    hj = datetime.now().strftime("%Y-%m-%d")
                    val = st.session_state.historico_estudos.get(hj, [0, 0, []])
                    if len(val) < 3: val.append([])
                    
                    novo_tempo = val[0] + (total/3600)
                    nova_qtd = val[1] + 1
                    detalhes = val[2]
                    detalhes.append(f"{d['materia']} ({d.get('conteudo', 'Geral')}) - {formatar_tempo(total)}")
                    
                    st.session_state.historico_estudos[hj] = [novo_tempo, nova_qtd, detalhes]
                    
                    if d.get('index_ciclo') is not None:
                        st.session_state.ciclo_estudos[d['index_ciclo']]['cumprido'] = total / 60
                        st.session_state.ciclo_estudos[d['index_ciclo']]['status'] = 'done'
                    
                    # Agendamento Revisão
                    data_rev1 = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
                    data_rev7 = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                    st.session_state.revisoes.append({"materia": d['materia'], "conteudo": d.get('conteudo', 'Geral'), "data": data_rev1, "tipo": "24h", "status": "pendente"})
                    st.session_state.revisoes.append({"materia": d['materia'], "conteudo": d.get('conteudo', 'Geral'), "data": data_rev7, "tipo": "7 Dias", "status": "pendente"})
                    
                    st.session_state.sessao_estudo = None; salvar_dados(); st.rerun()
                
                if d['rodando']: time.sleep(1); st.rerun()

        st.write("##")
        t_meta = sum([i['meta'] for i in st.session_state.ciclo_estudos])
        t_cump = sum([i.get('cumprido', 0) for i in st.session_state.ciclo_estudos])
        perc = (t_cump / t_meta * 100) if t_meta > 0 else 0
        
        cL, cR = st.columns([2, 1])
        cL.subheader("🔁 Ciclo de Estudos")
        with cR.popover("➕ Adicionar ao Ciclo"):
            mc = st.selectbox("Matéria", lista_materias, key="c_m")
            mtc = st.number_input("Meta (min)", 15, 120, 45, step=5, key="c_mt")
            if st.button("Adicionar", key="c_add"):
                st.session_state.ciclo_estudos.append({"materia": mc, "meta": mtc, "cumprido": 0, "status": "pending"})
                salvar_dados(); st.rerun()
        
        if st.session_state.ciclo_estudos:
            st.markdown(f"""<div style="margin-bottom:20px;"><div style="display:flex;justify-content:space-between;"><span class="big-percent">{perc:.1f}%</span><span>Meta: {formatar_tempo(t_meta*60)}</span></div><div class="progress-bg"><div class="progress-fill" style="width:{min(perc,100)}%"></div></div></div>""", unsafe_allow_html=True)
            for i, item in enumerate(st.session_state.ciclo_estudos):
                pi = (item.get('cumprido', 0) / item['meta'] * 100)
                cor = "#48bb78" if pi >= 100 else "#4299e1" if item['status'] == 'active' else "#cbd5e0"
                cc, cb = st.columns([5, 1])
                cc.markdown(f"""<div class="etapa-card"><div style="display:flex;justify-content:space-between;"><b>{item['materia']}</b><span>{item['meta']}m</span></div><div class="progress-bg" style="height:6px"><div class="progress-fill" style="width:{min(pi,100)}%;background:{cor}"></div></div></div>""", unsafe_allow_html=True)
                if not st.session_state.sessao_estudo and pi < 100 and cb.button("▶", key=f"pc_{i}"):
                    st.session_state.sessao_estudo = {"materia": item['materia'], "meta": item['meta'], "inicio": datetime.now(), "acumulado": item.get('cumprido',0)*60, "rodando": True, "index_ciclo": i, "conteudo": "Ciclo"}
                    item['status'] = 'active'; salvar_dados(); st.rerun()
            if st.button("Limpar Ciclo"): st.session_state.ciclo_estudos = []; salvar_dados(); st.rerun()

# ==========================================
# 🔄 REVISÕES
# ==========================================
elif menu == "🔄 Revisões Táticas":
    st.title("🔄 Centro de Comando")
    xp = st.session_state.get('xp', 0)
    st.caption(f"XP Acumulado: {xp}")
    
    tab_pend, tab_hist = st.tabs(["🔥 Pendentes", "✅ Histórico"])
    
    with tab_pend:
        hoje_str = datetime.now().strftime("%Y-%m-%d")
        revisoes_pendentes = [r for r in st.session_state.revisoes if r['data'] <= hoje_str and r['status'] == 'pendente']
        if not revisoes_pendentes:
            st.success("Tudo em dia! Nenhuma revisão para hoje.")
        else:
            st.subheader("Radar de Pendências")
            contagem = {}
            for r in revisoes_pendentes: m = r['materia']; contagem[m] = contagem.get(m, 0) + 1
            html_pills = ""
            for mat, qtd in contagem.items(): html_pills += f"<span class='threat-pill'>{mat}: {qtd}</span>"
            st.markdown(f"<div>{html_pills}</div>", unsafe_allow_html=True)
            st.write("---")
            for i, rev in enumerate(revisoes_pendentes):
                idx_orig = st.session_state.revisoes.index(rev)
                col_info, col_btn = st.columns([5, 1])
                with col_info:
                    st.markdown(f"""<div class="mission-card"><div><strong style="font-size:1.1rem">{rev['materia']}</strong> <span style="opacity:0.8">({rev['conteudo']})</span></div><div style="background:#e0e7ff; color:#4338ca; padding:2px 8px; border-radius:4px; font-size:0.8rem">{rev['tipo']}</div></div>""", unsafe_allow_html=True)
                with col_btn:
                    st.write("")
                    if st.button("✅ Feito", key=f"rev_ok_{i}"):
                        st.session_state.revisoes[idx_orig]['status'] = 'concluido'; st.session_state.xp += 50; st.toast("Revisão Concluída! +50 XP", icon="🎖️"); salvar_dados(); st.rerun()

    with tab_hist:
        concluidas = [r for r in st.session_state.revisoes if r['status'] == 'concluido']
        if not concluidas: st.info("Nenhuma revisão concluída.")
        else:
            for rev in reversed(concluidas): st.markdown(f"✅ **{rev['materia']}** - {rev['conteudo']} ({rev['tipo']})")

# ==========================================
# ⚖️ LEI SECA
# ==========================================
elif menu == "⚖️ Lei Seca":
    st.title("⚖️ Lei Seca")
    st.markdown("Cronômetro dedicado.")
    with st.container(border=True):
        if st.session_state.sessao_estudo is None:
            c1, c2 = st.columns([3, 1])
            lei = c1.text_input("Lei/Código", placeholder="Ex: CF/88")
            meta = c2.number_input("Meta", 15, 120, 30)
            if st.button("📖 Ler", type="primary", use_container_width=True):
                if lei:
                    st.session_state.sessao_estudo = {"materia": "Lei Seca", "conteudo": lei, "meta": meta, "inicio": datetime.now(), "acumulado": 0, "rodando": True, "index_ciclo": None}
                    st.rerun()
                else: st.warning("Digite o nome.")
        else:
            st.info("Sessão ativa na Home.")
            if st.button("Ir para Home"): st.rerun()

# ==========================================
# 🧠 FLASHCARDS
# ==========================================
elif menu == "🧠 Flashcards RPG":
    xp = st.session_state.get('xp', 0)
    nivel = st.session_state.get('nivel', 1)
    xp_prox = nivel * 100
    prog = (xp / xp_prox) * 100
    c_lvl, c_bar = st.columns([1, 4])
    c_lvl.markdown(f"<h2 style='margin:0'>🛡️ Lvl {nivel}</h2>", unsafe_allow_html=True)
    c_bar.markdown(f"""<div style="margin-top:10px;"><span style="font-weight:bold; color:#666">{xp} / {xp_prox} XP</span><div class="xp-bar-bg"><div class="xp-bar-fill" style="width:{min(prog, 100)}%"></div></div></div>""", unsafe_allow_html=True)
    st.divider()
    tab_arena, tab_forja, tab_lib = st.tabs(["⚔️ Arena", "⚒️ Forja", "📜 Biblioteca"])
    
    with tab_forja:
        c1, c2 = st.columns(2)
        m_flash = c1.selectbox("Matéria", list(st.session_state.materias.keys()) if st.session_state.materias else ["Geral"])
        perg = st.text_area("Pergunta")
        resp = st.text_area("Resposta")
        if st.button("⚒️ Forjar"):
            if perg and resp:
                novo_card = {"id": str(datetime.now().timestamp()), "materia": m_flash, "pergunta": perg, "resposta": resp, "proxima_revisao": datetime.now().strftime("%Y-%m-%d"), "intervalo": 1}
                st.session_state.flashcards.append(novo_card); salvar_dados(); st.success("Criado!")

    with tab_arena:
        hoje_str = datetime.now().strftime("%Y-%m-%d")
        cards_para_hoje = [c for c in st.session_state.flashcards if c.get('proxima_revisao', '2000-01-01') <= hoje_str]
        if not cards_para_hoje: st.markdown("""<div style="text-align:center; padding: 40px;"><h1>🎉 Vitória!</h1><p>Nenhum inimigo à vista.</p></div>""", unsafe_allow_html=True)
        else:
            st.markdown("### 📡 Radar")
            contagem = {}
            for c in cards_para_hoje: m = c.get('materia', 'Geral'); contagem[m] = contagem.get(m, 0) + 1
            html_pills = ""
            for mat, qtd in contagem.items(): html_pills += f"<span class='threat-pill'>{mat}: {qtd}</span>"
            st.markdown(f"<div>{html_pills}</div>", unsafe_allow_html=True); st.write("") 
            
            if 'card_batalha' not in st.session_state: st.session_state.card_batalha = random.choice(cards_para_hoje); st.session_state.card_revelado = False
            card = st.session_state.card_batalha
            st.markdown(f"""<div class="rpg-card-container"><div class="rpg-card"><span class="card-category">{card.get('materia', 'Geral')}</span><div class="card-text">{card['pergunta']}</div></div></div>""", unsafe_allow_html=True); st.write("##")
            if not st.session_state.card_revelado:
                if st.button("🛡️ Revelar", use_container_width=True): st.session_state.card_revelado = True; st.rerun()
            else:
                st.info(f"**R:** {card['resposta']}")
                c1, c2, c3 = st.columns(3)
                if c1.button("🔴 Errei"): card['proxima_revisao'] = datetime.now().strftime("%Y-%m-%d"); card['intervalo'] = 1; st.session_state.xp += 10; del st.session_state.card_batalha; salvar_dados(); st.rerun()
                if c2.button("🟡 Bom"): interv = int(card.get('intervalo', 1) * 1.5) + 1; card['proxima_revisao'] = (datetime.now() + timedelta(days=interv)).strftime("%Y-%m-%d"); card['intervalo'] = interv; st.session_state.xp += 20; del st.session_state.card_batalha; salvar_dados(); st.rerun()
                if c3.button("🟢 Fácil"): interv = int(card.get('intervalo', 1) * 2.5) + 2; card['proxima_revisao'] = (datetime.now() + timedelta(days=interv)).strftime("%Y-%m-%d"); card['intervalo'] = interv; st.session_state.xp += 30; del st.session_state.card_batalha; salvar_dados(); st.rerun()
                if st.session_state.xp >= st.session_state.nivel * 100: st.session_state.nivel += 1; st.session_state.xp = 0; st.toast("LEVEL UP!", icon="🔥")

    with tab_lib:
        st.write(f"Total: {len(st.session_state.flashcards)}")
        for i, c in enumerate(st.session_state.flashcards):
            with st.expander(f"{c.get('materia')} - {c['pergunta'][:30]}..."):
                st.write(f"R: {c['resposta']}"); st.caption(f"Rev: {c.get('proxima_revisao')}")
                if st.button("🗑️", key=f"d_{i}"): st.session_state.flashcards.pop(i); salvar_dados(); st.rerun()

# ==========================================
# 📊 ACOMPANHAMENTO
# ==========================================
elif menu == "📊 Acompanhamento":
    st.title("📊 Estatísticas")
    total_horas = 0
    total_dias = len(st.session_state.historico_estudos)
    for data, valores in st.session_state.historico_estudos.items(): total_horas += valores[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("Total", f"{int(total_horas)}h {int((total_horas%1)*60)}m")
    c2.metric("Dias", f"{total_dias}")
    media = total_horas / total_dias if total_dias > 0 else 0
    c3.metric("Média", f"{int(media)}h {int((media%1)*60)}m")
