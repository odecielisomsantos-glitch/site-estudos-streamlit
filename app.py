import streamlit as st
import time
import calendar
from datetime import datetime

# --- Configuração Inicial ---
st.set_page_config(page_title="StudyHub Pro", page_icon="🎓", layout="wide")

# --- CSS Personalizado ---
st.markdown("""
<style>
    .stSelectbox label { display: none; }
    div[data-testid="stExpander"] { border: none; box-shadow: none; }
    
    /* Card do Ciclo */
    .cycle-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 5px solid #cbd5e0;
    }
    .cycle-card.active { border-left-color: #4299e1; background-color: #ebf8ff; }
    .cycle-card.done { border-left-color: #48bb78; background-color: #f0fff4; opacity: 0.7; }
    
    /* Destaque para área de cadastro vazia */
    .empty-state {
        padding: 20px;
        background-color: #fff5f5;
        border: 1px dashed #fc8181;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- Inicialização de Estado (ZERADO) ---
if 'materias' not in st.session_state:
    # COMEÇA VAZIO! O usuário adiciona manualmente.
    st.session_state.materias = {} 

if 'ciclo_estudos' not in st.session_state:
    st.session_state.ciclo_estudos = []

if 'sessao_estudo' not in st.session_state:
    st.session_state.sessao_estudo = None 

if 'historico_estudos' not in st.session_state:
    # Histórico vazio ou com dados de exemplo (pode zerar se quiser: removemos os dados fictícios)
    st.session_state.historico_estudos = {} 

# --- Funções Auxiliares ---
def formatar_tempo(segundos):
    segundos = int(segundos)
    h = segundos // 3600
    m = (segundos % 3600) // 60
    s = segundos % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def desenhar_calendario(ano, mes):
    cal = calendar.Calendar(firstweekday=6)
    mes_days = cal.monthdayscalendar(ano, mes)
    dias_semana = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
    
    cols = st.columns(7)
    for i, d in enumerate(dias_semana): cols[i].markdown(f"**{d}**", unsafe_allow_html=True)
    
    for semana in mes_days:
        cols = st.columns(7)
        for i, dia in enumerate(semana):
            with cols[i]:
                if dia != 0:
                    chave = f"{ano}-{mes:02d}-{dia:02d}"
                    horas, ativ = st.session_state.historico_estudos.get(chave, (0, 0))
                    if horas > 0:
                        h, m = int(horas), int((horas % 1) * 60)
                        st.markdown(f"""<div style="background-color:#eafce0;border-radius:6px;padding:8px;height:90px;">
                            <div style="font-weight:bold;color:#666;">{dia}</div>
                            <div style="font-size:12px;">📖 {ativ}<br>⏱️ {h}h{m:02d}m</div></div>""", unsafe_allow_html=True)
                    else:
                        st.markdown(f"""<div style="background-color:#f9f9f9;border-radius:6px;padding:8px;height:90px;">
                            <div style="color:#ccc;">{dia}</div></div>""", unsafe_allow_html=True)

# --- Barra Lateral ---
st.sidebar.title("StudyHub v5")
menu = st.sidebar.radio("Menu", ["🏠 Home", "⏳ Pomodoro", "✅ Tarefas"])

if st.session_state.sessao_estudo:
    status = "🟢 Estudando" if st.session_state.sessao_estudo['rodando'] else "🟡 Pausado"
    st.sidebar.info(f"{status}: {st.session_state.sessao_estudo['materia']}")

# --- Conteúdo Principal ---
if menu == "🏠 Home":
    st.title("🎓 Dashboard")
    
    # Calendário
    if 'ano_cal' not in st.session_state:
        st.session_state.ano_cal = datetime.now().year
        st.session_state.mes_cal = datetime.now().month

    with st.expander("📅 Ver Calendário", expanded=False):
        c_prev, c_mes, c_next = st.columns([1, 6, 1])
        if c_prev.button("⬅️"): st.session_state.mes_cal -= 1
        c_mes.markdown(f"<h4 style='text-align:center'>{calendar.month_name[st.session_state.mes_cal]}</h4>", unsafe_allow_html=True)
        if c_next.button("➡️"): st.session_state.mes_cal += 1
        desenhar_calendario(st.session_state.ano_cal, st.session_state.mes_cal)
    
    st.divider()

    # ==========================================
    # 0. VERIFICAÇÃO: LISTA DE MATÉRIAS VAZIA?
    # ==========================================
    lista_materias = list(st.session_state.materias.keys())
    
    if not lista_materias:
        st.markdown("""
        <div class="empty-state">
            <h3>👋 Olá! Vamos começar?</h3>
            <p>Você ainda não tem matérias cadastradas. Adicione a primeira abaixo para liberar o cronômetro.</p>
        </div>
        """, unsafe_allow_html=True)
        
        c_new_mat, c_new_cont, c_new_btn = st.columns([3, 3, 2])
        new_mat_input = c_new_mat.text_input("Nome da Matéria (ex: Matemática)", key="init_mat")
        new_cont_input = c_new_cont.text_input("Primeiro Conteúdo (ex: Álgebra)", key="init_cont")
        
        if c_new_btn.button("💾 Salvar Primeira Matéria", type="primary"):
            if new_mat_input and new_cont_input:
                st.session_state.materias[new_mat_input] = [new_cont_input]
                st.success("Matéria cadastrada! O painel será liberado.")
                time.sleep(1)
                st.rerun()
            else:
                st.warning("Preencha os dois campos.")
                
    else:
        # ==========================================
        # 1. ÁREA DE ESTUDO ATIVO (PLAYER)
        # ==========================================
        st.subheader("🚀 Sessão Ativa")
        
        with st.container(border=True):
            if st.session_state.sessao_estudo is None:
                # Seletor de Início Rápido
                c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
                
                with c1:
                    st.caption("Matéria")
                    mat_rapida = st.selectbox("Selecione", lista_materias, key="sel_mat_rapida")
                
                with c2:
                    st.caption("Conteúdo")
                    # Pega conteudos da materia selecionada
                    lista_conteudos = st.session_state.materias.get(mat_rapida, ["Geral"])
                    cont_rapida = st.selectbox("Selecione", lista_conteudos, key="sel_cont_rapida")

                with c3:
                    st.caption("Meta (min)")
                    meta_rapida = st.number_input("Meta", min_value=5, value=45, step=5, label_visibility="collapsed")
                
                with c4:
                    st.caption("Ação")
                    if st.button("▶ Iniciar", type="primary", use_container_width=True):
                        st.session_state.sessao_estudo = {
                            "materia": mat_rapida, "conteudo": cont_rapida, "meta": meta_rapida, 
                            "inicio": datetime.now(), "acumulado": 0, "rodando": True, "index_ciclo": None
                        }
                        st.rerun()
                
                # Botãozinho discreto para adicionar mais matérias aqui também
                with st.expander("➕ Cadastrar nova matéria ou conteúdo"):
                    cm1, cm2, cm3 = st.columns([3, 3, 2])
                    n_mat = cm1.text_input("Nova Matéria")
                    n_top = cm2.text_input("Tópico/Conteúdo")
                    if cm3.button("Salvar Novo"):
                        if n_mat and n_top:
                            if n_mat in st.session_state.materias:
                                st.session_state.materias[n_mat].append(n_top)
                            else:
                                st.session_state.materias[n_mat] = [n_top]
                            st.success("Salvo!")
                            time.sleep(0.5)
                            st.rerun()

            else:
                # --- MODO CRONÔMETRO RODANDO ---
                dados = st.session_state.sessao_estudo
                if dados['rodando']:
                    tempo_decorrido = (datetime.now() - dados['inicio']).total_seconds()
                    total_segundos = dados['acumulado'] + tempo_decorrido
                else:
                    total_segundos = dados['acumulado']
                
                meta_segundos = dados['meta'] * 60
                progresso = min(total_segundos / meta_segundos, 1.0)
                
                col_txt, col_timer, col_btns = st.columns([3, 4, 3])
                with col_txt:
                    st.markdown(f"### 📖 {dados['materia']}")
                    st.caption(f"Conteúdo: {dados.get('conteudo', 'Geral')} | Meta: {dados['meta']} min")
                    st.progress(progresso)
                with col_timer:
                    cor = "#48bb78" if dados['rodando'] else "#ecc94b"
                    st.markdown(f"<h1 style='color:{cor};text-align:center;font-size:3rem;margin:0'>{formatar_tempo(total_segundos)}</h1>", unsafe_allow_html=True)
                with col_btns:
                    st.write("")
                    c_play, c_stop = st.columns(2)
                    if dados['rodando']:
                        if c_play.button("⏸ Pausar", use_container_width=True):
                            st.session_state.sessao_estudo['acumulado'] = total_segundos
                            st.session_state.sessao_estudo['rodando'] = False
                            st.rerun()
                    else:
                        if c_play.button("▶ Retomar", use_container_width=True):
                            st.session_state.sessao_estudo['inicio'] = datetime.now()
                            st.session_state.sessao_estudo['rodando'] = True
                            st.rerun()
                    if c_stop.button("⏹ Finalizar", type="primary", use_container_width=True):
                        hoje_str = datetime.now().strftime("%Y-%m-%d")
                        h_atual, ativ_atual = st.session_state.historico_estudos.get(hoje_str, (0, 0))
                        st.session_state.historico_estudos[hoje_str] = (h_atual + (total_segundos/3600), ativ_atual + 1)
                        if dados.get('index_ciclo') is not None:
                            st.session_state.ciclo_estudos[dados['index_ciclo']]['status'] = 'done'
                        st.session_state.sessao_estudo = None
                        st.balloons()
                        st.rerun()
                if dados['rodando']: time.sleep(1); st.rerun()

        st.write("##")

        # ==========================================
        # 2. ÁREA DO CICLO DE ESTUDOS (PLAYLIST)
        # ==========================================
        st.subheader("🔁 Meu Ciclo de Estudos")
        
        # Formulário para Adicionar ao Ciclo
        with st.container():
            c_add_mat, c_add_meta, c_add_btn = st.columns([4, 2, 2])
            
            # Dropdown só aparece se tiver matérias (já verificado pelo if/else principal)
            nova_materia_ciclo = c_add_mat.selectbox("Matéria", lista_materias, key="ciclo_sel")
            nova_meta_ciclo = c_add_meta.number_input("Meta (min)", min_value=15, value=45, step=5, key="ciclo_meta")
            
            if c_add_btn.button("➕ Adicionar à Fila", use_container_width=True):
                st.session_state.ciclo_estudos.append({
                    "materia": nova_materia_ciclo,
                    "meta": nova_meta_ciclo,
                    "status": "pending"
                })
                st.rerun()

        st.write("---")

        if not st.session_state.ciclo_estudos:
            st.caption("Sua fila está vazia. Adicione matérias acima.")
        else:
            for i, item in enumerate(st.session_state.ciclo_estudos):
                if item['status'] == 'done':
                    css = "done"; icon = "✅"; label = "Concluído"; dis = True
                elif item['status'] == 'active':
                    css = "active"; icon = "🔵"; label = "Em Andamento"; dis = True
                else:
                    css = ""; icon = "⚪"; label = "▶ Iniciar"; dis = False
                    if st.session_state.sessao_estudo is not None: dis = True # Bloqueia se já tem um rodando
                
                st.markdown(f"""
                <div class="cycle-card {css}">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div><strong style="font-size:1.1rem;">{icon} {item['materia']}</strong>
                        <div style="color:#666;">Meta: {item['meta']} min</div></div>
                    </div>
                </div>""", unsafe_allow_html=True)
                
                c_void, c_act = st.columns([5, 1])
                if not dis and c_act.button(label, key=f"btn_ciclo_{i}"):
                    st.session_state.sessao_estudo = {
                        "materia": item['materia'], "meta": item['meta'],
                        "inicio": datetime.now(), "acumulado": 0, "rodando": True, "index_ciclo": i
                    }
                    item['status'] = 'active'
                    st.rerun()
            
            if st.button("🗑️ Limpar Ciclo"):
                st.session_state.ciclo_estudos = []
                st.rerun()

elif menu == "⏳ Pomodoro":
    st.header("Pomodoro (Em breve)")
elif menu == "✅ Tarefas":
    st.header("Tarefas (Em breve)")
