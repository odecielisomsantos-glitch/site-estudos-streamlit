import streamlit as st
import json
import os

# Configuração da página
st.set_page_config(page_title="Foco na Missão", page_icon="🎯")

# --- FUNÇÕES DE PERSISTÊNCIA DE DADOS ---
DB_FILE = "usuarios.json"

def carregar_usuarios():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {"odecielisonsonadson02@gmail.com": "ode123"}

def salvar_usuario(email, senha):
    usuarios = carregar_usuarios()
    usuarios[email] = senha
    with open(DB_FILE, "w") as f:
        json.dump(usuarios, f)

# --- SISTEMA DE ESTADO DA SESSÃO ---
if "logado" not in st.session_state:
    st.session_state.logado = False

# --- INTERFACE ---

st.title("🎯 Foco na Missão")
st.subheader("Plataforma de Registro e Análise de Estudos")

if not st.session_state.logado:
    tab1, tab2 = st.tabs(["Login", "Cadastrar Novo Usuário"])

    with tab1:
        st.write("### Acessar conta")
        email_input = st.text_input("Email")
        senha_input = st.text_input("Senha", type="password")
        
        if st.button("Entrar"):
            usuarios = carregar_usuarios()
            if email_input in usuarios and usuarios[email_input] == senha_input:
                st.session_state.logado = True
                st.success("Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")

    with tab2:
        st.write("### Criar nova conta")
        novo_email = st.text_input("Novo Email")
        nova_senha = st.text_input("Nova Senha", type="password")
        confirmar_senha = st.text_input("Confirme a Senha", type="password")

        if st.button("Cadastrar"):
            usuarios = carregar_usuarios()
            if novo_email in usuarios:
                st.warning("Este email já está cadastrado.")
            elif nova_senha != confirmar_senha:
                st.error("As senhas não coincidem.")
            elif novo_email == "" or nova_senha == "":
                st.error("Preencha todos os campos.")
            else:
                salvar_usuario(novo_email, nova_senha)
                st.success("Usuário cadastrado com sucesso! Agora vá para a aba de Login.")

else:
    # --- ÁREA LOGADA ---
    st.sidebar.write(f"Conectado como: {email_input if 'email_input' in locals() else 'Usuário'}")
    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()

    st.write("---")
    st.write("## Bem-vindo à sua área de estudos!")
    st.info("Aqui começaremos a registrar suas missões e análises.")
    
    # Exemplo de onde os registros entrarão futuramente
    st.date_input("Data do estudo")
    st.text_input("O que você estudou hoje?")
    st.button("Salvar Registro")
