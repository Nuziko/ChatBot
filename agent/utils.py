from langchain_groq import ChatGroq
from agent.prompts import MEDICAL_SYSTEM_PROMPT,BUILD_SUMMARY_PROMPT_TEMPLATE,EXTEND_SUMMARY_PROMPT_TEMPLATE
from dotenv import load_dotenv
import os
load_dotenv()  

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

def get_llm(model_name: str ,tools:list=None,**kwargs) -> ChatGroq:
    """
    Initialize and return a ChatGroq instance with the specified model name.
    """
    tags=kwargs.get("tags",[])
        
    llm = ChatGroq(model=model_name, **kwargs).with_config({'tags': tags})
    if tools:
        llm=llm.bind_tools(tools)
    return llm


def build_system_prompt(summary: str) -> str:
    """Inject the rolling summary into the system prompt if it exists."""
    if summary:
        summary_section = (
            f"\n\nCONVERSATION SUMMARY (context from earlier in this session):\n"
            f"{summary}"
        )
    else:
        summary_section = ""

    
    return MEDICAL_SYSTEM_PROMPT.format(summary_section=summary_section)

def build_summary_prompt(existing_summary: str, conversation: str) -> str:
    """Prompt for summarization. Inject current patient info and existing summary."""
    if existing_summary:
        prompt=EXTEND_SUMMARY_PROMPT_TEMPLATE.format(current_summary=existing_summary,conversation=conversation)
    else:
        prompt=BUILD_SUMMARY_PROMPT_TEMPLATE.format(conversation=conversation)

    return prompt

from groq import Groq

client = Groq()

def transcript(file_name: str, file_bytes: bytes) -> str:
    try: 
        transcription = client.audio.transcriptions.create(
        file=(file_name, file_bytes,),
        model="whisper-large-v3-turbo",
        temperature=0,
        response_format="verbose_json",
        )
        return transcription.text
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None

