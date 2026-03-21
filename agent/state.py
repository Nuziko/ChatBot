from langgraph.graph import MessagesState
from typing import Optional,Literal

class MedicalState(MessagesState):
    query :str=""
    summary :Optional[str] = None
    safety_status :Literal['safe','unsafe'] = 'safe'
    answer:str=""
    urls:list[str]=[]





