from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, RemoveMessage,ToolMessage
from agent.state import MedicalState
from agent.tools import TOOLS,search_web,get_patient_by_id,search_patient_by,NODE_TOOLS
from agent.utils import get_llm, build_system_prompt,build_summary_prompt
from agent.prompts import REFUSAL_MESSAGES,GUARD_SYSTEM_PROMPT
import json
from typing import Literal
from langgraph.prebuilt import ToolNode
from agent.constant import MESSAGES_TO_KEEP,HISTORY_MESSAGES_TO_KEEP


def guard_node(state: MedicalState) -> dict:
    
    """
    Safety gate powered by GPT-OSS Safeguard 20B.

    Flow:
      1. Send the user's latest message to the safeguard model
      2. Parse the JSON verdict (SAFE / UNSAFE + category + reason)
      3. If SAFE  → set safety_status = 'safe', pass through
      4. If UNSAFE → set safety_status = 'unsafe',
                     append category-specific refusal AIMessage,
                     graph routes to END immediately

    The safeguard model NEVER sees conversation history — only the
    latest user message. This keeps cost minimal and prevents the
    model being confused by prior context.
    """
    

   
    
    
    messages=state["messages"][-5:] if len(state['messages'])>5 else state["messages"]
    clean_messages =[m for m in messages if m.type in ['human', 'ai']]
    safeguard_messages = [SystemMessage(content=GUARD_SYSTEM_PROMPT)] + clean_messages + [HumanMessage(content=f"""Classify the message based on the provided context:\n\n#message :{state['query']}""")]

    response = get_llm(model_name="openai/gpt-oss-safeguard-20b", tools=[],tags=["safety"],temperature=0.0).invoke(safeguard_messages)
    try:
        data = json.loads(response.content)
        verdict = data.get("verdict")
        category = data.get("category", "none")
    except Exception as e:
        
        verdict ="SAFE"


    if verdict == "UNSAFE":
        refusal_text = REFUSAL_MESSAGES.get(category, REFUSAL_MESSAGES["default"])
        refusal_msg  = AIMessage(content=refusal_text)
        return {
            "safety_status": "unsafe",
            "answer": refusal_msg.content,
        }

    return {"safety_status": "safe",
            "messages": [HumanMessage(content=state["query"])]
            }


def brain_node(state: MedicalState) -> dict:
    
    """
    Core reasoning node. The LLM decides:
      - Answer directly from knowledge
      - Call a tool (patient lookup, web search)

    The rolling summary is injected into the system prompt so the model
    always has full context even after messages have been trimmed.
    """
    system_prompt = build_system_prompt(state.get("summary", ""))

    messages_list = state["messages"]
    if len(messages_list) > HISTORY_MESSAGES_TO_KEEP:
        recent_messages = messages_list[-HISTORY_MESSAGES_TO_KEEP:]
        while recent_messages and isinstance(recent_messages[0], ToolMessage):
            recent_messages.pop(0)
    else:
        recent_messages = messages_list
    messages = [SystemMessage(content=system_prompt)] + recent_messages

    response = get_llm(model_name="openai/gpt-oss-120b", tools=TOOLS,temperature=0.2).invoke(messages)

    
    return {"messages": [response]}






def summarize_node(state: MedicalState) -> dict:
    
    """
    1. Takes all messages OLDER than the last 20
    2. Summarizes them (extending any existing summary)
    3. Removes those old messages from state via RemoveMessage
    4. Updates the 'summary' key in state

    The summary is then injected into the next agent call's system prompt,
    so no clinical context is ever truly lost.
    """
    messages = state["messages"]
    existing_summary = state.get("summary", "")

    
    messages_to_summarize = messages[-MESSAGES_TO_KEEP:-HISTORY_MESSAGES_TO_KEEP]  # Keep the most recent HISTORY_MESSAGES_TO_KEEP messages in full to preserve context for the summary

    past_conversation = "\n".join(
        f"{m.__class__.__name__}: {m.content}"
        for m in messages_to_summarize
        if hasattr(m, 'content') and m.content
        and not isinstance(m, RemoveMessage)
        and not isinstance(m, ToolMessage)
        and not (isinstance(m, AIMessage) and m.content.strip() == "")
    )

    prompt = build_summary_prompt(existing_summary, past_conversation)

    
    

    summary_response = get_llm(model_name="llama-3.1-8b-instant", tools=[],temperature=0.0,max_tokens=2048).invoke(
        [SystemMessage(content=prompt)]
    )
    new_summary = summary_response.content

    return {
        "summary": new_summary
    }




def web_search_node(state: MedicalState):
  

  last_message = state["messages"][-1]
  tool_call = last_message.tool_calls[0]

  result = search_web.invoke(tool_call['args'])
  urls = [res["url"] for res in result.get("results",[])]
  result=json.dumps(result)
  return {"messages": [ToolMessage(content=result,tool_call_id=tool_call['id'])], "urls": urls}


def patient_lookup_node(state: MedicalState):
    
    tool_func={
        "get_patient_by_id":get_patient_by_id,
        "search_patient_by":search_patient_by
    }
    
    last_message = state["messages"][-1]
    tool_call = last_message.tool_calls[0]
    patient_info = (tool_func.get(tool_call['name'])).invoke(tool_call['args'])

 
    return {
        "messages": [ToolMessage(content=patient_info,tool_call_id=tool_call['id'])],
      }

tool_node=ToolNode(tools=NODE_TOOLS)

def route_after_guard(state: MedicalState) -> Literal["to brain", "final_answer"]:
    """
    After the guard node:
    - If safety_status is 'unsafe' → final_answer
    - Otherwise → proceed to brain node
    """
    if state.get("safety_status") == "unsafe":
        
        return "block"
    
    return "safe"


def route_after_brain(state: MedicalState) :
    
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        tool_call_name = last_message.tool_calls[0]['name']
        if tool_call_name == "search_web":
            
            return "additional web info"
        elif tool_call_name in ["get_patient_by_id",'search_patient_by']:
            
            return "patients info"
        
        elif tool_call_name == "get_current_date_time" :
            
            return "auxiliary info"
    
    return "pass to summarize"



def route_to_summarize_or_end(state: MedicalState) -> Literal["summarize", "pass to final answer"]:
    
    """
    After the agent produces a final answer:
    - If conversation has more than MESSAGES_TO_KEEP messages → summarize
    - Otherwise → end normally

    We only summarize AFTER a complete agent turn (not mid-tool-call)
    to avoid interrupting the reasoning loop.
    """
    if len(state["messages"]) > MESSAGES_TO_KEEP:
        
        return "summerize conversation"
    return "pass to final answer"



def answer_node(state: MedicalState) -> dict:
    """
    Final answer node. Could be used to format the final response, add
    disclaimers, or perform any last steps before sending the answer to the user.
    """
    if  state.get("safety_status") == "unsafe":
        return state
    last_message = state["messages"][-1]
    return {"answer": last_message.content}