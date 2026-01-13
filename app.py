import streamlit as st
import time
import calendar
from datetime import datetime, timedelta

# --- Configuração Inicial ---
st.set_page_config(
    page_title="StudyHub Pro", 
    page_icon="🎓", 
    layout="wide"
)

# --- CSS Personalizado ---
st.markdown("""
<style>
    .stSelectbox label { display: none; }
    div[data-testid="stExpander"] { border: none; box-shadow: none; }
</style>
""", unsafe_allow_html=True)

# --- Inicialização de Estado ---
if 'materias' not in st.session_state:
    st.session_state.materias = {
        "Matemática": ["Álgebra", "Geometria", "Cálculo"],
        "História": ["Revolução Francesa", "Brasil Colônia", "Guerra Fria"],
        "Português": ["Gramática", "Literatura", "Redação"],
        "Programação": ["Python", "Streamlit", "Data Science"]
    }

if 'sessao_estudo' not in st.session_state:
    # Estrutura nova para suportar PAUSA:
    # { 
    #   "materia": str, 
    #   "conteudo": str, 
    #   "inicio": datetime, (hora que começou ou retomou)
    #   "acumulado": int, (segundos guardados de pausas anteriores)
    #   "rodando": bool (se está contando ou pausado)
    # }
    st.session_state.sessao_estudo = None 

if 'historico_estudos' not in st.session_state:
    hoje = datetime.now()
    ano, mes = hoje.year, hoje.month
    st.session_state.historico_estudos = {
        f"{ano}-{mes:02d}-05": (2.7, 3),
        f"{ano}-{mes:02d}-08": (3.25, 4),
        f"{ano}-{mes:02d}-10": (6.28, 5),
    }

# --- Funções Auxiliares ---
def formatar_tempo(segundos):
    segundos = int(segundos)
    horas = segundos // 3600
    minutos = (segundos % 3600) // 60
    seg_restantes = segundos % 60
    return f"{horas:02d}:{minutos:02d}:{seg_restantes:02d}"

def desenhar_calendario(ano, mes):
    cal = calendar.Calendar(firstweekday=6)
    mes_days = cal.monthdayscalendar(ano, mes)
    dias_semana = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
    
    cols = st.columns(7)
    for i, dia in enumerate(dias_semana):
        cols[i].markdown(f"**{dia}**", unsafe_allow_html=True)
    
    for semana in mes_days:
        cols = st.columns(7)
        for i, dia_num in enumerate(semana):
            with cols[i]:
                if dia_num != 0:
                    chave = f"{ano}-{mes:02d}-{dia_num:02d}"
                    horas, ativ = st.session_state.historico_estudos.get(chave, (0, 0))
                    
                    if horas > 0:
                        h = int(horas)
                        m = int((horas % 1) * 60)
                        st.markdown(f"""
                        <div style="background-color: #eafce0; border-radius: 6px; padding: 8px; height: 90px;">
                            <div style="font-weight: bold; color: #666;">{dia_num}</div>
                            <div style="font-size: 13px; margin-top: 5px;">
                                📖 {ativ}<br>⏱️ {h}h{m:02d}m
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="background-color: #f9f9f9; border-radius: 6px; padding: 8px; height: 90px;">
                            <div style="font-weight: bold; color: #ccc;">{dia_num}</div>
                        </div>
                        """, unsafe_allow_html=True)

# --- Barra Lateral ---
st.sidebar.title("StudyHub")
menu = st.sidebar.radio("Menu", ["🏠 Home", "⏳ Pomodoro", "✅ Tarefas"])

if st.session_state.sessao_estudo:
    status = "🟢 Estudando" if st.session_state.sessao_estudo['rodando'] else "🟡 Pausado"
    st.sidebar.info(f"{status}: {st.session_state.sessao_estudo['materia']}")

# --- Conteúdo Principal ---
if menu == "🏠 Home":
    st.title("🎓 Dashboard de Estudos")
    
    # Métricas
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Horas", "45h", "+2h")
    c2.metric("Sessões", "12", "+1")
    c3.metric("Eficiência", "88%", "Estável")
    
    st.divider()
    
    # --- Calendário ---
    if 'ano_cal' not in st.session_state:
        st.session_state.ano_cal = datetime.now().year
        st.session_state.mes_cal = datetime.now().month

    col_a, col_b, col_c = st.columns([1, 6, 1])
    with col_a:
        if st.button("⬅️"):
            st.session_state.mes_cal -= 1
            if st.session_state.mes_cal == 0: st.session_state.mes_cal = 12; st.session_state.ano_cal -= 1
            st.rerun()
    with col_b:
        st.markdown(f"<h3 style='text-align: center'>{calendar.month_name[st.session_state.mes_cal]} {st.session_state.ano_cal}</h3>", unsafe_allow_html=True)
    with col_c:
        if st.button("➡️"):
            st.session_state.mes_cal += 1
            if st.session_state.mes_cal == 13: st.session_state.mes_cal = 1; st.session_state.ano_cal += 1
            st.rerun()
            
    desenhar_calendario(st.session_state.ano_cal, st.session_state.mes_cal)
    
    st.write("##")
    
    # --- ÁREA DE CONTROLE DE ESTUDOS ---
    st.subheader("🚀 Sessão de Estudos")
    
    with st.container(border=True):
        
        # MODO 1: Escolha (Se não existe sessão)
        if st.session_state.sessao_estudo is None:
            c_mat, c_cont, c_btn, c_add = st.columns([3, 3, 2, 2])
            
            with c_mat:
                st.caption("Matéria")
                materia_sel = st.selectbox("Selecione a matéria", list(st.session_state.materias.keys()), key="sel_mat")
            
            with c_cont:
                st.caption("Conteúdo")
                conteudos = st.session_state.materias[materia_sel]
                conteudo_sel = st.selectbox("Selecione o conteúdo", conteudos, key="sel_cont")
            
            with c_btn:
                st.caption("Ação")
                if st.button("▶ Iniciar", type="primary", use_container_width=True):
                    st.session_state.sessao_estudo = {
                        "materia": materia_sel,
                        "conteudo": conteudo_sel,
                        "inicio": datetime.now(),
                        "acumulado": 0,
                        "rodando": True
                    }
                    st.rerun()
            
            with c_add:
                st.caption("Gerenciar")
                with st.popover("➕ Nova"):
                    nova_mat = st.text_input("Matéria")
                    novo_topico = st.text_input("Tópico")
                    if st.button("Salvar"):
                        if nova_mat and novo_topico:
                            st.session_state.materias[nova_mat] = [novo_topico]
                            st.rerun()

        # MODO 2: Cronômetro Ativo (Rodando ou Pausado)
        else:
            dados = st.session_state.sessao_estudo
            
            # Cálculo do tempo atual
            if dados['rodando']:
                agora = datetime.now()
                tempo_atual_sessao = (agora - dados['inicio']).total_seconds()
                tempo_total = dados['acumulado'] + tempo_atual_sessao
            else:
                tempo_total = dados['acumulado']
            
            # Layout
            col_info, col_timer, col_acoes = st.columns([3, 3, 4])
            
            with col_info:
                status_icon = "🟢" if dados['rodando'] else "🟡"
                st.markdown(f"### {status_icon} {dados['materia']}")
                st.caption(f"Conteúdo: {dados['conteudo']}")
            
            with col_timer:
                cor_tempo = "#48bb78" if dados['rodando'] else "#ecc94b" # Verde ou Amarelo
                st.markdown(f"<h2 style='color: {cor_tempo}; text-align: center;'>{formatar_tempo(tempo_total)}</h2>", unsafe_allow_html=True)
            
            with col_acoes:
                st.write("") # Espaço para alinhar
                c_pause, c_stop = st.columns(2)
                
                with c_pause:
                    if dados['rodando']:
                        if st.button("⏸ Pausar", use_container_width=True):
                            # Salva o tempo decorrido no acumulado e para de rodar
                            st.session_state.sessao_estudo['acumulado'] = tempo_total
                            st.session_state.sessao_estudo['rodando'] = False
                            st.rerun()
                    else:
                        if st.button("▶ Retomar", use_container_width=True):
                            # Reinicia o contador de 'inicio'
                            st.session_state.sessao_estudo['inicio'] = datetime.now()
                            st.session_state.sessao_estudo['rodando'] = True
                            st.rerun()
                
                with c_stop:
                    if st.button("⏹ Finalizar", type="primary", use_container_width=True):
                        # Salva tudo e limpa
                        horas_totais = tempo_total / 3600
                        
                        data_hoje = datetime.now().strftime("%Y-%m-%d")
                        hist_atual = st.session_state.historico_estudos.get(data_hoje, (0, 0))
                        
                        novo_tempo = hist_atual[0] + horas_totais
                        nova_qtd = hist_atual[1] + 1
                        
                        st.session_state.historico_estudos[data_hoje] = (novo_tempo, nova_qtd)
                        st.session_state.sessao_estudo = None
                        st.balloons()
                        time.sleep(1)
                        st.rerun()

            # Refresh automático se estiver rodando
            if dados['rodando']:
                time.sleep(1)
                st.rerun()

elif menu == "⏳ Pomodoro":
    st.header("Pomodoro")
    st.write("Em breve...")

elif menu == "✅ Tarefas":
    st.header("Tarefas")
    # ... código de tarefas ...
