import streamlit as st
import time
import calendar
from datetime import datetime, timedelta

# --- Configuração Inicial ---
st.set_page_config(page_title="StudyHub Pro", page_icon="🎓", layout="wide")

# --- CSS Personalizado ---
st.markdown("""
<style>
    .stSelectbox label { display: none; }
    div[data-testid="stExpander"] { border: none; box-shadow: none; }
    /* Estilo para os cards do ciclo */
    .cycle-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 5px solid #cbd5e0;
    }
    .cycle-card.active { border-left-color: #4299e1; background-color: #ebf8ff; } /* Azul */
    .cycle-card.done { border-left-color: #48bb78; background-color: #f0fff4; opacity: 0.7; } /* Verde */
</style>
""", unsafe_allow_html=True)

# --- Inicialização de Estado ---
if 'materias' not in st.session_state:
    st.session_state.materias = {
        "Matemática": ["Álgebra", "Geometria", "Cálculo"],
        "História": ["Rev. Francesa", "Brasil Colônia"],
        "Português": ["Gramática", "Literatura"],
        "Inglês": ["Vocabulary", "Grammar"]
    }

# Estrutura do Ciclo: Lista de dicionários
# [{'id': 1, 'materia': 'Math', 'meta': 30 (min), 'status': 'pendente'}]
if 'ciclo_estudos' not in st.session_state:
    st.session_state.ciclo_estudos = []

if 'sessao_estudo' not in st.session_state:
    # Agora inclui 'index_ciclo' para saber qual item do ciclo estamos fazendo
    st.session_state.sessao_estudo = None 

if 'historico_estudos' not in st.session_state:
    hoje = datetime.now()
    st.session_state.historico_estudos = {
        f"{hoje.year}-{hoje.month:02d}-05": (2.7, 3),
        f"{hoje.year}-{hoje.month:02d}-08": (3.25, 4),
    }

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
st.sidebar.title("StudyHub 4.0")
menu = st.sidebar.radio("Menu", ["🏠 Home", "⏳ Pomodoro", "✅ Tarefas"])

if st.session_state.sessao_estudo:
    status = "🟢 Estudando" if st.session_state.sessao_estudo['rodando'] else "🟡 Pausado"
    st.sidebar.info(f"{status}: {st.session_state.sessao_estudo['materia']}")

# --- Conteúdo Principal ---
if menu == "🏠 Home":
    st.title("🎓 Dashboard")
    
    # Calendário (Simplificado visualmente para focar no resto)
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
    # 1. ÁREA DE ESTUDO ATIVO (PLAYER)
    # ==========================================
    st.subheader("🚀 Sessão Ativa")
    
    with st.container(border=True):
        # CENÁRIO A: Nenhuma sessão ativa -> Mostra seletor rápido
        if st.session_state.sessao_estudo is None:
            st.info("Selecione uma matéria no Ciclo abaixo ou inicie uma rápida aqui.")
            
            c1, c2, c3 = st.columns([3, 2, 2])
            mat_rapida = c1.selectbox("Matéria Rápida", list(st.session_state.materias.keys()))
            meta_rapida = c2.number_input("Meta (min)", min_value=10, value=60, step=5)
            if c3.button("▶ Iniciar Avulso", type="primary", use_container_width=True):
                st.session_state.sessao_estudo = {
                    "materia": mat_rapida, "meta": meta_rapida, "inicio": datetime.now(),
                    "acumulado": 0, "rodando": True, "index_ciclo": None # None significa avulso
                }
                st.rerun()

        # CENÁRIO B: Sessão rodando ou pausada
        else:
            dados = st.session_state.sessao_estudo
            
            # Lógica do Tempo
            if dados['rodando']:
                tempo_decorrido = (datetime.now() - dados['inicio']).total_seconds()
                total_segundos = dados['acumulado'] + tempo_decorrido
            else:
                total_segundos = dados['acumulado']
            
            # Lógica da Meta (Progresso)
            meta_segundos = dados['meta'] * 60
            progresso = min(total_segundos / meta_segundos, 1.0)
            
            # Layout do Player
            col_txt, col_timer, col_btns = st.columns([3, 4, 3])
            
            with col_txt:
                st.markdown(f"### 📖 {dados['materia']}")
                st.caption(f"Meta: {dados['meta']} min")
                # Barra de progresso visual
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
                    # Salva no histórico
                    hoje_str = datetime.now().strftime("%Y-%m-%d")
                    h_atual, ativ_atual = st.session_state.historico_estudos.get(hoje_str, (0, 0))
                    st.session_state.historico_estudos[hoje_str] = (h_atual + (total_segundos/3600), ativ_atual + 1)
                    
                    # Se veio do CICLO, marca como concluído
                    idx = dados.get('index_ciclo')
                    if idx is not None:
                        st.session_state.ciclo_estudos[idx]['status'] = 'done'
                    
                    st.session_state.sessao_estudo = None
                    st.balloons()
                    st.rerun()

            if dados['rodando']: time.sleep(1); st.rerun()

    st.write("##")

    # ==========================================
    # 2. ÁREA DO CICLO DE ESTUDOS (PLAYLIST)
    # ==========================================
    st.subheader("🔁 Meu Ciclo de Estudos")
    
    # Formulário para Adicionar
    with st.container():
        c_add_mat, c_add_meta, c_add_btn = st.columns([3, 2, 2])
        nova_materia_ciclo = c_add_mat.selectbox("Adicionar Matéria ao Ciclo", list(st.session_state.materias.keys()))
        nova_meta_ciclo = c_add_meta.number_input("Meta (minutos)", min_value=15, value=45, step=5, key="meta_ciclo")
        
        if c_add_btn.button("➕ Adicionar à Fila", use_container_width=True):
            st.session_state.ciclo_estudos.append({
                "materia": nova_materia_ciclo,
                "meta": nova_meta_ciclo,
                "status": "pending" # pending, active, done
            })
            st.rerun()

    st.write("---")

    # Lista de Cards do Ciclo
    if not st.session_state.ciclo_estudos:
        st.caption("Seu ciclo está vazio. Adicione matérias acima!")
    else:
        for i, item in enumerate(st.session_state.ciclo_estudos):
            # Define estilo visual baseado no status
            if item['status'] == 'done':
                css_class = "done"
                icon = "✅"
                btn_disabled = True
                label_btn = "Concluído"
            elif item['status'] == 'active':
                css_class = "active"
                icon = "🔵"
                btn_disabled = True
                label_btn = "Em Andamento..."
            else:
                css_class = ""
                icon = "⚪"
                btn_disabled = False
                label_btn = "▶ Iniciar"
                # Se já tem sessão rodando (mesmo que avulsa), bloqueia iniciar outro
                if st.session_state.sessao_estudo is not None:
                    btn_disabled = True
            
            # HTML Card Container
            st.markdown(f"""
            <div class="cycle-card {css_class}">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <strong style="font-size:1.1rem;">{icon} {item['materia']}</strong>
                        <div style="color:#666; font-size:0.9rem;">Meta: {item['meta']} minutos</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Botão (Fora do HTML para usar lógica do Streamlit)
            # Usamos colunas negativas para jogar o botão para a direita alinhado visualmente
            c_vazio, c_btn_card = st.columns([4, 1]) 
            if not btn_disabled:
                if c_btn_card.button(label_btn, key=f"start_cycle_{i}"):
                    # Lógica de Início do Ciclo
                    st.session_state.sessao_estudo = {
                        "materia": item['materia'],
                        "meta": item['meta'],
                        "inicio": datetime.now(),
                        "acumulado": 0,
                        "rodando": True,
                        "index_ciclo": i
                    }
                    item['status'] = 'active'
                    st.rerun()

    # Botão para limpar ciclo
    if st.session_state.ciclo_estudos:
        if st.button("🗑️ Limpar Ciclo Completo"):
            st.session_state.ciclo_estudos = []
            st.rerun()

elif menu == "⏳ Pomodoro":
    st.header("Pomodoro")
    st.write("Em construção...")

elif menu == "✅ Tarefas":
    st.header("Tarefas")
