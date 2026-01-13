import streamlit as st
import time
import calendar
import json
import os
from datetime import datetime

# --- Configuração Inicial ---
st.set_page_config(page_title="StudyHub Pro", page_icon="🎓", layout="wide")

# --- ARQUIVO DE BANCO DE DADOS ---
ARQUIVO_DB = "dados_estudos.json"

# --- Funções de Persistência (Salvar e Carregar) ---
def carregar_dados():
    """Lê o arquivo JSON e retorna os dados. Se não existir, retorna padrão vazio."""
    if not os.path.exists(ARQUIVO_DB):
        return {
            "materias": {},
            "historico": {},
            "ciclo": []
        }
    try:
        with open(ARQUIVO_DB, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return {"materias": {}, "historico": {}, "ciclo": []}

def salvar_dados():
    """Pega o estado atual e salva no arquivo JSON."""
    dados_para_salvar = {
        "materias": st.session_state.materias,
        "historico": st.session_state.historico_estudos,
        "ciclo": st.session_state.ciclo_estudos
    }
    with open(ARQUIVO_DB, "w", encoding="utf-8") as f:
        json.dump(dados_para_salvar, f, ensure_ascii=False, indent=4)

# --- Inicialização de Estado (CARREGANDO DO ARQUIVO) ---
if 'dados_carregados' not in st.session_state:
    db = carregar_dados()
    st.session_state.materias = db.get("materias", {})
    st.session_state.historico_estudos = db.get("historico", {})
    st.session_state.ciclo_estudos = db.get("ciclo", [])
    st.session_state.dados_carregados = True

if 'sessao_estudo' not in st.session_state:
    st.session_state.sessao_estudo = None 

# --- CSS Personalizado ---
st.markdown("""
<style>
    .stSelectbox label { display: none; }
    div[data-testid="stExpander"] { border: 1px solid #e2e8f0; border-radius: 8px; }
    .progress-bg { background-color: #f1f3f5; border-radius: 10px; height: 10px; width: 100%; margin: 5px 0; }
    .progress-fill { background-color: #ffeb3b; height: 100%; border-radius: 10px; transition: width 0.5s ease-in-out; }
    .big-percent { font-size: 3rem; font-weight: bold; color: #333; line-height: 1;}
    .meta-text { font-size: 0.85rem; color: #888; text-align: right; }
    .item-title { font-size: 1.1rem; font-weight: 600; color: #444; }
    .etapa-card { background-color: white; padding: 15px; border-radius: 10px; border: 1px solid #eee; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
</style>
""", unsafe_allow_html=True)

# --- Constantes ---
MESES_PT = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}

# --- Funções Auxiliares de Visualização ---
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
                    horas, ativ = st.session_state.historico_estudos.get(chave, [0, 0]) # [horas, qtd]
                    # Compatibilidade se salvou como tupla antiga
                    if isinstance(horas, list) or isinstance(horas, tuple): h_val, a_val = horas[0], horas[1]
                    else: h_val, a_val = 0, 0

                    if h_val > 0:
                        h, m = int(h_val), int((h_val % 1) * 60)
                        st.markdown(f"""<div style="background-color:#eafce0;border-radius:6px;padding:8px;height:90px;">
                            <div style="font-weight:bold;color:#666;">{dia}</div>
                            <div style="font-size:12px;">📖 {a_val}<br>⏱️ {h}h{m:02d}m</div></div>""", unsafe_allow_html=True)
                    else:
                        st.markdown(f"""<div style="background-color:#f9f9f9;border-radius:6px;padding:8px;height:90px;">
                            <div style="color:#ccc;">{dia}</div></div>""", unsafe_allow_html=True)

# --- Barra Lateral ---
st.sidebar.title("StudyHub Pro")
menu = st.sidebar.radio("Menu", ["🏠 Home", "⏳ Pomodoro", "✅ Tarefas"])
st.sidebar.divider()
if st.sidebar.button("🗑️ Resetar Tudo (Apaga DB)"):
    if os.path.exists(ARQUIVO_DB): os.remove(ARQUIVO_DB)
    st.session_state.clear()
    st.rerun()

if st.session_state.sessao_estudo:
    status = "🟢 Estudando" if st.session_state.sessao_estudo['rodando'] else "🟡 Pausado"
    st.sidebar.info(f"{status}: {st.session_state.sessao_estudo['materia']}")
    
    # Atualiza visual do ciclo em tempo real
    if st.session_state.sessao_estudo['rodando']:
        idx = st.session_state.sessao_estudo.get('index_ciclo')
        if idx is not None and 0 <= idx < len(st.session_state.ciclo_estudos):
            delta = (datetime.now() - st.session_state.sessao_estudo['inicio']).total_seconds()
            tempo_real = st.session_state.sessao_estudo['acumulado'] + delta
            st.session_state.ciclo_estudos[idx]['cumprido'] = tempo_real / 60

# --- Conteúdo Principal ---
if menu == "🏠 Home":
    st.title("🎓 Dashboard")
    
    # Calendário
    if 'ano_cal' not in st.session_state: st.session_state.ano_cal = datetime.now().year; st.session_state.mes_cal = datetime.now().month
    with st.expander("📅 Calendário de Estudos", expanded=True):
        c_prev, c_mes, c_next = st.columns([1, 6, 1])
        if c_prev.button("⬅️"): st.session_state.mes_cal -= 1
        c_mes.markdown(f"<h4 style='text-align:center'>{MESES_PT.get(st.session_state.mes_cal, 'Mês')} {st.session_state.ano_cal}</h4>", unsafe_allow_html=True)
        if c_next.button("➡️"): st.session_state.mes_cal += 1
        desenhar_calendario(st.session_state.ano_cal, st.session_state.mes_cal)
    st.divider()

    lista_materias = list(st.session_state.materias.keys())
    
    # Se não tiver matérias, mostra tela de boas-vindas
    if not lista_materias:
        st.markdown("""<div style="text-align:center; padding:20px; border:1px dashed #ccc; border-radius:10px;">
            <h3>👋 Bem-vindo!</h3><p>Cadastre sua primeira matéria. (Seus dados serão salvos automaticamente)</p></div>""", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3,3,2])
        nm, nc = c1.text_input("Matéria"), c2.text_input("Conteúdo")
        if c3.button("Salvar Inicial", type="primary"):
            if nm and nc: 
                st.session_state.materias[nm] = [nc]
                salvar_dados() # <--- SALVA NO ARQUIVO
                st.rerun()
    else:
        # Sessão Ativa
        st.subheader("🚀 Sessão Ativa")
        with st.container(border=True):
            if st.session_state.sessao_estudo is None:
                c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
                m_rap = c1.selectbox("Matéria", lista_materias)
                c_rap = c2.selectbox("Conteúdo", st.session_state.materias.get(m_rap, ["Geral"]))
                meta_rap = c3.number_input("Meta", 5, 120, 45, label_visibility="collapsed")
                if c4.button("▶ Iniciar", type="primary", use_container_width=True):
                    st.session_state.sessao_estudo = {
                        "materia": m_rap, "conteudo": c_rap, "meta": meta_rap, 
                        "inicio": datetime.now(), "acumulado": 0, "rodando": True, "index_ciclo": None
                    }
                    st.rerun()
                
                with st.expander("⚙️ Gerenciar Matérias"):
                    tab1, tab2, tab3 = st.tabs(["➕ Add", "✏️ Edit", "🗑️ Del"])
                    with tab1:
                        c_a1, c_a2, c_a3 = st.columns([3,3,2])
                        nm = c_a1.text_input("Nova Matéria", key="nm_add")
                        nt = c_a2.text_input("Tópico", key="nt_add")
                        if c_a3.button("Salvar", key="btn_add"):
                            if nm and nt: 
                                st.session_state.materias[nm] = [nt]
                                salvar_dados() # <--- SALVA NO ARQUIVO
                                st.success("Salvo!"); time.sleep(0.5); st.rerun()
                    with tab3:
                         md = st.selectbox("Excluir", lista_materias, key="del_sel")
                         if st.button("Confirmar Exclusão"): 
                             del st.session_state.materias[md]
                             salvar_dados() # <--- SALVA NO ARQUIVO
                             st.rerun()
            else:
                dados = st.session_state.sessao_estudo
                total_seg = dados['acumulado'] + ((datetime.now()-dados['inicio']).total_seconds() if dados['rodando'] else 0)
                
                c_txt, c_time, c_act = st.columns([3, 4, 3])
                with c_txt:
                    st.markdown(f"### {dados['materia']}")
                    st.progress(min(total_seg / (dados['meta']*60), 1.0))
                with c_time:
                    cor = "#48bb78" if dados['rodando'] else "#ecc94b"
                    st.markdown(f"<h1 style='color:{cor};text-align:center;margin:0'>{formatar_relogio(total_seg)}</h1>", unsafe_allow_html=True)
                with c_act:
                    st.write(""); kp, ks = st.columns(2)
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
                        hj = datetime.now().strftime("%Y-%m-%d")
                        h, a = st.session_state.historico_estudos.get(hj, [0, 0])
                        # Garante compatibilidade e soma
                        if isinstance(h, list): h_val, a_val = h[0], h[1]
                        else: h_val, a_val = 0, 0
                        
                        st.session_state.historico_estudos[hj] = [h_val + (total_seg/3600), a_val + 1]
                        
                        idx = dados.get('index_ciclo')
                        if idx is not None:
                            st.session_state.ciclo_estudos[idx]['cumprido'] = total_seg / 60
                            st.session_state.ciclo_estudos[idx]['status'] = 'done'
                        
                        st.session_state.sessao_estudo = None
                        salvar_dados() # <--- SALVA TUDO NO ARQUIVO
                        st.balloons(); st.rerun()
                if dados['rodando']: time.sleep(1); st.rerun()
        st.write("##")

        # Ciclo de Estudos
        total_meta = sum([i['meta'] for i in st.session_state.ciclo_estudos])
        total_cump = sum([i.get('cumprido', 0) for i in st.session_state.ciclo_estudos])
        percent = (total_cump / total_meta * 100) if total_meta > 0 else 0
        
        col_L, col_R = st.columns([2, 1])
        with col_L: st.subheader("🔁 Ciclo de Estudos")
        with col_R:
             with st.popover("➕ Adicionar ao Ciclo"):
                m_c = st.selectbox("Matéria", lista_materias)
                meta_c = st.number_input("Meta (min)", 15, 120, 45, step=5)
                if st.button("Adicionar"):
                    st.session_state.ciclo_estudos.append({"materia": m_c, "meta": meta_c, "cumprido": 0, "status": "pending"})
                    salvar_dados() # <--- SALVA NO ARQUIVO
                    st.rerun()

        if st.session_state.ciclo_estudos:
            st.markdown(f"""<div style="margin-bottom: 30px;"><div style="display:flex; justify-content:space-between;">
                <span class="big-percent">{percent:.1f}%</span><span class="meta-text">Meta Global: {formatar_tempo(total_meta*60)}</span></div>
                <div class="progress-bg"><div class="progress-fill" style="width: {min(percent, 100)}%; background-color: #ffeb3b;"></div></div></div>""", unsafe_allow_html=True)
            
            for i, item in enumerate(st.session_state.ciclo_estudos):
                p_item = (item.get('cumprido', 0) / item['meta'] * 100)
                cor = "#48bb78" if p_item >= 100 else "#4299e1" if item['status'] == 'active' else "#cbd5e0"
                c_card, c_btn = st.columns([5, 1])
                with c_card:
                    st.markdown(f"""<div class="etapa-card"><div style="display:flex; justify-content:space-between;"><span class="item-title">{item['materia']}</span>
                        <span class="meta-text">Meta: {item['meta']}m</span></div><div class="progress-bg" style="height:6px;"><div class="progress-fill" style="width:{min(p_item, 100)}%;background-color:{cor}"></div></div></div>""", unsafe_allow_html=True)
                with c_btn:
                    st.write(""); st.write("")
                    dis = True if (st.session_state.sessao_estudo or p_item >= 100) else False
                    if not dis and st.button("▶", key=f"p_{i}"):
                        st.session_state.sessao_estudo = {
                            "materia": item['materia'], "meta": item['meta'], "inicio": datetime.now(), 
                            "acumulado": item.get('cumprido',0)*60, "rodando": True, "index_ciclo": i, "conteudo": "Ciclo"
                        }
                        item['status'] = 'active'
                        salvar_dados() # <--- SALVA STATUS
                        st.rerun()
            
            if st.button("🗑️ Limpar Ciclo"):
                st.session_state.ciclo_estudos = []
                salvar_dados() # <--- LIMPA E SALVA
                st.rerun()

elif menu == "⏳ Pomodoro": st.header("Pomodoro")
elif menu == "✅ Tarefas": st.header("Tarefas")
