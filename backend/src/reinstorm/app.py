from fastapi import FastAPI
from pydantic import BaseModel
from ollama import Client
from ollama import ChatResponse
from fastapi.responses import StreamingResponse

client = Client(host='http://localhost:11434', headers={})
chatArgs = {
    'model': 'qwen2.5:7b-instruct',
    'options': {'temperature': 0, 'num_ctx': 4096 },
    'stream': True
}

app = FastAPI()

class ChatItem(BaseModel):
    message: str

@app.post("/chat")
async def inbound_message(chatItem: ChatItem):
    def generate_chunks():
        response = client.chat(
            **chatArgs,
            messages=[{'role': 'user', 'content': chatItem.message}],
        )
        for chunk in response:
            if chunk.done:
                yield f"done: True, eval_count: {chunk.eval_count}, eval_duration: {chunk.eval_duration}"
            else:
                yield f"data: {chunk.message.content}"

    return StreamingResponse(generate_chunks(), media_type="text/event-stream")
