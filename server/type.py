from pydantic import BaseModel
from typing import List, Optional,Literal


class ChatRequest(BaseModel):
    user_input: str
    thread_id: str 

class ChatResponse(BaseModel):
    success: bool
    response: Optional[str] = None
    error: Optional[str] = None
    urls: Optional[List[str]] = None
    safety: Literal['safe', 'unsafe'] = 'safe'

class Checkpoint(BaseModel):
    threads: int

class HistoryResponse(BaseModel):
    messages: List[dict]

class ThreadInfo(BaseModel):
    thread_id: str
    thread_name: str

class ThreadListResponse(BaseModel):
    threads: List[ThreadInfo]


class TranscriptionResponse(BaseModel):
    transcription: Optional[str] = None
    error: Optional[str] = None