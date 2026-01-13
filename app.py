import streamlit as st
import time

# --- Configuração Inicial ---
st.set_page_config(
    page_title="StudyHub Pro", 
    page_icon="🎓", 
    layout="wide"  # Layout mais espaçoso
)

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
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Horas Estudadas", "12h", "+2h hoje")
    col2.metric("Tarefas Concluídas", "8", "3 pendentes")
    col3.metric("Flashcards Revisados", "25", "Média 80%")
    
    st.info("💡 Dica do dia: Faça pausas curtas para manter o cérebro ativo!")

elif menu == "⏳ Pomodoro":
    st.header("⏳ Cronômetro de Foco")
    col1, col2 = st.columns(2)
    with col1:
        tempo = st.number_input("Minutos de foco:", min_value=1, value=25)
    with col2:
        st.write("##") # Espaçamento
        iniciar = st.button("🚀 Iniciar Foco")
    
    if iniciar:
        barra = st.progress(0)
        status = st.empty()
        total = tempo * 60
        for i in range(total):
            status.text(f"Restam {total - i} segundos...")
            barra.progress((i + 1) / total)
            time.sleep(0.01) # Rápido para teste (mude para 1.0 para tempo real)
        st.balloons()
        st.success("Ciclo concluído! Hora da pausa. ☕")

elif menu == "✅ Tarefas":
    st.header("✅ Lista de Tarefas")
    
    if 'tarefas' not in st.session_state:
        st.session_state.tarefas = []

    c1, c2 = st.columns([3, 1])
    with c1:
        nova_tarefa = st.text_input("O que você precisa estudar hoje?")
    with c2:
        st.write("##")
        if st.button("Adicionar"):
            if nova_tarefa:
                st.session_state.tarefas.append(nova_tarefa)

    st.divider()
    if st.session_state.tarefas:
        for i, tarefa in enumerate(st.session_state.tarefas):
            col_a, col_b = st.columns([4, 1])
            col_a.checkbox(tarefa, key=f"check_{i}")
            if col_b.button("🗑️", key=f"del_{i}"):
                st.session_state.tarefas.pop(i)
                st.rerun()
    else:
        st.caption("Nenhuma tarefa pendente. Aproveite o descanso!")

elif menu == "🧠 Flashcards":
    st.header("🧠 Revisão Rápida")
    
    # Banco de dados simples de perguntas (depois podemos colocar em arquivos)
    flashcards = {
        "Qual a capital da França?": "Paris",
        "Fórmula da Água?": "H2O",
        "Raiz quadrada de 144?": "12",
        "Quem descobriu o Brasil?": "Pedro Álvares Cabral"
    }
    
    pergunta = st.selectbox("Escolha uma pergunta:", list(flashcards.keys()))
    
    if st.button("Ver Resposta"):
        st.info(f"Resposta: **{flashcards[pergunta]}**")

elif menu == "📝 Anotações":
    st.header("📝 Caderno Digital")
    materia = st.selectbox("Matéria:", ["Matemática", "História", "Português", "Programação"])
    texto = st.text_area(f"Anotações de {materia}:", height=200)
    
    if st.button("Salvar Anotação"):
        st.toast(f"Anotação de {materia} salva com sucesso!", icon="💾")
