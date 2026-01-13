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
    # Gamificação
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
                st.session_state.xp = dados.get("xp", 0)
                st.session_state.nivel = dados.get("nivel", 1)
        except: pass

def salvar_dados():
    if not st.session_state.logado: return
    arquivo = get_arquivo_db()
    dados = {
        "materias": st.session_state.materias,
        "historico": st.session_state.historico_estudos,
        "ciclo": st.session_state.ciclo_estudos,
        "flashcards": st.session_state.flashcards,
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
if 'flashcards' not in st.session_state: st.session_state.flashcards = []

# --- CSS REVOLUCIONÁRIO ---
st.markdown("""
<style>
    .stSelectbox label { display: none; }
    div[data-testid="stExpander"] { border: 1px solid #e2e8f0; border-radius: 8px; }
    
    /* Design do Flashcard RPG */
    .rpg-card-container {
        perspective: 1000px;
        margin-top: 20px;
    }
    .rpg-card {
        background: linear-gradient(135deg, #ffffff 0%, #f3f4f6 100%);
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        padding: 40px;
        text-align: center;
        min-height: 300px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        border: 1px solid #e5e7eb;
        transition: transform 0.3s;
    }
    .rpg-card:hover { transform: translateY(-5px); }
    .card-category {
        background-color: #e0f2fe; color: #0369a1; 
        padding: 5px 15px; border-radius: 20px; 
        font-size: 0.8rem; font-weight: bold; margin-bottom: 20px;
        text-transform: uppercase; letter-spacing: 1px;
    }
    .card-text { font-size: 1.6rem; font-weight: 600; color: #1f2937; line-height: 1.4; }
    
    /* Gamification Header */
    .xp-bar-bg { background: #e5e7eb; height: 10px; border-radius: 5px; width: 100%; margin-top: 5px; }
    .xp-bar-fill { background: linear-gradient(90deg, #8b5cf6, #ec4899); height: 100%; border-radius: 5px; }
    
    /* Botões de Decisão */
    .btn-hard { border: 2px solid #ef4444; color: #ef4444; background: white; padding: 10px; border-radius: 10px; text-align: center; cursor: pointer; font-weight: bold;}
    .btn-hard:hover { background: #ef4444; color: white; }
    
    .btn-good { border: 2px solid #f59e0b; color: #f59e0b; background: white; padding: 10px; border-radius: 10px; text-align: center; cursor: pointer; font-weight: bold;}
    .btn-good:hover { background: #f59e0b; color: white; }
    
    .btn-easy { border: 2px solid #10b981; color: #10b981; background: white; padding: 10px; border-radius: 10px; text-align: center; cursor: pointer; font-weight: bold;}
    .btn-easy:hover { background: #10b981; color: white; }

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
                        h, m = int(h_val), int((h_val % 1) * 60)
                        st.markdown(f"""<div style="background-color:#eafce0;border-radius:6px;padding:8px;height:90px;">
                            <div style="font-weight:bold;color:#666;">{dia}</div>
                            <div style="font-size:12px;">📖 {a_val}<br>⏱️ {h}h{m:02d}m</div></div>""", unsafe_allow_html=True)
                    else:
                         st.markdown(f"""<div style="background-color:#f9f9f9;border-radius:6px;padding:8px;height:90px;"><div style="color:#ccc;">{dia}</div></div>""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.title("StudyHub Pro")
st.sidebar.caption(f"👤 **{st.session_state.usuario_atual}**")
if st.sidebar.button("🚪 Sair"): fazer_logout()
st.sidebar.divider()
menu = st.sidebar.radio("Navegação", ["🏠 Home", "⚖️ Lei Seca", "🧠 Flashcards RPG", "📊 Acompanhamento"])
st.sidebar.divider()
if st.sidebar.button("🗑️ Resetar Meus Dados"):
    arquivo = get_arquivo_db()
    if os.path.exists(arquivo): os.remove(arquivo)
    st.session_state.clear()
    st.rerun()

# Atualização do Ciclo
if st.session_state.sessao_estudo and st.session_state.sessao_estudo['rodando']:
    st.sidebar.info(f"🟢 {st.session_state.sessao_estudo['materia']}")
    idx = st.session_state.sessao_estudo.get('index_ciclo')
    if idx is not None and 0 <= idx < len(st.session_state.ciclo_estudos):
        delta = (datetime.now() - st.session_state.sessao_estudo['inicio']).total_seconds()
        st.session_state.ciclo_estudos[idx]['cumprido'] = (st.session_state.sessao_estudo['acumulado'] + delta) / 60

# ==========================================
# 🏠 HOME
# ==========================================
if menu == "🏠 Home":
    st.title(f"Painel de {st.session_state.usuario_atual}")
    
    # --- CALENDÁRIO ---
    if 'ano_cal' not in st.session_state: st.session_state.ano_cal = datetime.now().year; st.session_state.mes_cal = datetime.now().month
    with st.expander("📅 Calendário de Estudos", expanded=True):
        c_prev, c_mes, c_next = st.columns([1, 6, 1])
        if c_prev.button("⬅️"): st.session_state.mes_cal -= 1
        c_mes.markdown(f"<h4 style='text-align:center'>{MESES_PT.get(st.session_state.mes_cal, 'Mês')} {st.session_state.ano_cal}</h4>", unsafe_allow_html=True)
        if c_next.button("➡️"): st.session_state.mes_cal += 1
        desenhar_calendario(st.session_state.ano_cal, st.session_state.mes_cal)
    
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
        # PLAYER
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
                    val = st.session_state.historico_estudos.get(hj, [0, 0])
                    st.session_state.historico_estudos[hj] = [val[0] + (total/3600), val[1] + 1]
                    if d.get('index_ciclo') is not None:
                        st.session_state.ciclo_estudos[d['index_ciclo']]['cumprido'] = total / 60
                        st.session_state.ciclo_estudos[d['index_ciclo']]['status'] = 'done'
                    st.session_state.sessao_estudo = None; salvar_dados(); st.rerun()
                if d['rodando']: time.sleep(1); st.rerun()

        # CICLO
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
# ⚖️ LEI SECA
# ==========================================
elif menu == "⚖️ Lei Seca":
    st.title("⚖️ Lei Seca")
    st.markdown("Cronômetro dedicado para legislação.")
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
# 🧠 FLASHCARDS RPG (REVOLUCIONÁRIO)
# ==========================================
elif menu == "🧠 Flashcards RPG":
    
    # 1. CABEÇALHO GAMIFICADO
    xp = st.session_state.get('xp', 0)
    nivel = st.session_state.get('nivel', 1)
    xp_prox = nivel * 100
    progresso_xp = (xp / xp_prox) * 100
    
    c_lvl, c_bar = st.columns([1, 4])
    c_lvl.markdown(f"<h2 style='margin:0'>🛡️ Lvl {nivel}</h2>", unsafe_allow_html=True)
    c_bar.markdown(f"""
    <div style="margin-top:10px;">
        <span style="font-weight:bold; color:#666">{xp} / {xp_prox} XP</span>
        <div class="xp-bar-bg"><div class="xp-bar-fill" style="width:{min(progresso_xp, 100)}%"></div></div>
    </div>""", unsafe_allow_html=True)
    
    st.divider()

    # 2. ABAS (ARENA vs FORJA)
    tab_arena, tab_forja, tab_lib = st.tabs(["⚔️ A Arena (Estudar)", "⚒️ A Forja (Criar)", "📜 Biblioteca"])
    
    # --- A FORJA (CRIAR) ---
    with tab_forja:
        c1, c2 = st.columns(2)
        m_flash = c1.selectbox("Matéria", list(st.session_state.materias.keys()) if st.session_state.materias else ["Geral"])
        perg = st.text_area("Pergunta / Desafio")
        resp = st.text_area("Resposta / Solução")
        if st.button("⚒️ Forjar Carta"):
            if perg and resp:
                novo_card = {
                    "id": str(datetime.now().timestamp()),
                    "materia": m_flash,
                    "pergunta": perg,
                    "resposta": resp,
                    "proxima_revisao": datetime.now().strftime("%Y-%m-%d"), # Disponível hoje
                    "intervalo": 1
                }
                st.session_state.flashcards.append(novo_card)
                salvar_dados()
                st.success("Carta adicionada ao seu deck!")

    # --- A ARENA (ESTUDAR SRS) ---
    with tab_arena:
        # Filtra cartas disponíveis para hoje
        hoje_str = datetime.now().strftime("%Y-%m-%d")
        cards_para_hoje = [c for c in st.session_state.flashcards if c.get('proxima_revisao', '2000-01-01') <= hoje_str]
        
        if not cards_para_hoje:
            st.markdown("""
            <div style="text-align:center; padding: 40px;">
                <h1>🎉 Vitória!</h1>
                <p>Você zerou todos os inimigos (cards) por hoje!</p>
                <p>Descanse, guerreiro, ou crie mais cartas na Forja.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Seleciona um card aleatório dos pendentes
            if 'card_batalha' not in st.session_state:
                st.session_state.card_batalha = random.choice(cards_para_hoje)
                st.session_state.card_revelado = False
            
            card = st.session_state.card_batalha
            total_pendente = len(cards_para_hoje)
            
            st.caption(f"🔥 Inimigos restantes hoje: {total_pendente}")
            
            # MOSTRA A CARTA (FRONT)
            st.markdown(f"""
            <div class="rpg-card-container">
                <div class="rpg-card">
                    <span class="card-category">{card.get('materia', 'Geral')}</span>
                    <div class="card-text">{card['pergunta']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("##") # Espaço
            
            if not st.session_state.card_revelado:
                if st.button("🛡️ Revelar Resposta", use_container_width=True):
                    st.session_state.card_revelado = True
                    st.rerun()
            else:
                # MOSTRA A RESPOSTA (BACK) E BOTÕES DE DECISÃO
                st.info(f"**Resposta:** {card['resposta']}")
                
                st.write("### Como foi a batalha?")
                col_h, col_m, col_e = st.columns(3)
                
                # LÓGICA DO SRS (SIMPLIFICADA)
                # Hard: Repete amanhã (XP +10)
                # Good: Intervalo * 1.5 (XP +20)
                # Easy: Intervalo * 2.5 (XP +30)
                
                if col_h.button("🔴 Errei / Difícil (+10 XP)"):
                    card['proxima_revisao'] = datetime.now().strftime("%Y-%m-%d") # Mantém hoje/amanhã
                    card['intervalo'] = 1
                    st.session_state.xp += 10
                    # Checa Level Up
                    if st.session_state.xp >= st.session_state.nivel * 100:
                        st.session_state.nivel += 1
                        st.session_state.xp = 0
                        st.toast("LEVEL UP! 🆙", icon="🔥")
                    
                    del st.session_state.card_batalha
                    salvar_dados()
                    st.rerun()

                if col_m.button("🟡 Bom (+20 XP)"):
                    interv = int(card.get('intervalo', 1) * 1.5) + 1
                    prox = datetime.now() + timedelta(days=interv)
                    card['proxima_revisao'] = prox.strftime("%Y-%m-%d")
                    card['intervalo'] = interv
                    st.session_state.xp += 20
                    
                    if st.session_state.xp >= st.session_state.nivel * 100:
                        st.session_state.nivel += 1; st.session_state.xp = 0; st.toast("LEVEL UP! 🆙", icon="🔥")
                        
                    del st.session_state.card_batalha
                    salvar_dados()
                    st.rerun()

                if col_e.button("🟢 Fácil (+30 XP)"):
                    interv = int(card.get('intervalo', 1) * 2.5) + 2
                    prox = datetime.now() + timedelta(days=interv)
                    card['proxima_revisao'] = prox.strftime("%Y-%m-%d")
                    card['intervalo'] = interv
                    st.session_state.xp += 30
                    
                    if st.session_state.xp >= st.session_state.nivel * 100:
                        st.session_state.nivel += 1; st.session_state.xp = 0; st.toast("LEVEL UP! 🆙", icon="🔥")
                        
                    del st.session_state.card_batalha
                    salvar_dados()
                    st.rerun()

    # --- BIBLIOTECA (GERENCIAR) ---
    with tab_lib:
        st.write(f"Total de cartas no deck: {len(st.session_state.flashcards)}")
        for i, c in enumerate(st.session_state.flashcards):
            with st.expander(f"{c.get('materia')} - {c['pergunta'][:30]}..."):
                st.write(f"**P:** {c['pergunta']}")
                st.write(f"**R:** {c['resposta']}")
                st.caption(f"Próxima revisão: {c.get('proxima_revisao')}")
                if st.button("🗑️ Excluir Card", key=f"del_card_{i}"):
                    st.session_state.flashcards.pop(i)
                    salvar_dados()
                    st.rerun()

# ==========================================
# 📊 ACOMPANHAMENTO
# ==========================================
elif menu == "📊 Acompanhamento":
    st.title("📊 Estatísticas")
    total_horas = 0
    total_dias = len(st.session_state.historico_estudos)
    for data, valores in st.session_state.historico_estudos.items(): total_horas += valores[0]
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Estudado", f"{int(total_horas)}h {int((total_horas%1)*60)}m")
    c2.metric("Dias Ativos", f"{total_dias} dias")
    if total_dias > 0:
        media = total_horas / total_dias
        c3.metric("Média Diária", f"{int(media)}h {int((media%1)*60)}m")
    else: c3.metric("Média Diária", "0h")
