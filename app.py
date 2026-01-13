import streamlit as st
import time
import calendar
from datetime import datetime

# --- Configuração Inicial ---
st.set_page_config(
    page_title="StudyHub Pro", 
    page_icon="🎓", 
    layout="wide"
)

# --- Funções Auxiliares ---
def desenhar_calendario_minimalista(ano, mes, dados_estudos):
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
                if dia_num == 0:
                    st.write("")
                else:
                    chave_data = f"{ano}-{mes:02d}-{dia_num:02d}"
                    # Pega os dados (horas e atividades) ou retorna (0, 0) se não houver
                    horas, atividades = dados_estudos.get(chave_data, (0, 0))
                    
                    # --- ESTILO MINIMALISTA AQUI ---
                    if horas > 0:
                        # Calcula horas e minutos para o formato "2h42m"
                        h = int(horas)
                        m = int((horas % 1) * 60)
                        
                        # Cor de fundo verde claro (estilo da imagem 5)
                        cor_fundo = "#eafce0" 
                        # Se quiser destacar um dia específico (como o 10 na imagem), 
                        # podemos usar uma cor mais vibrante: "#ccff99"

                        st.markdown(f"""
                        <div style="
                            background-color: {cor_fundo};
                            border-radius: 6px;
                            padding: 8px 10px;
                            height: 100px;
                            color: #333;
                            font-family: sans-serif;">
                            <div style="font-size: 18px; font-weight: bold; color: #666;">{dia_num}</div>
                            <div style="margin-top: 10px; font-size: 14px; line-height: 1.6;">
                                📖 {atividades} Ativ.<br>
                                ⏱️ {h}h{m:02d}m
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        # Dia vazio (cinza bem claro, sem borda)
                        st.markdown(f"""
                        <div style="
                            background-color: #f9f9f9;
                            border-radius: 6px;
                            padding: 8px 10px;
                            height: 100px;">
                            <div style="font-size: 18px; font-weight: bold; color: #ccc;">{dia_num}</div>
                        </div>
                        """, unsafe_allow_html=True)

# --- Barra Lateral e Menu (Mantido igual) ---
st.sidebar.title("🧰 Ferramentas")
menu = st.sidebar.radio(
    "Navegação", 
    ["🏠 Home", "⏳ Pomodoro", "✅ Tarefas", "🧠 Flashcards", "📝 Anotações"]
)

if menu == "🏠 Home":
    st.title("🎓 Bem-vindo ao StudyHub")
    st.write("Seu painel central para produtividade e aprendizado.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Horas Estudadas", "12h", "+2h hoje")
    col2.metric("Tarefas Concluídas", "8", "3 pendentes")
    col3.metric("Flashcards Revisados", "25", "Média 80%")
    
    st.divider()
    
    st.subheader("📅 Histórico de Estudos")

    if 'ano_cal' not in st.session_state:
        hoje = datetime.now()
        st.session_state.ano_cal = hoje.year
        st.session_state.mes_cal = hoje.month

    col_nav1, col_nav2, col_nav3 = st.columns([1, 5, 1])
    with col_nav1:
        if st.button("⬅️ Anterior"):
            st.session_state.mes_cal -= 1
            if st.session_state.mes_cal == 0:
                st.session_state.mes_cal = 12
                st.session_state.ano_cal -= 1
            st.rerun()
    with col_nav2:
        nome_mes = calendar.month_name[st.session_state.mes_cal]
        st.markdown(f"<h3 style='text-align: center;'>{nome_mes} {st.session_state.ano_cal}</h3>", unsafe_allow_html=True)
    with col_nav3:
        if st.button("Próximo ➡️"):
            st.session_state.mes_cal += 1
            if st.session_state.mes_cal == 13:
                st.session_state.mes_cal = 1
                st.session_state.ano_cal += 1
            st.rerun()

    # --- Dados Simulados Atualizados ---
    # Agora guardamos uma tupla: (horas, atividades)
    dados_simulados = {
        f"{st.session_state.ano_cal}-{st.session_state.mes_cal:02d}-05": (2.7, 3),
        f"{st.session_state.ano_cal}-{st.session_state.mes_cal:02d}-06": (1.73, 2),
        f"{st.session_state.ano_cal}-{st.session_state.mes_cal:02d}-07": (4.58, 4),
        f"{st.session_state.ano_cal}-{st.session_state.mes_cal:02d}-08": (3.25, 4),
        f"{st.session_state.ano_cal}-{st.session_state.mes_cal:02d}-09": (4.02, 2),
        # Vamos deixar o dia 10 com mais destaque, como na imagem
        f"{st.session_state.ano_cal}-{st.session_state.mes_cal:02d}-10": (6.28, 5),
    }

    desenhar_calendario_minimalista(st.session_state.ano_cal, st.session_state.mes_cal, dados_simulados)

# --- Outras páginas (Mantidas iguais para economizar espaço) ---
elif menu == "⏳ Pomodoro":
    st.header("⏳ Cronômetro de Foco")
    # ... (código do pomodoro igual ao anterior) ...
elif menu == "✅ Tarefas":
    st.header("✅ Lista de Tarefas")
    # ... (código de tarefas igual ao anterior) ...
elif menu == "🧠 Flashcards":
    st.header("🧠 Revisão")
    st.info("Funcionalidade em construção...")
elif menu == "📝 Anotações":
    st.header("📝 Caderno")
    st.text_area("Escreva aqui...", height=200)
