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
    div[data-testid="stExpander"] { border: 1px solid #e2e8f0; border-radius: 8px; }
    
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
    
    /* Estado Vazio */
    .empty-state {
        padding: 20px;
        background-color: #fff5f5;
        border: 1px dashed #fc8181;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- Inicialização de Estado ---
if 'materias' not in st.session_state:
    st.session_state.materias = {} 

if 'ciclo_estudos' not in st.session_state:
    st.session_state.ciclo_estudos = []

if 'sessao_estudo' not in st.session_state:
    st.session_state.sessao_estudo = None 

if 'historico_estudos' not in st.session_state:
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
st.sidebar.title("StudyHub v6")
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
    # 0. VERIFICAÇÃO INICIAL
    # ==========================================
    lista_materias = list(st.session_state.materias.keys())
    
    if not lista_materias:
        st.markdown("""
        <div class="empty-state">
            <h3>👋 Olá! Vamos começar?</h3>
            <p>Cadastre sua primeira matéria para liberar o painel.</p>
        </div>""", unsafe_allow_html=True)
        
        c_new_mat, c_new_cont, c_new_btn = st.columns([3, 3, 2])
        new_mat = c_new_mat.text_input("Matéria (ex: Matemática)")
        new_cont = c_new_cont.text_input("Conteúdo (ex: Álgebra)")
        
        if c_new_btn.button("💾 Salvar Inicial", type="primary"):
            if new_mat and new_cont:
                st.session_state.materias[new_mat] = [new_cont]
                st.rerun()
                
    else:
        # ==========================================
        # 1. ÁREA DE ESTUDO ATIVO
        # ==========================================
        st.subheader("🚀 Sessão Ativa")
        
        with st.container(border=True):
            # --- MODO DE SELEÇÃO ---
            if st.session_state.sessao_estudo is None:
                c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
                with c1: 
                    st.caption("Matéria")
                    mat_rapida = st.selectbox("Sel.", lista_materias, key="m_r")
                with c2:
                    st.caption("Conteúdo")
                    conts = st.session_state.materias.get(mat_rapida, ["Geral"])
                    cont_rapida = st.selectbox("Sel.", conts, key="c_r")
                with c3:
                    st.caption("Meta")
                    meta_rapida = st.number_input("Min", 5, 120, 45, label_visibility="collapsed")
                with c4:
                    st.caption("Ação")
                    if st.button("▶ Iniciar", type="primary", use_container_width=True):
                        st.session_state.sessao_estudo = {
                            "materia": mat_rapida, "conteudo": cont_rapida, "meta": meta_rapida, 
                            "inicio": datetime.now(), "acumulado": 0, "rodando": True, "index_ciclo": None
                        }
                        st.rerun()

                # --- NOVO: GERENCIADOR DE MATÉRIAS ---
                with st.expander("⚙️ Gerenciar Matérias (Adicionar / Editar / Excluir)"):
                    tab_add, tab_edit, tab_topics, tab_del = st.tabs(["➕ Adicionar", "✏️ Renomear", "📚 Tópicos", "🗑️ Excluir"])
                    
                    # 1. ADICIONAR
                    with tab_add:
                        c_a1, c_a2, c_a3 = st.columns([3, 3, 2])
                        n_m = c_a1.text_input("Nova Matéria", key="add_nm")
                        n_c = c_a2.text_input("Primeiro Tópico", key="add_nc")
                        if c_a3.button("Salvar Nova"):
                            if n_m and n_c:
                                st.session_state.materias[n_m] = [n_c]
                                st.success("Adicionado!")
                                time.sleep(0.5)
                                st.rerun()
                    
                    # 2. RENOMEAR MATÉRIA
                    with tab_edit:
                        c_e1, c_e2, c_e3 = st.columns([3, 3, 2])
                        m_old = c_e1.selectbox("Escolha para renomear", lista_materias, key="ren_old")
                        m_new = c_e2.text_input("Novo nome", key="ren_new")
                        if c_e3.button("Renomear"):
                            if m_new and m_old in st.session_state.materias:
                                st.session_state.materias[m_new] = st.session_state.materias.pop(m_old)
                                st.success("Renomeado!")
                                time.sleep(0.5)
                                st.rerun()
                    
                    # 3. GERENCIAR TÓPICOS
                    with tab_topics:
                        m_top = st.selectbox("Selecione a matéria:", lista_materias, key="topic_mat")
                        if m_top:
                            atuais = st.session_state.materias[m_top]
                            st.write(f"Tópicos atuais: {', '.join(atuais)}")
                            
                            c_t1, c_t2 = st.columns(2)
                            novo_top = c_t1.text_input("Adicionar novo tópico:", key="new_topic_input")
                            if c_t1.button("Adicionar Tópico"):
                                if novo_top:
                                    st.session_state.materias[m_top].append(novo_top)
                                    st.rerun()
                                    
                            del_top = c_t2.multiselect("Remover tópicos:", atuais, key="del_topic_input")
                            if c_t2.button("Remover Selecionados"):
                                for d in del_top:
                                    if d in st.session_state.materias[m_top]:
                                        st.session_state.materias[m_top].remove(d)
                                st.rerun()

                    # 4. EXCLUIR MATÉRIA
                    with tab_del:
                        st.warning("Cuidado: Isso apagará a matéria e seus tópicos!")
                        c_d1, c_d2 = st.columns([4, 2])
                        del_target = c_d1.selectbox("Selecione para excluir definitivamente", lista_materias, key="del_target")
                        if c_d2.button("🗑️ Confirmar Exclusão", type="primary"):
                            if del_target in st.session_state.materias:
                                del st.session_state.materias[del_target]
                                st.success("Excluído!")
                                time.sleep(0.5)
                                st.rerun()

            # --- MODO CRONÔMETRO ---
            else:
                dados = st.session_state.sessao_estudo
                if dados['rodando']:
                    total = dados['acumulado'] + (datetime.now() - dados['inicio']).total_seconds()
                else:
                    total = dados['acumulado']
                
                col_txt, col_timer, col_btns = st.columns([3, 4, 3])
                with col_txt:
                    st.markdown(f"### 📖 {dados['materia']}")
                    st.caption(f"Conteúdo: {dados.get('conteudo', 'Geral')}")
                    st.progress(min(total / (dados['meta']*60), 1.0))
                with col_timer:
                    cor = "#48bb78" if dados['rodando'] else "#ecc94b"
                    st.markdown(f"<h1 style='color:{cor};text-align:center;font-size:3rem;margin:0'>{formatar_tempo(total)}</h1>", unsafe_allow_html=True)
                with col_btns:
                    st.write("")
                    c_p, c_s = st.columns(2)
                    if dados['rodando']:
                        if c_p.button("⏸ Pausar", use_container_width=True):
                            st.session_state.sessao_estudo['acumulado'] = total
                            st.session_state.sessao_estudo['rodando'] = False
                            st.rerun()
                    else:
                        if c_p.button("▶ Retomar", use_container_width=True):
                            st.session_state.sessao_estudo['inicio'] = datetime.now()
                            st.session_state.sessao_estudo['rodando'] = True
                            st.rerun()
                    if c_s.button("⏹ Finalizar", type="primary", use_container_width=True):
                        hj = datetime.now().strftime("%Y-%m-%d")
                        h, a = st.session_state.historico_estudos.get(hj, (0, 0))
                        st.session_state.historico_estudos[hj] = (h + (total/3600), a + 1)
                        if dados.get('index_ciclo') is not None:
                            st.session_state.ciclo_estudos[dados['index_ciclo']]['status'] = 'done'
                        st.session_state.sessao_estudo = None
                        st.rerun()
                
                if dados['rodando']: time.sleep(1); st.rerun()

        st.write("##")

        # ==========================================
        # 2. CICLO DE ESTUDOS
        # ==========================================
        st.subheader("🔁 Ciclo de Estudos")
        with st.container():
            c1, c2, c3 = st.columns([4, 2, 2])
            n_m = c1.selectbox("Matéria", lista_materias, key="ciclo_m")
            n_meta = c2.number_input("Meta", 15, 120, 45, step=5, label_visibility="collapsed")
            if c3.button("➕ Fila", use_container_width=True):
                st.session_state.ciclo_estudos.append({"materia": n_m, "meta": n_meta, "status": "pending"})
                st.rerun()

        st.write("---")
        if not st.session_state.ciclo_estudos:
            st.caption("Fila vazia.")
        else:
            for i, item in enumerate(st.session_state.ciclo_estudos):
                css = "done" if item['status'] == 'done' else "active" if item['status'] == 'active' else ""
                icon = "✅" if item['status'] == 'done' else "🔵" if item['status'] == 'active' else "⚪"
                
                st.markdown(f"""
                <div class="cycle-card {css}">
                    <strong>{icon} {item['materia']}</strong> <span style="color:#666">({item['meta']} min)</span>
                </div>""", unsafe_allow_html=True)
                
                if item['status'] == 'pending':
                    if st.button("▶ Iniciar", key=f"btn_{i}"):
                        st.session_state.sessao_estudo = {
                            "materia": item['materia'], "meta": item['meta'],
                            "inicio": datetime.now(), "acumulado": 0, "rodando": True, "index_ciclo": i
                        }
                        item['status'] = 'active'
                        st.rerun()
            
            if st.button("Limpar Ciclo"):
                st.session_state.ciclo_estudos = []
                st.rerun()

elif menu == "⏳ Pomodoro":
    st.header("Pomodoro (Em breve)")
elif menu == "✅ Tarefas":
    st.header("Tarefas (Em breve)")
