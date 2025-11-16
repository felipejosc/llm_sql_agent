from __future__ import annotations

from datetime import datetime
from typing import List, Dict, Any

import json

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    SystemMessage,
    AIMessage,
    ToolMessage,
)
from langchain_groq import ChatGroq

from agent_core.config import Config
from agent_core.log_utils import log_panel


SYSTEM_PROMPT = """
Você é um agente SQL altamente preciso e confiável.

Regra 1 — Conversas Normais:
• Se a mensagem do usuário for uma saudação ou conversa casual (“olá”, “oi”, “tudo bem?”),
  responda normalmente sem usar ferramentas e sem gerar SQL.

Regra 2 — Consultas SQL:
• Se a mensagem envolver dados, tabelas, colunas, métricas, listagens ou análises,
  você deve usar ferramentas para descobrir a estrutura do banco
  e gerar a consulta SQL correta.

Regra 3 — Uso de Ferramentas:
• Use a ferramenta apropriada somente quando necessário.
• Nunca chame uma ferramenta sem fornecer todos os argumentos obrigatórios.
• Nunca invente nomes de tabelas ou colunas.
• Nunca execute SQL sem confirmar a estrutura primeiro.

Regra 4 — Segurança:
• Não faça suposições.
• Não retorne SQL se a pergunta não exigir SQL.
• Não use ferramentas para perguntas que não são sobre dados.

Seu objetivo é:
— Dar respostas corretas,
— Evitar erros,
— Minimizar chamadas de ferramentas,
— Evitar loops,
— Ser estável, profissional e previsível.

"""



def create_history() -> List[BaseMessage]:
    """Cria o histórico inicial com o SystemMessage."""
    return [SystemMessage(content=SYSTEM_PROMPT)]



class Agent:
    """Agente SQL com LangChain e Groq, usando ferramentas estruturadas"""

    def __init__(self, tools: List, llm: BaseChatModel | None = None, max_iterations: int = 8):
        self.tools = tools
        self.tools_dict: Dict[str, Any] = {t.name: t for t in tools}
        self.llm: BaseChatModel = llm or self._create_llm()
        self.max_iterations = max_iterations

        # histórico interno da conversa LLM 
        self.history: List[BaseMessage] = create_history()

        # bind das tools no LLM (para tool calling automático)
        self._llm_with_tools = self.llm.bind_tools(self.tools)

        # debug das tools disponíveis
        debug_lines = ["=== DEBUG TOOLS ==="]
        for t in self.tools:
            debug_lines.append(f"- {t.name} ({type(t).__name__})")
        log_panel("Agent Init – Tools carregadas", "\n".join(debug_lines))

    
    def _create_llm(self) -> BaseChatModel:
        return ChatGroq(
            api_key=Config.GROQ_API_KEY,
            model=Config.MODEL.name,
            temperature=Config.MODEL.temperature,
        )

  
    def ask(self, query: str) -> str:
        """
        Processa uma pergunta do usuário, chamando ferramentas
        quantas vezes forem necessárias (até max_iterations).
        Retorna APENAS o texto final para ser exibido no Streamlit.
        """
        log_panel("User Query", query)

        # começamos do histórico acumulado + nova pergunta
        messages: List[BaseMessage] = self.history.copy()
        messages.append(HumanMessage(content=query))

        n_iterations = 0

        while n_iterations < self.max_iterations:
            
            ai_msg: AIMessage = self._llm_with_tools.invoke(messages)
            messages.append(ai_msg)

            # log do passo do modelo
            log_panel(
                f"LLM Step {n_iterations + 1}",
                f"Content: {ai_msg.content}\nTool calls: {repr(ai_msg.tool_calls)}",
            )

            
            if not getattr(ai_msg, "tool_calls", None):
                final_text = ai_msg.content or "No answer generated."
                self.history = messages  # atualiza histórico interno
                return final_text

            
            for tool_call in ai_msg.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call.get("args", {}) or {}
                tool_call_id = tool_call.get("id")

                if tool_name not in self.tools_dict:
                    err_msg = f"Requested tool '{tool_name}' does not exist."
                    log_panel("Erro no Agente", err_msg)
                    messages.append(
                        ToolMessage(
                            content=err_msg,
                            tool_call_id=tool_call_id,
                        )
                    )
                    continue

                tool = self.tools_dict[tool_name]
                log_panel("Chamando tool", f"{tool_name}({tool_args})")

                try:
                    result = tool.invoke(tool_args)
                    # serialização segura (RealDictRow, bytes, etc.)
                    safe_result = json.dumps(
                        result,
                        ensure_ascii=False,
                        default=str,
                    )
                    log_panel("Resultado da tool", safe_result[:2000] + "...")
                    tool_msg = ToolMessage(
                        content=safe_result,
                        tool_call_id=tool_call_id,
                    )
                    messages.append(tool_msg)

                except Exception as e:
                    err_text = f"ERRO ao executar ferramenta {tool_name}: {repr(e)}"
                    log_panel("Erro SQL", err_text)
                    messages.append(
                        ToolMessage(
                            content=err_text,
                            tool_call_id=tool_call_id,
                        )
                    )

            n_iterations += 1

        # limite de iterações
        self.history = messages
        warn_msg = (
            "Desculpe, atingi o limite interno de passos ao tentar responder à sua "
            "pergunta. Tente reformular a consulta de forma mais específica."
        )
        log_panel("Limite de iterações atingido", warn_msg)
        return warn_msg
