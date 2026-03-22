import json
from groq import Groq
from dotenv import load_dotenv
load_dotenv()



async def stream_app_output(app,input,config):
    try:
        async for output in app.astream(input,config=config):
            if output.get('web search'):
                result = json.loads(output['web search']['messages'][-1].content)
                query = result.get('query')
                urls = [res['url'] for res in result.get('results',[])]
                yield f"{json.dumps({'step':'web search','query':query,'urls':urls})}\n"
            if output.get("patient lookup"):
                yield f"{json.dumps({'step':'patient lookup'})}\n"
            if output.get('helper tools'):
                yield f"{json.dumps({'step':'helper tools'})}\n"
            if output.get('guard'):
                yield f"{json.dumps({'step':'safety check','safety status':output['guard']['safety_status']})}\n"
            if output.get('final answer'):
                yield f"{json.dumps({'step':'answer written','answer':output['final answer']['answer']})}\n"
    except Exception as e:
        print(e)
        yield f"{json.dumps({'error':'Some things went worng'})}\n"

async def get_answer(app,input,config):
    output=await app.ainvoke(input,config=config)
    return output.get('answer',""),output.get('urls',[]),output.get("safety_status","safe")




client = Groq()

def transcript(temp_file, original_name: str) -> str:
    try: 
        transcription = client.audio.transcriptions.create(
            
            file=(original_name, temp_file), 
            model="whisper-large-v3-turbo",
            temperature=0,
            response_format="verbose_json",
        )
        return transcription.text
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None

    
