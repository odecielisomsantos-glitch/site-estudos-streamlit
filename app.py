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

# --- CSS Personalizado para a Barra Inferior ---
# Isso deixa a barra com aquele visual "Dark" e botões bonitos
st.markdown("""
<style>
    .stSelectbox label { display: none; } /* Esconde labels padrão para ficar limpo */
    div[data-testid="stExpander"] { border: none; box-shadow: none; }
    
    /* Estilo para a barra de status flutuante (opcional, se quiser fixar no futuro) */
    .status-box {
        padding: 15px;
        border-radius: 10px;
        background-color: #f0f2f6;
        border-left: 5px solid #48bb78;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- Inicialização de Estado (Banco de Dados Temporário) ---
if 'materias' not in st.session_state:
    st.session_state.materias = {
        "Matemática": ["Álgebra", "Geometria", "Cálculo"],
        "História": ["Revolução Francesa", "Brasil Colônia", "Guerra Fria"],
        "Português": ["Gramática", "Literatura", "Redação"],
        "Programação": ["Python", "Streamlit", "Data Science"]
    }

if 'sessao_estudo' not in st.session_state:
    # Guarda o estado atual: None ou dicionário com dados do estudo
    st.session_state.sessao_estudo = None 

if 'historico_estudos' not in st.session_state:
    # Formato: "YYYY-MM-DD": (horas_float, qtd_atividades)
    hoje = datetime.now()
    ano, mes = hoje.year, hoje.month
    st.session_state.historico_estudos = {
        f"{ano}-{mes:02d}-05": (2.7, 3),
        f"{ano}-{mes:02d}-08": (3.25, 4),
        f"{ano}-{mes:02d}-10": (6.28, 5),
    }

# --- Funções Auxiliares ---
def formatar_tempo(segundos):
    horas = int(segundos // 3600)
    minutos = int((segundos % 3600) // 60)
    seg_restantes = int(segundos % 60)
    return f"{horas:02d}:{minutos:02d}:{seg_restantes:02d}"

def desenhar_calendario(ano, mes):
    cal = calendar.Calendar(firstweekday=6)
    mes_days = cal.monthdayscalendar(ano, mes)
    dias_semana = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
    
    # Cabeçalho
    cols = st.columns(7)
    for i, dia in enumerate(dias_semana):
        cols[i].markdown(f"**{dia}**", unsafe_allow_html=True)
    
    # Dias
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

# Se estiver estudando, mostra um aviso na sidebar
if st.session_state.sessao_estudo:
    inicio = st.session_state.sessao_estudo['inicio']
    delta = datetime.now() - inicio
    st.sidebar.success(f"📚 Estudando: {formatar_tempo(delta.total_seconds())}")

# --- Conteúdo Principal ---
if menu == "🏠 Home":
    st.title("🎓 Dashboard de Estudos")
    
    # Métricas (Estáticas para exemplo)
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
    
    st.write("##") # Espaço
    
    # --- BARRA DE CONTROLE DE ESTUDOS (NOVA) ---
    st.subheader("🚀 Iniciar Sessão")
    
    # Container estilizado
    with st.container(border=True):
        # Lógica: Se NÃO estiver estudando, mostra os selects. Se ESTIVER, mostra o Timer.
        if st.session_state.sessao_estudo is None:
            c_mat, c_cont, c_btn, c_add = st.columns([3, 3, 2, 2])
            
            with c_mat:
                st.caption("Matéria")
                materia_sel = st.selectbox("Selecione a matéria", list(st.session_state.materias.keys()), key="sel_mat")
            
            with c_cont:
                st.caption("Conteúdo")
                # Carrega conteúdos baseados na matéria selecionada
                conteudos = st.session_state.materias[materia_sel]
                conteudo_sel = st.selectbox("Selecione o conteúdo", conteudos, key="sel_cont")
            
            with c_btn:
                st.caption("Ação")
                if st.button("▶ Iniciar", type="primary", use_container_width=True):
                    # Inicia a sessão
                    st.session_state.sessao_estudo = {
                        "materia": materia_sel,
                        "conteudo": conteudo_sel,
                        "inicio": datetime.now()
                    }
                    st.rerun()
            
            with c_add:
                st.caption("Gerenciar")
                with st.popover("➕ Nova Matéria"):
                    nova_mat = st.text_input("Nome da Matéria")
                    novo_topico = st.text_input("Primeiro Tópico")
                    if st.button("Salvar"):
                        if nova_mat and novo_topico:
                            st.session_state.materias[nova_mat] = [novo_topico]
                            st.success("Adicionado!")
                            time.sleep(1)
                            st.rerun()

        else:
            # MODO ESTUDANDO (CRONÔMETRO ATIVO)
            dados = st.session_state.sessao_estudo
            agora = datetime.now()
            tempo_decorrido = (agora - dados['inicio']).total_seconds()
            
            # Layout do Timer Ativo
            col_info, col_timer, col_stop = st.columns([4, 3, 2])
            
            with col_info:
                st.markdown(f"### 📖 {dados['materia']}")
                st.caption(f"Focando em: {dados['conteudo']}")
            
            with col_timer:
                # Mostra o tempo grande
                st.markdown(f"<h2 style='color: #48bb78; text-align: center;'>{formatar_tempo(tempo_decorrido)}</h2>", unsafe_allow_html=True)
                
            with col_stop:
                st.write("") # Espaçamento vertical
                if st.button("⏹ Parar e Salvar", type="primary", use_container_width=True):
                    # 1. Calcula horas finais
                    horas_totais = tempo_decorrido / 3600
                    
                    # 2. Salva no histórico (banco de dados do calendário)
                    data_hoje = agora.strftime("%Y-%m-%d")
                    hist_atual = st.session_state.historico_estudos.get(data_hoje, (0, 0))
                    
                    novo_tempo = hist_atual[0] + horas_totais
                    nova_qtd = hist_atual[1] + 1
                    
                    st.session_state.historico_estudos[data_hoje] = (novo_tempo, nova_qtd)
                    
                    # 3. Limpa a sessão
                    st.session_state.sessao_estudo = None
                    st.balloons()
                    time.sleep(1)
                    st.rerun()
            
            # Auto-refresh simples para o timer "andar" visualmente a cada segundo
            time.sleep(1)
            st.rerun()

elif menu == "⏳ Pomodoro":
    st.header("Pomodoro")
    st.write("A contagem global continua rodando mesmo aqui!")
    if st.session_state.sessao_estudo:
         st.info("Você tem uma sessão de estudos ativa na Home!")

elif menu == "✅ Tarefas":
    st.header("Tarefas")
    # (Seu código de tarefas aqui...)
