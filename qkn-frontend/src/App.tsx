import { useEffect, useState } from 'react';
import axios from 'axios';
import { io } from 'socket.io-client';
import './styles.css';

interface Problem {
  id: number;
  question: string;
  method: 'quantum' | 'ai';
  result?: Record<string, number>;
  answer?: string;
  cid: string;
  timestamp: string;
}

function App() {
  const [q, setQ] = useState('');
  const [method, setMethod] = useState<'quantum' | 'ai'>('quantum');
  const [live, setLive] = useState<Problem[]>([]);
  const [history, setHistory] = useState<Problem[]>([]);

  // 1) Load history once
  useEffect(() => {
    axios.get<Problem[]>('http://localhost:8000/history')
      .then(res => setHistory(res.data))
      .catch(console.error);
  }, []);

  // 2) Connect to Socket.IO for live updates
  useEffect(() => {
    const socket = io('http://localhost:8000');
    socket.on('new_problem', (data: Problem) => {
      setLive(prev => [data, ...prev]);
    });
    return () => {
      socket.disconnect();
    };
  }, []);

  // 3) Submit form
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await axios.post<Problem>(
        'http://localhost:8000/solve',
        { question: q, method }
      );
      setLive(prev => [res.data, ...prev]);
      setQ('');
    } catch (err) {
      console.error(err);
      alert('Request failed; see console.');
    }
  };

  return (
    <div className="container">
      <h1>Quantum Knowledge Network</h1>

      <form onSubmit={handleSubmit} className="solve-form">
        <input
          value={q}
          onChange={e => setQ(e.target.value)}
          placeholder="Enter your question"
          required
        />
        <select
          value={method}
          onChange={e => setMethod(e.target.value as 'quantum' | 'ai')}
        >
          <option value="quantum">Quantum</option>
          <option value="ai">AI</option>
        </select>
        <button type="submit">Solve</button>
      </form>

      <section className="live-section">
        <h2>Live Updates</h2>
        <ul>
          {live.map(item => (
            <li key={item.id}>
              <strong>[{item.method.toUpperCase()}]</strong> {item.question} →
              {item.method === 'quantum'
                ? <pre>{JSON.stringify(item.result, null, 2)}</pre>
                : <p>{item.answer}</p>
              }
              <small>CID: {item.cid}</small>
            </li>
          ))}
        </ul>
      </section>

      <section className="history-section">
        <h2>History</h2>
        <ul>
          {history.map(item => (
            <li key={item.id}>
              <strong>[{item.method.toUpperCase()}]</strong> {item.question} →
              {item.method === 'quantum'
                ? <pre>{JSON.stringify(item.result, null, 2)}</pre>
                : <p>{item.answer}</p>
              }
              <small>
                {new Date(item.timestamp).toLocaleString()} | CID: {item.cid}
              </small>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}

export default App;
