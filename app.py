import os
import streamlit as st
from groq import Groq

# Configuração da página
st.set_page_config(
    page_title="LembreMente - Seu Assistente Amigo",
    page_icon="💛",
    layout="centered"
)

# Inicialização do cliente Groq
# No Render, a variável de ambiente GROQ_API_KEY deve ser configurada
api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    st.error("Chave de API do Groq não encontrada. Configure a variável GROQ_API_KEY.")
    st.stop()

client = Groq(api_key=api_key)

# Inicialização do estado da sessão (Memória de Lembretes e Histórico)
if "lembretes" not in st.session_state:
    st.session_state.lembretes = []

if "messages" not in st.session_state:
    st.session_state.messages = []

# System Prompt focado em empatia, paciência e acolhimento
SYSTEM_PROMPT = f"""
Você é o 'LembreMente', um assistente virtual extremamente carismático, paciente, gentil e carinhoso.
Seu objetivo principal é ajudar pessoas com perda de memória ou Alzheimer a se lembrarem de seus compromissos, rotinas, medicação e tarefas diárias.

Instruções de Comportamento:
1. Responda SEMPRE de forma calma, acolhedora, com frases curtas, claras e fáceis de entender.
2. Seja reconfortante. Caso o usuário demonstre confusão ou ansiedade, acalme-o com carinho.
3. Utilize os lembretes cadastrados no sistema para responder às dúvidas do usuário sobre compromissos.
4. Se o usuário perguntar algo que não está cadastrado nos lembretes, responda com gentileza e sugira cadastrar na aba lateral.

Lembretes Atualmente Cadastrados no Sistema:
{st.session_state.lembretes if st.session_state.lembretes else "Nenhum lembrete cadastrado até o momento."}
"""

# Interface Principal
st.title("💛 LembreMente")
st.subheader("Seu assistente carinhoso para o dia a dia")

# Barra Lateral (Sidebar) para Cadastrar Lembretes
with st.sidebar:
    st.header("📌 Cadastrar Lembrete")
    st.write("Guarde aqui compromissos, remédios ou tarefas importantes.")
    
    with st.form("form_lembrete", clear_on_submit=True):
        titulo = st.text_input("O que não pode esquecer?", placeholder="Ex: Tomar remédio da pressão")
        horario = st.text_input("Qual horário / dia?", placeholder="Ex: Todos os dias às 08h")
        submitted = st.form_submit_button("Salvar Lembrete")
        
        if submitted and titulo:
            st.session_state.lembretes.append({"compromisso": titulo, "horario": horario})
            st.success("Lembrete salvo com sucesso!")

    st.divider()
    st.header("📋 Seus Lembretes")
    if st.session_state.lembretes:
        for idx, item in enumerate(st.session_state.lembretes, 1):
            st.write(f"**{idx}. {item['compromisso']}**")
            if item['horario']:
                st.caption(f"🕒 {item['horario']}")
    else:
        st.info("Nenhum lembrete salvo ainda.")

# Exibição do Chat
st.write("---")

# Renderiza histórico de mensagens
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada do usuário
if user_input := st.chat_input("Como posso te ajudar agora? (ex: 'O que tenho para fazer hoje?')"):
    # Adiciona e exibe mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Prepara o contexto para a API do Groq
    messages_payload = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in st.session_state.messages:
        messages_payload.append({"role": msg["role"], "content": msg["content"]})

    # Resposta da API
    with st.chat_message("assistant"):
        with st.spinner("Pensando com carinho..."):
            try:
                chat_completion = client.chat.completions.create(
                    messages=messages_payload,
                    model="llama-3.3-70b-versatile",
                    temperature=0.5,
                    max_tokens=500,
                )
                response = chat_completion.choices[0].message.content
                st.markdown(response)
                
                # Salva a resposta no histórico
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error("Ops! Tive um probleminha para responder. Pode perguntar de novo?")