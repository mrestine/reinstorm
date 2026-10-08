import json
from fastapi import FastAPI
from pydantic import BaseModel
from ollama import Client
from ollama import ChatResponse
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

OLLAMA_HOST = 'http://localhost:11434'
DEFAULT_MODEL = 'qwen2.5:7b-instruct'
client = Client(host=OLLAMA_HOST, headers={})
chatArgs = {
    'options': {'temperature': 0, 'num_ctx': 4096 },
    'stream': True
}

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

class ChatItem(BaseModel):
    message: str
    model: str

@app.get('/models')
async def get_models():
    return client.list()

@app.post("/chat")
async def inbound_message(chatItem: ChatItem):
    def generate_chunks():
        try:
            response = client.chat(
                **chatArgs,
                model=chatItem.model or DEFAULT_MODEL,
                messages=[{'role': 'user', 'content': chatItem.message}],
            )
            for chunk in response:
                if chunk.message.content:
                    yield json.dumps({'data': chunk.message.content}) + '\n'
                if chunk.done:
                    yield json.dumps({'done': True, 'eval_count': chunk.eval_count, 'eval_duration': chunk.eval_duration}) + '\n'
        except Exception as e:
            yield json.dumps({"error": str(e)}) + '\n'

    return StreamingResponse(generate_chunks(), media_type="application/x-ndjson")
