from fastapi import FastAPI,Depends,UploadFile,File
from fastapi.responses import StreamingResponse
from agent.graph_builder import builder
import shutil
import tempfile

from server.type import ChatRequest,ChatResponse,HistoryResponse,TranscriptionResponse
from server.utils import get_answer,stream_app_output,transcript
from contextlib import asynccontextmanager
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from server.db import get_pool
import os 
from dotenv import load_dotenv

load_dotenv()




@asynccontextmanager
async def lifespan(app: FastAPI):
    db_uri = os.environ.get("DB_URI")
    async with AsyncPostgresSaver.from_conn_string(db_uri) as checkpointer:
        await checkpointer.setup()
        print("==> Setup the checkpointer")
    yield
    
   
    


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Welcome to the Medical Chatbot API. Use the /chat endpoint to interact with the chatbot."}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, pool=Depends(get_pool)):

    state = {"query": request.user_input}
    config = {"configurable": {"thread_id": request.thread_id}}

    try:
        async with pool.connection() as conn:  
            checkpointer = AsyncPostgresSaver(conn)

            graph_app = builder.compile(checkpointer=checkpointer)

            output, urls, safety = await get_answer(graph_app, state, config)

    except Exception as e:
        print(f"Error in /chat endpoint: {e}")
        return ChatResponse(success=False, error="Something went wrong while processing the request.")

    return ChatResponse(success=True, response=output, urls=urls, safety=safety)


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest, pool=Depends(get_pool)):

    state = {"query": request.user_input}
    config = {"configurable": {"thread_id": request.thread_id}}

    async def event_generator():
        async with pool.connection() as conn:
            checkpointer = AsyncPostgresSaver(conn)  

            graph_app = builder.compile(checkpointer=checkpointer)

            async for event in stream_app_output(graph_app, state, config):
                yield event

    return StreamingResponse(event_generator(), media_type="application/event-stream")

@app.get("/history", response_model=HistoryResponse)
async def get_history(thread_id: str ,pool = Depends(get_pool)):
    """Fetches full chat history  messages for a given thread."""
    config = {"configurable": {"thread_id": thread_id}}
    
    async with pool.connection() as conn:
        checkpointer = AsyncPostgresSaver(conn)
        checkpoint_tuple = await checkpointer.aget_tuple(config)
    
    if not checkpoint_tuple:
        return HistoryResponse(messages=[])
    
    messages = checkpoint_tuple.checkpoint.get("channel_values", {}).get("messages", [])
    formated_messages = [{"type": message.type, "content": message.content} 
                     for message in messages
                     if message.type in ['human', 'ai']
                     and message.content.strip() != ""]
    
        
    return HistoryResponse(messages=formated_messages)


@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(file: UploadFile = File(...)):
    # 1. Create a named temporary file
    # We use 'delete=True' so it vanishes once the block closes
    with tempfile.NamedTemporaryFile(delete=True, suffix=f"_{file.filename}") as temp_file:
        # 2. Efficiently stream the uploaded content into the temp file
        shutil.copyfileobj(file.file, temp_file)
        print(temp_file)
        
        # 3. Reset the temp file pointer to the beginning before reading
        temp_file.seek(0)
        
        # 4. Pass the actual file object to Groq
        transcription = transcript(temp_file, file.filename)

    if transcription is None:
        return TranscriptionResponse(error="Transcription failed.")
        
    return TranscriptionResponse(transcription=transcription)