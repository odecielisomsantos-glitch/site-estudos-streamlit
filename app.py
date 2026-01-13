import streamlit as st
import time
import calendar
from datetime import datetime

# --- Configuração Inicial ---
st.set_page_config(page_title="StudyHub Pro", page_icon="🎓", layout="wide")

# --- CSS Personalizado (Estilo da Imagem) ---
st.markdown("""
<style>
    .stSelectbox label { display: none; }
    div[data-testid="stExpander"] { border: 1px solid #e2e8f0; border-radius: 8px; }
    
    /* Barra de Progresso Customizada */
    .progress-bg {
        background-color: #f1f3f5;
        border-radius: 10px;
        height: 10px;
        width: 100%;
        margin-top: 5px;
        margin-bottom: 5px;
    }
    .progress-fill {
        background-color: #ffeb3b; /* Amarelo da imagem (ou verde #48bb78) */
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s ease-in-out;
    }
    
    /* Textos */
    .big-percent { font-size: 3rem; font-weight: bold; color: #333; line-height: 1;}
    .meta-text { font-size: 0.85rem; color: #888; text-align: right; }
    .item-title { font-size: 1.1rem; font-weight: 600; color: #444; }
    
    /* Container do Item */
    .etapa-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #eee;
        margin-bottom: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
</style>
""", unsafe_allow_html=True)

# --- Inicialização de Estado ---
if 'materias' not in st.session_state: st.session_state.materias = {} 
if 'sessao_estudo' not in st.session_state: st.session_state.sessao_estudo = None 
if 'historico_estudos' not in st.session_state: st.session_state.historico_estudos = {} 

# Estrutura do Ciclo: [{'materia': 'X', 'meta': 60, 'cumprido': 0, 'status': 'pending'}]
if 'ciclo_estudos' not in st.session_state: st.session_state.ciclo_estudos = []

# --- Funções Auxiliares ---
def formatar_tempo(segundos):
    segundos = int(segundos)
    h = segundos // 3600
    m = (segundos % 3600) // 60
    return f"{h}h {m}m" if h > 0 else f"{m}m"

def formatar_relogio(segundos):
    s = int(segundos)
    return f"{s//3600:02d}:{(s%3600)//60:02d}:{s%60:02d}"

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
st.sidebar.title("StudyHub v7")
menu = st.sidebar.radio("Menu", ["🏠 Home", "⏳ Pomodoro", "✅ Tarefas"])
if st.session_state.sessao_estudo:
    status = "🟢 Estudando" if st.session_state.sessao_estudo['rodando'] else "🟡 Pausado"
    st.sidebar.info(f"{status}: {st.session_state.sessao_estudo['materia']}")

# --- Lógica de Atualização do Tempo no Ciclo ---
# Se estiver rodando um item do ciclo, atualiza o 'cumprido' dele em tempo real para a barra mexer
if st.session_state.sessao_estudo and st.session_state.sessao_estudo['rodando']:
    idx = st.session_state.sessao_estudo.get('index_ciclo')
    if idx is not None and 0 <= idx < len(st.session_state.ciclo_estudos):
        # Calcula quanto tempo passou nesta sessão atual
        delta = (datetime.now() - st.session_state.sessao_estudo['inicio']).total_seconds()
        # O total cumprido é o que já tinha antes + o delta atual
        # Nota: Só atualizamos visualmente aqui, o salvamento real acontece no 'Finalizar'
        tempo_real_atual = st.session_state.sessao_estudo['acumulado'] + delta
        # Atualizamos o estado do ciclo TEMPORARIAMENTE para refletir no visual
        st.session_state.ciclo_estudos[idx]['cumprido'] = tempo_real_atual / 60 # Convertendo para minutos

# --- Conteúdo Principal ---
if menu == "🏠 Home":
    st.title("🎓 Dashboard")
    
    # --- Calendário (Expansível) ---
    if 'ano_cal' not in st.session_state:
        st.session_state.ano_cal = datetime.now().year; st.session_state.mes_cal = datetime.now().month
    with st.expander("📅 Ver Calendário", expanded=False):
        c_prev, c_mes, c_next = st.columns([1, 6, 1])
        if c_prev.button("⬅️"): st.session_state.mes_cal -= 1
        c_mes.markdown(f"<h4 style='text-align:center'>{calendar.month_name[st.session_state.mes_cal]}</h4>", unsafe_allow_html=True)
        if c_next.button("➡️"): st.session_state.mes_cal += 1
        desenhar_calendario(st.session_state.ano_cal, st.session_state.mes_cal)
    st.divider()

    # =======================================================
    # 0. VERIFICAÇÃO INICIAL (Se não tem matérias)
    # =======================================================
    lista_materias = list(st.session_state.materias.keys())
    if not lista_materias:
        st.markdown("""<div style="text-align:center; padding:20px; border:1px dashed #ccc; border-radius:10px;">
            <h3>👋 Comece por aqui!</h3><p>Cadastre sua primeira matéria para desbloquear o sistema.</p></div>""", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3,3,2])
        nm, nc = c1.text_input("Matéria"), c2.text_input("Conteúdo")
        if c3.button("Salvar", type="primary"):
            if nm and nc: st.session_state.materias[nm] = [nc]; st.rerun()
    else:
        # =======================================================
        # 1. SESSÃO ATIVA (Player Principal)
        # =======================================================
        st.subheader("🚀 Sessão Ativa")
        with st.container(border=True):
            # MODO SELEÇÃO
            if st.session_state.sessao_estudo is None:
                c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
                m_rap = c1.selectbox("Matéria", lista_materias, key="m_quick")
                c_rap = c2.selectbox("Conteúdo", st.session_state.materias.get(m_rap, ["Geral"]), key="c_quick")
                meta_rap = c3.number_input("Meta", 5, 120, 45, label_visibility="collapsed")
                if c4.button("▶ Iniciar", type="primary", use_container_width=True):
                    st.session_state.sessao_estudo = {
                        "materia": m_rap, "conteudo": c_rap, "meta": meta_rap, 
                        "inicio": datetime.now(), "acumulado": 0, "rodando": True, "index_ciclo": None
                    }
                    st.rerun()
                
                # Gerenciador (Expander)
                with st.expander("⚙️ Gerenciar Matérias"):
                    tab1, tab2, tab3 = st.tabs(["➕ Add", "✏️ Edit", "🗑️ Del"])
                    with tab1:
                        c_a1, c_a2, c_a3 = st.columns([3,3,2])
                        nm = c_a1.text_input("Nova Matéria", key="nm_add")
                        nt = c_a2.text_input("Tópico", key="nt_add")
                        if c_a3.button("Salvar", key="btn_add"):
                            if nm and nt: st.session_state.materias[nm] = [nt]; st.success("Ok!"); time.sleep(0.5); st.rerun()
                    with tab3:
                         md = st.selectbox("Excluir", lista_materias, key="del_sel")
                         if st.button("Confirmar Exclusão"): del st.session_state.materias[md]; st.rerun()

            # MODO RODANDO
            else:
                dados = st.session_state.sessao_estudo
                total_seg = dados['acumulado'] + ((datetime.now()-dados['inicio']).total_seconds() if dados['rodando'] else 0)
                # Atualiza ciclo em tempo real se vinculado
                if dados.get('index_ciclo') is not None:
                     st.session_state.ciclo_estudos[dados['index_ciclo']]['cumprido'] = total_seg / 60

                c_txt, c_time, c_act = st.columns([3, 4, 3])
                with c_txt:
                    st.markdown(f"### {dados['materia']}")
                    st.caption(f"Conteúdo: {dados.get('conteudo', 'Geral')}")
                    st.progress(min(total_seg / (dados['meta']*60), 1.0))
                with c_time:
                    cor = "#48bb78" if dados['rodando'] else "#ecc94b"
                    st.markdown(f"<h1 style='color:{cor};text-align:center;margin:0'>{formatar_relogio(total_seg)}</h1>", unsafe_allow_html=True)
                with c_act:
                    st.write("")
                    kp, ks = st.columns(2)
                    if dados['rodando']:
                        if kp.button("⏸ Pausar", use_container_width=True):
                            st.session_state.sessao_estudo['acumulado'] = total_seg
                            st.session_state.sessao_estudo['rodando'] = False
                            st.rerun()
                    else:
                        if kp.button("▶ Retomar", use_container_width=True):
                            st.session_state.sessao_estudo['inicio'] = datetime.now()
                            st.session_state.sessao_estudo['rodando'] = True
                            st.rerun()
                    if ks.button("⏹ Finalizar", type="primary", use_container_width=True):
                        # Salva histórico
                        hj = datetime.now().strftime("%Y-%m-%d")
                        h, a = st.session_state.historico_estudos.get(hj, (0, 0))
                        st.session_state.historico_estudos[hj] = (h + (total_seg/3600), a + 1)
                        # Salva progresso final no ciclo e marca done
                        idx = dados.get('index_ciclo')
                        if idx is not None:
                            st.session_state.ciclo_estudos[idx]['cumprido'] = total_seg / 60
                            st.session_state.ciclo_estudos[idx]['status'] = 'done'
                        
                        st.session_state.sessao_estudo = None
                        st.rerun()
                if dados['rodando']: time.sleep(1); st.rerun()

        st.write("##")

        # =======================================================
        # 2. MEU CICLO DE ESTUDOS (Visual Novo!)
        # =======================================================
        
        # --- Lógica dos Cálculos Globais ---
        total_meta_global = sum([item['meta'] for item in st.session_state.ciclo_estudos])
        total_cumprido_global = sum([item.get('cumprido', 0) for item in st.session_state.ciclo_estudos])
        
        percent_global = (total_cumprido_global / total_meta_global * 100) if total_meta_global > 0 else 0
        restante_global = max(0, total_meta_global - total_cumprido_global)
        
        # Layout Header do Ciclo
        col_header_L, col_header_R = st.columns([2, 1])
        with col_header_L:
            st.subheader("🔁 Meu Ciclo de Estudos")
        with col_header_R:
             with st.popover("➕ Adicionar ao Ciclo"):
                m_c = st.selectbox("Matéria", lista_materias, key="ciclo_add_m")
                meta_c = st.number_input("Meta (min)", 15, 120, 45, step=5)
                if st.button("Adicionar"):
                    # Agora inicializamos com 'cumprido': 0
                    st.session_state.ciclo_estudos.append({"materia": m_c, "meta": meta_c, "cumprido": 0, "status": "pending"})
                    st.rerun()

        if not st.session_state.ciclo_estudos:
            st.info("Seu ciclo está vazio. Adicione matérias no botão acima ➕")
        else:
            # --- DISPLAY GLOBAL (Igual à imagem - Parte de Cima) ---
            st.markdown(f"""
            <div style="margin-bottom: 30px;">
                <div style="display:flex; align-items:baseline; justify-content:space-between;">
                    <span class="big-percent">{percent_global:.1f}%</span>
                    <span class="meta-text">Falta: {formatar_tempo(restante_global*60)} <br> Meta Total: {formatar_tempo(total_meta_global*60)}</span>
                </div>
                <div class="progress-bg"><div class="progress-fill" style="width: {min(percent_global, 100)}%; background-color: #ffeb3b;"></div></div>
            </div>
            <h4 style="color:#666; margin-bottom:15px;">Etapas</h4>
            """, unsafe_allow_html=True)

            # --- LISTA DE ETAPAS (Igual à imagem - Parte de Baixo) ---
            for i, item in enumerate(st.session_state.ciclo_estudos):
                # Cálculos Individuais
                meta_min = item['meta']
                cump_min = item.get('cumprido', 0)
                percent_item = (cump_min / meta_min * 100) if meta_min > 0 else 0
                falta_min = max(0, meta_min - cump_min)
                
                # Definição de Cores/Status
                cor_barra = "#48bb78" if item['status'] == 'done' else "#4299e1" if item['status'] == 'active' else "#cbd5e0"
                if percent_item >= 100: cor_barra = "#48bb78" # Verde se completou

                # Colunas para alinhar Botão Play à direita
                col_card, col_btn = st.columns([5, 1])
                
                with col_card:
                    st.markdown(f"""
                    <div class="etapa-card">
                        <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                            <span class="item-title">{item['materia']}</span>
                            <span class="meta-text" style="color:#ff6b6b;">Falta: {formatar_tempo(falta_min*60)} <span style="color:#ccc">/ Meta: {formatar_tempo(meta_min*60)}</span></span>
                        </div>
                        <div class="progress-bg" style="height:6px;">
                            <div class="progress-fill" style="width: {min(percent_item, 100)}%; background-color: {cor_barra};"></div>
                        </div>
                        <div style="text-align:right; font-size:0.8rem; color:#888; margin-top:3px;">{percent_item:.1f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_btn:
                    # Lógica do Botão Play
                    st.write("") # Espaçamento para alinhar verticalmente
                    st.write("") 
                    
                    disabled = False
                    if st.session_state.sessao_estudo is not None: disabled = True # Bloqueia se já tem um rodando
                    if item['status'] == 'done' and percent_item >= 100: disabled = True # Bloqueia se já acabou
                    
                    label_btn = "▶"
                    if item['status'] == 'active': label_btn = "Em Andamento"
                    
                    if not disabled:
                        if st.button(label_btn, key=f"play_stage_{i}"):
                            st.session_state.sessao_estudo = {
                                "materia": item['materia'], "meta": meta_min,
                                "inicio": datetime.now(), 
                                "acumulado": cump_min * 60, # Converte min de volta pra segundos pro timer
                                "rodando": True, "index_ciclo": i, "conteudo": "Ciclo"
                            }
                            item['status'] = 'active'
                            st.rerun()

            # Botão Limpar (Discreto)
            if st.button("🗑️ Reiniciar Ciclo", help="Apaga todas as etapas acima"):
                st.session_state.ciclo_estudos = []
                st.rerun()

elif menu == "⏳ Pomodoro":
    st.header("Pomodoro")
elif menu == "✅ Tarefas":
    st.header("Tarefas")
