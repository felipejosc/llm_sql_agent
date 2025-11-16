import streamlit as st
from agent_core.agent import Agent
from agent_core.tools import get_available_tools

if st.button("Limpar sessão"):
    st.session_state.clear()
    st.rerun()
# Configuração da página
st.set_page_config(
    page_title="SQL Agent • LangChain + Streamlit",
    page_icon=" ",
    layout="wide"
)

st.title("SQL Agent • LangChain + Streamlit")


if "agent" not in st.session_state:
    tools = get_available_tools()
    st.session_state.agent = Agent(tools)

if "messages" not in st.session_state:
    st.session_state.messages = []



for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])



prompt = st.chat_input("Digite sua pergunta...")

if prompt:
    # mostra pergunta do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # placeholder para resposta
    with st.chat_message("assistant"):
        response_placeholder = st.empty()

        try:
            # chama o agente
            response_text = st.session_state.agent.ask(prompt)

            # mostra resposta
            response_placeholder.markdown(response_text)

            # adiciona ao histórico
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_text
            })

        except Exception as e:
            response_placeholder.error(f"Erro: {e}")
