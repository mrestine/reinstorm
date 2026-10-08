from ollama import Client
from ollama import ChatResponse

client = Client(host='http://localhost:11434', headers={})
response: ChatResponse = client.chat(
  model='qwen2.5:7b-instruct',
  messages=[{'role': 'user', 'content': 'ping' }],
  options={'temperature': 0, 'num_ctx': 4096 }
)

print(response.message.content)
print(f"prompt tokens: {response.prompt_eval_count}, "
    f"response tokens: {response.eval_count}, "
    f"load: {response.load_duration / 1e9:.2f}s, "
    f"gen: {response.eval_duration / 1e9:.2f}s")