import os
import logging
from langgraph.graph import MessagesState, END
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage, AIMessage, ToolMessage
from langgraph.types import interrupt
from typing import Annotated, Any, Dict, List, Optional, Sequence, TypedDict
from langgraph.prebuilt import ToolNode

from openai import RateLimitError, APIError, APIConnectionError, APITimeoutError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


from src.llm.factory_class import create_llm
from src.utils.config import load_config
from src.agent.tools import ToolDefinitions
from src.llm.prompts import query_analysis_prompt, initial_analysis_prompt

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class State(MessagesState):
    summary: str
    clarification_needed: bool
    query: Optional[str]
    next_step: Optional[str]

class AIAgent:
    def __init__(self):
        
        cfg = load_config()["llm"]
        self.llm = create_llm(cfg)
        self.tools_definitions = ToolDefinitions()
        self.tools_list = [self.tools_definitions._get_hr_policies(),
                            self.tools_definitions._get_time_tool(),
                            self.tools_definitions._get_http_response]
        # self.vector_store = VectorDBManager()


    RETRY_EXCEPTIONS = (RateLimitError, APIConnectionError, APITimeoutError)
    @retry(
            retry=retry_if_exception_type(RETRY_EXCEPTIONS),
            wait=wait_exponential(multiplier=1, min=4, max=60),
            stop=stop_after_attempt(5),
            before_sleep=lambda retry_state: logger.info(f"Retrying in {retry_state.next_action.sleep} seconds... (Attempt {retry_state.attempt_number})")
        )
    def safe_llm_invoke(self,messages, **kwargs):
        """Safely invoke the LLM with comprehensive error handling"""
        try:
            return self.llm.chat(messages, **kwargs)
        except RateLimitError as e:
            logger.warning(f"Rate limit exceeded: {str(e)}")
            raise
        except APIConnectionError as e:
            logger.warning(f"Connection error: {str(e)}")
            raise
        except APITimeoutError as e:
            logger.warning(f"API timeout: {str(e)}")
            raise
        except APIError as e:
            if hasattr(e, 'http_status') and 500 <= e.http_status < 600:
                logger.warning(f"Server error ({e.http_status}): {str(e)}")
                raise  
            else:
                logger.error(f"API error: {str(e)}")
                raise RuntimeError(f"Non-retryable API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during LLM invocation: {str(e)}", exc_info=True)
            raise RuntimeError(f"Unexpected error: {str(e)}")
    
    def initial_analysis(self, state: State):
        """Analyze the initial user query to determine if human feedback is needed or not."""
        try:
            logger.info(f"User Query: {state['messages'][-1].content}")
            summary = state.get("summary", "")
            conversation_messages = [message for message in state["messages"] if message.type in ("human", "system")
            or (message.type == "ai" and not message.tool_calls)
            ]
            system_message = initial_analysis_prompt.format(summary=summary)
            prompt = [SystemMessage(system_message)] + conversation_messages
            response = self.safe_llm_invoke(prompt)
            response_text = response.content
            logger.info(f"initial_analysis call successful")
            logger.info(f"Follow-up response: {response_text}")
            if response_text.strip().upper().startswith("RETRIEVE"):
                return {
                    "next_step": "react_agent",
                    "clarification_needed": False,
                    "remove_tool_message": False
                }
            elif response_text.strip().upper().startswith("IRRELEVANT"):
                end_statement = response_text.split("IRRELEVANT", 1)[1].strip()
                
                return {
                    "next_step": END,
                     "messages": [AIMessage(content=end_statement)],
                }
            elif response_text.strip().upper().startswith("ANSWER"):
                answer_to_query = response_text.split("ANSWER", 1)[1].strip()
                
                return {
                    "next_step": END,
                     "messages": [AIMessage(content=answer_to_query)],
                }
            else:
                return {
                    "next_step": END,
                    "clarification_needed": False,
                    "messages": [AIMessage(content=response_text)],
                    "remove_tool_message": False
                }

        except Exception as e:
            # Handle the case where all retries failed
            logger.error(f"API call failed: {str(e)}")
            return {
                "messages": [AIMessage(content="I'm sorry, I'm having trouble responding right now. Please try again later.")]
            }

    def react_agent(self, state: State):
        """Analyze the user query to determine if and which tools need to be called."""
        try:
            summary = state.get("summary", "")
            system_message = query_analysis_prompt.format(summary=summary)
            prompt = [SystemMessage(system_message)] + state['messages']
            self.llm.bind_tools(self.tools_list)
            response = self.safe_llm_invoke(prompt)
            logger.info(f"React agent call successful")
            if len(response.content) > 0:
                logger.info(f"-"*50)
                logger.info(f"Response: {response.content}")
            return {"messages": [response],'acceptable_message_length': 5, "remove_tool_message": True}

        except Exception as e:
            logger.error(f"API call failed: {str(e)}")
            return {
                "messages": [AIMessage(content="I'm sorry, I'm having trouble responding right now. Please try again later.")]
            }


    def summarize_conversation(self, state: State):

        if len(state["messages"]) > state.get("acceptable_message_length",7):

            summary = state.get("summary", "")
            messages = []
            if summary:
                summary_message = (
                    f"This is a summary of the conversation to date: {summary}\n\n"
                    "Extend the summary by taking into account the content of the new messages above in paragraph form. Make sure all information is retained but token count for next messages is reduced."
                )
            else:
                summary_message = "Create a summary of the conversation above in paragraph form so that all information is retained but token count for next messages is reduced."

            for i in range(len(state["messages"])):
                if state["messages"][i].type != 'tool' and len(state["messages"][i].content) > 0:
                    new_message = {"role": state["messages"][i].type, "content": state["messages"][i].content}
                    messages.append(new_message)

            messages = messages + [{"role": "human", "content": summary_message}]
            try:
                response = self.safe_llm_invoke(messages)
                logger.info(f"Summarizer LLM call successful")
            except Exception as e:
                # Handle the case where all retries failed
                logger.error(f"All retries failed for: {str(e)}")
                return

            if state["remove_tool_message"]:
                delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-1]]
            else:
                delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2] if m.type!='tool' and not (m.type == 'ai' and m.tool_calls)]
            return {"summary": response.content, "messages": delete_messages, 'acceptable_message_length': 5}

    def tools(self,query: str) -> ToolNode:
        return ToolNode(self.tools_list)