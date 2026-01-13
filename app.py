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
def desenhar_calendario(ano, mes, dados_estudos):
    # Cria o objeto calendário
    cal = calendar.Calendar(firstweekday=6) # 6 = Domingo
    mes_days = cal.monthdayscalendar(ano, mes)
    
    # Nomes dos dias da semana
    dias_semana = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
    
    # Cabeçalho do Calendário (Dias da semana)
    cols = st.columns(7)
    for i, dia in enumerate(dias_semana):
        cols[i].markdown(f"**{dia}**", unsafe_allow_html=True)
    
    # Desenha os dias
    for semana in mes_days:
        cols = st.columns(7)
        for i, dia in enumerate(semana):
            with cols[i]:
                if dia == 0:
                    st.write("") # Dia vazio (mês anterior/próximo)
                else:
                    # Verifica se tem estudo nesse dia
                    chave_data = f"{ano}-{mes:02d}-{dia:02d}"
                    horas = dados_estudos.get(chave_data, 0)
                    
                    # Estilo do cartão do dia (HTML/CSS simples para dar cor)
                    if horas > 0:
                        # Dia COM estudo (Fundo verde claro)
                        st.markdown(f"""
                        <div style="
                            background-color: #e6fffa;
                            border: 1px solid #b2f5ea;
                            border-radius: 5px;
                            padding: 10px;
                            height: 100px;
                            text-align: center;">
                            <strong style="font-size: 20px;">{dia}</strong><br>
                            <span style="color: #2c7a7b; font-size: 14px;">📚 {horas}h</span>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        # Dia SEM estudo (Cinza básico)
                        st.markdown(f"""
                        <div style="
                            background-color: #f7fafc;
                            border: 1px solid #e2e8f0;
                            border-radius: 5px;
                            padding: 10px;
                            height: 100px;
                            color: #a0aec0;">
                            <strong style="font-size: 20px;">{dia}</strong>
                        </div>
                        """, unsafe_allow_html=True)

# --- Barra Lateral (Menu) ---
st.sidebar.title("🧰 Ferramentas")
menu = st.sidebar.radio(
    "Navegação", 
    ["🏠 Home", "⏳ Pomodoro", "✅ Tarefas", "🧠 Flashcards", "📝 Anotações"]
)

# --- Funcionalidades ---

if menu == "🏠 Home":
    st.title("🎓 Bem-vindo ao StudyHub")
    st.write("Seu painel central para produtividade e aprendizado.")
    
    # Métricas Superiores
    col1, col2, col3 = st.columns(3)
    col1.metric("Horas Estudadas", "12h", "+2h hoje")
    col2.metric("Tarefas Concluídas", "8", "3 pendentes")
    col3.metric("Flashcards Revisados", "25", "Média 80%")
    
    st.divider()
    
    # --- Lógica do Calendário ---
    st.subheader("📅 Histórico de Estudos")

    # Controle de Data (Ano e Mês Atual)
    if 'ano_cal' not in st.session_state:
        hoje = datetime.now()
        st.session_state.ano_cal = hoje.year
        st.session_state.mes_cal = hoje.month

    # Botões de Navegação do Calendário
    col_nav1, col_nav2, col_nav3 = st.columns([1, 5, 1])
    
    with col_nav1:
        if st.button("⬅️ Anterior"):
            st.session_state.mes_cal -= 1
            if st.session_state.mes_cal == 0:
                st.session_state.mes_cal = 12
                st.session_state.ano_cal -= 1
            st.rerun()

    with col_nav2:
        # Mostra o mês e ano centralizado
        nome_mes = calendar.month_name[st.session_state.mes_cal]
        st.markdown(f"<h3 style='text-align: center;'>{nome_mes} {st.session_state.ano_cal}</h3>", unsafe_allow_html=True)

    with col_nav3:
        if st.button("Próximo ➡️"):
            st.session_state.mes_cal += 1
            if st.session_state.mes_cal == 13:
                st.session_state.mes_cal = 1
                st.session_state.ano_cal += 1
            st.rerun()

    # Dados Fictícios (Simulando um banco de dados)
    # Formato: "AAAA-MM-DD": horas
    dados_simulados = {
        f"{st.session_state.ano_cal}-{st.session_state.mes_cal:02d}-05": 3,
        f"{st.session_state.ano_cal}-{st.session_state.mes_cal:02d}-08": 4.5,
        f"{st.session_state.ano_cal}-{st.session_state.mes_cal:02d}-12": 2,
        f"{st.session_state.ano_cal}-{st.session_state.mes_cal:02d}-20": 6,
    }

    # Chama a função que desenha
    desenhar_calendario(st.session_state.ano_cal, st.session_state.mes_cal, dados_simulados)


elif menu == "⏳ Pomodoro":
    st.header("⏳ Cronômetro de Foco")
    col1, col2 = st.columns(2)
    with col1:
        tempo = st.number_input("Minutos de foco:", min_value=1, value=25)
    with col2:
        st.write("##")
        iniciar = st.button("🚀 Iniciar Foco")
    
    if iniciar:
        barra = st.progress(0)
        status = st.empty()
        total = tempo * 60
        for i in range(total):
            status.text(f"Restam {total - i} segundos...")
            barra.progress((i + 1) / total)
            time.sleep(0.01) # Mude para 1.0 em produção
        st.success("Ciclo concluído! Hora da pausa. ☕")

elif menu == "✅ Tarefas":
    st.header("✅ Lista de Tarefas")
    if 'tarefas' not in st.session_state:
        st.session_state.tarefas = []
    
    nova = st.text_input("Nova tarefa:")
    if st.button("Adicionar") and nova:
        st.session_state.tarefas.append(nova)
        st.rerun()

    for i, t in enumerate(st.session_state.tarefas):
        st.checkbox(t, key=i)

elif menu == "🧠 Flashcards":
    st.header("🧠 Revisão")
    st.info("Funcionalidade em construção...")

elif menu == "📝 Anotações":
    st.header("📝 Caderno")
    st.text_area("Escreva aqui...", height=200)
