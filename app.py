import streamlit as st
import time

st.set_page_config(page_title="Meu Portal de Estudos", page_icon="📚")

st.title("📚 Foco nos Estudos")
st.write("Bem-vindo ao seu ambiente de produtividade.")

menu = st.sidebar.selectbox("Escolha uma ferramenta", ["Pomodoro", "To-Do List"])

if menu == "Pomodoro":
    st.header("⏳ Cronômetro Pomodoro")
    tempo = st.number_input("Minutos de foco:", min_value=1, value=25)
    if st.button("Iniciar Foco"):
        barra = st.progress(0)
        total_segundos = tempo * 60
        for i in range(total_segundos):
            time.sleep(1)
            barra.progress((i + 1) / total_segundos)
        st.success("Tempo esgotado! Hora de uma pausa. ☕")

elif menu == "To-Do List":
    st.header("✅ Lista de Tarefas")
    if 'tarefas' not in st.session_state:
        st.session_state.tarefas = []
    nova_tarefa = st.text_input("Adicionar nova tarefa:")
    if st.button("Adicionar") and nova_tarefa:
        st.session_state.tarefas.append(nova_tarefa)
    st.write("### Suas Tarefas:")
    for i, tarefa in enumerate(st.session_state.tarefas):
        st.checkbox(tarefa, key=i)
