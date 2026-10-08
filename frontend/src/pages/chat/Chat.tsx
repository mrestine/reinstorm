import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import ModelSelect from '../../components/ModelSelect';

function Chat() {
  const [response, setResponse] = useState<string>('awaiting message');
  const [message, setMessage] = useState<string>('');
  const [model, setModel] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  function handleInputChange(ev: React.ChangeEvent<HTMLInputElement>) {
    const newValue = ev.target.value;
    setMessage(newValue);
  }

  function sendMessage() {
    setLoading(true);
    setResponse('');
    fetch('http://localhost:8000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'Application/JSON' },
      body: JSON.stringify({ message, model }),
    }).then(async (res) => {
      const reader = res.body!.getReader();
      if (!res.ok || !reader) {
        alert('error');
        console.log(res);
      }
      const decoder = new TextDecoder();
      let buffer = '';

      setResponse('');
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() ?? '';

        for (const line of lines) {
          if (!line) continue;
          const event = JSON.parse(line);
          if (event.data) {
            setResponse((prev) => prev + event.data);
            // TODO: scroll to bottom
          } else if (event.done) {
            console.log('message finished', event);
            setMessage('');
            setLoading(false);
          } else if (event.error) {
            console.error(event);
            setMessage('');
            setResponse((prev) => prev + '- an error occurred.');
            setLoading(false);
          }
        }
      }
    });
  }

  function handleModelChange(newModel: string) {
    setModel(newModel);
  }

  return (
    <>
      <div className="chatWindow">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {response || 'awaiting response...'}
        </ReactMarkdown>
      </div>
      <input type="text" value={message} onChange={handleInputChange} disabled={loading} />
      <button onClick={sendMessage} disabled={!message || loading}>
        send
      </button>
      <ModelSelect onChange={handleModelChange} />
    </>
  );
}

export default Chat;
