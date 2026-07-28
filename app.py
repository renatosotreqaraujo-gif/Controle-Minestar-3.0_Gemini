import streamlit as st
import pandas as pd
from ping3 import ping
import time
from database import get_connection, hash_password, init_db

# Inicializa o BD
init_db()

# Configuração da página e Tema Caterpillar
st.set_page_config(page_title="Monitoramento de Rede - Mina", layout="wide", page_icon="🚜")

st.markdown("""
    <style>
    .stApp { background-color: #121212; color: #FFFFFF; }
    .stButton>button { background-color: #FFCD00; color: #000000; font-weight: bold; border-radius: 4px; border: none; }
    .stButton>button:hover { background-color: #E5B800; color: #000000; }
    div[data-baseweb="tab-list"] { background-color: #1E1E1E; }
    </style>
""", unsafe_allow_html=True)

# Session State para Autenticação
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.username = None

def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM usuarios WHERE username = ? AND password = ?", 
                   (username, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    return user[0] if user else None

# TELA DE LOGIN
if not st.session_state.logged_in:
    st.title("🚜 Sistema de Monitoramento de Rede")
    st.subheader("Autenticação de Usuário")
    
    with st.form("login_form"):
        user_input = st.text_input("Usuário")
        pass_input = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Entrar")
        
        if submit:
            role = login_user(user_input, pass_input)
            if role:
                st.session_state.logged_in = True
                st.session_state.user_role = role
                st.session_state.username = user_input
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")
    st.stop()

# BARRA LATERAL (LOGOUT)
st.sidebar.title(f"👤 {st.session_state.username}")
st.sidebar.caption(f"Perfil: **{st.session_state.user_role}**")
if st.sidebar.button("Sair"):
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.username = None
    st.rerun()

st.title("🚜 Monitoramento de Rede - Operação Mina")

# DEFINE ABAS BASEADO NO PERFIL
tabs_list = ["📊 Monitoramento", "🎯 Ping Pontual", "⚙️ Cadastrar Equipamentos"]
if st.session_state.user_role == "Admin":
    tabs_list.append("👥 Gestão de Usuários")

tabs = st.tabs(tabs_list)

# --- ABA 1: MONITORAMENTO CONTINUO ---
with tabs[0]:
    st.header("Monitoramento de Ativos de Rede")
    conn = get_connection()
    df_eq = pd.read_sql_query("SELECT id, nome, ip, setor, tipo FROM equipamentos", conn)
    conn.close()
    
    if st.button("🔄 Atualizar Status Agora"):
        st.rerun()
        
    if not df_eq.empty:
        results = []
        for _, row in df_eq.iterrows():
            # Executa Ping (Timeout de 1s)
            response = ping(row['ip'], timeout=1)
            status = "🟢 ONLINE" if response is not None and response is not False else "🔴 OFFLINE"
            latency = f"{round(response * 1000, 2)} ms" if isinstance(response, float) else "N/A"
            
            results.append({
                "ID": row['id'],
                "Equipamento": row['nome'],
                "IP": row['ip'],
                "Setor": row['setor'],
                "Tipo": row['tipo'],
                "Status": status,
                "Latência": latency
            })
        
        st.dataframe(pd.DataFrame(results), use_container_width=True)
    else:
        st.info("Nenhum equipamento cadastrado.")

# --- ABA 2: PING PONTUAL ---
with tabs[1]:
    st.header("Teste de Ping Pontual")
    ip_to_ping = st.text_input("Digite o IP para testar (ou escolha um da lista abaixo):")
    
    conn = get_connection()
    df_eq = pd.read_sql_query("SELECT nome, ip FROM equipamentos", conn)
    conn.close()
    
    if not df_eq.empty:
        selected_eq = st.selectbox("Ou selecione um equipamento cadastrado:", ["Nenhum"] + df_eq['nome'].tolist())
        if selected_eq != "Nenhum":
            ip_to_ping = df_eq[df_eq['nome'] == selected_eq]['ip'].values[0]
            
    if st.button("Disparar Ping"):
        if ip_to_ping:
            with st.spinner(f"Disparando ping para {ip_to_ping}..."):
                res = ping(ip_to_ping, timeout=2)
                if res is not None and res is not False:
                    st.success(f"✅ Sucesso! Resposta em {round(res * 1000, 2)} ms")
                else:
                    st.error(f"❌ Falha! O IP {ip_to_ping} não respondeu ao ping.")
        else:
            st.warning("Por favor, informe um IP válido.")

# --- ABA 3: CADASTRO DE EQUIPAMENTOS ---
with tabs[2]:
    st.header("Cadastro e Gestão de Equipamentos")
    
    if st.session_state.user_role in ["Admin", "Avançado"]:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Cadastro Manual")
            with st.form("add_eq_form"):
                nome = st.text_input("Nome do Equipamento")
                ip = st.text_input("Endereço IP")
                setor = st.text_input("Setor/Área")
                tipo = st.selectbox("Tipo", ["Roteador", "Switch", "Câmera", "Servidor", "Outro"])
                submit = st.form_submit_button("Cadastrar")
                
                if submit and nome and ip:
                    try:
                        conn = get_connection()
                        conn.execute("INSERT INTO equipamentos (nome, ip, setor, tipo) VALUES (?, ?, ?, ?)",
                                     (nome, ip, setor, tipo))
                        conn.commit()
                        conn.close()
                        st.success("Equipamento cadastrado com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao cadastrar (IP já existente?): {e}")

        with col2:
            st.subheader("Upload de Planilha (.xlsx)")
            uploaded_file = st.file_uploader("Suba um arquivo Excel com as colunas: Nome, IP, Setor, Tipo", type=['xlsx'])
            if uploaded_file:
                try:
                    df_upload = pd.read_excel(uploaded_file)
                    conn = get_connection()
                    for _, row in df_upload.iterrows():
                        conn.execute("INSERT OR REPLACE INTO equipamentos (nome, ip, setor, tipo) VALUES (?, ?, ?, ?)",
                                     (str(row['Nome']), str(row['IP']), str(row['Setor']), str(row['Tipo'])))
                    conn.commit()
                    conn.close()
                    st.success("Planilha importada com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao processar arquivo: {e}")
    else:
        st.warning("Seu perfil (Leitura) não tem permissão para cadastrar ou alterar equipamentos.")

    st.divider()
    st.subheader("Equipamentos Cadastrados")
    conn = get_connection()
    df_all = pd.read_sql_query("SELECT * FROM equipamentos", conn)
    conn.close()
    
    st.dataframe(df_all, use_container_width=True)
    
    if st.session_state.user_role in ["Admin", "Avançado"] and not df_all.empty:
        eq_to_delete = st.selectbox("Selecione um equipamento para excluir:", df_all['nome'].tolist())
        if st.button("🗑️ Excluir Equipamento"):
            conn = get_connection()
            conn.execute("DELETE FROM equipamentos WHERE nome = ?", (eq_to_delete,))
            conn.commit()
            conn.close()
            st.success(f"Equipamento '{eq_to_delete}' excluído.")
            st.rerun()

# --- ABA 4: GESTÃO DE USUÁRIOS (SÓ ADMIN) ---
if st.session_state.user_role == "Admin":
    with tabs[3]:
        st.header("Gerenciamento de Usuários")
        
        col_u1, col_u2 = st.columns(2)
        with col_u1:
            st.subheader("Criar Novo Usuário")
            with st.form("new_user_form"):
                new_user = st.text_input("Nome de Usuário")
                new_pass = st.text_input("Senha", type="password")
                new_role = st.selectbox("Perfil", ["Admin", "Avançado", "Leitura"])
                btn_user = st.form_submit_button("Criar Usuário")
                
                if btn_user and new_user and new_pass:
                    try:
                        conn = get_connection()
                        conn.execute("INSERT INTO usuarios (username, password, role) VALUES (?, ?, ?)",
                                     (new_user, hash_password(new_pass), new_role))
                        conn.commit()
                        conn.close()
                        st.success("Usuário criado!")
                        st.rerun()
                    except Exception as e:
                        st.error("Erro ao criar usuário (nome de usuário já existe).")
                        
        conn = get_connection()
        users_df = pd.read_sql_query("SELECT id, username, role FROM usuarios", conn)
        conn.close()
        
        with col_u2:
            st.subheader("Usuários Existentes")
            st.dataframe(users_df, use_container_width=True)
            
            user_to_del = st.selectbox("Excluir Usuário:", users_df[users_df['username'] != 'admin']['username'].tolist())
            if st.button("🗑️ Excluir Usuário"):
                conn = get_connection()
                conn.execute("DELETE FROM usuarios WHERE username = ?", (user_to_del,))
                conn.commit()
                conn.close()
                st.success("Usuário removido!")
                st.rerun()
