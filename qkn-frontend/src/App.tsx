import { useEffect, useState } from 'react'
import axios from 'axios'
import { io } from 'socket.io-client'

interface Problem {
  id: number
  question: string
  method: 'quantum' | 'ai'
  answer?: string
  result?: Record<string, number>
  cid: string
  timestamp: string
}

function App() {
  const [q, setQ] = useState('')
  const [method, setMethod] = useState<'quantum' | 'ai'>('quantum')
  const [live, setLive] = useState<Problem[]>([])
  const [history, setHistory] = useState<Problem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Fetch history on mount
  useEffect(() => {
    axios
      .get<Problem[]>('http://localhost:8000/history')
      .then((res) => setHistory(res.data))
      .catch((err) => {
        console.error(err)
        setError('Failed to load history')
      })
  }, [])

  // WebSocket live updates
  useEffect(() => {
    const socket = io('http://localhost:8000')
    socket.on('new_problem', (data: Problem) => {
      setLive((prev) => [data, ...prev])
    })
    socket.on('connect_error', (err) => {
      console.error('Socket error', err)
      setError('Live updates disconnected')
    })
    return () => {
      socket.disconnect()
    }
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      const res = await axios.post<Problem>('http://localhost:8000/solve', {
        question: q,
        method,
      })
      setLive((prev) => [res.data, ...prev])
      setQ('')
    } catch (err: any) {
      console.error(err)
      setError(
        err.response?.data?.error || 'An unexpected error occurred. Please try again.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-bl from-indigo-50 via-white to-indigo-100 p-6 flex items-center justify-center">
      <div className="max-w-3xl w-full space-y-8">
        
        <h1 className="text-4xl lg:text-5xl font-extrabold text-indigo-800 text-center drop-shadow-[0_2px_4px_rgba(0,0,0,0.2)]">
          Quantum Knowledge Network
        </h1>

        {/* Optional glass form */}
        <form
          onSubmit={handleSubmit}
          className="bg-white/50 backdrop-blur-lg rounded-2xl p-6 flex gap-4 items-center shadow-lg"
        >
          <input
            type="text"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Enter your question…"
            required
            className="flex-1 border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-400"
          />

          <select
            value={method}
            onChange={(e) => setMethod(e.target.value as any)}
            className="border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-400"
          >
            <option value="quantum">Quantum</option>
            <option value="ai">AI</option>
          </select>

          <button
            type="submit"
            disabled={loading}
            className={`
              relative bg-indigo-600 text-white px-6 py-3 rounded-full font-semibold overflow-hidden transition
              ${loading 
                ? 'opacity-60 cursor-not-allowed' 
                : 'hover:brightness-110 active:translate-y-1 active:shadow-inner'
              }
            `}
          >
            {loading
              ? <svg className="w-5 h-5 animate-spin mx-auto" /* … */ />
              : 'Solve'
            }
          </button>
        </form>

        {error && (
          <div className="bg-red-100 text-red-800 px-4 py-2 rounded-lg mb-4 flex justify-between items-center">
            <span>{error}</span>
            <button onClick={() => setError(null)} className="font-bold">✕</button>
          </div>
        )}

        <section className="space-y-6">
          <h2 className="text-2xl font-semibold text-gray-800">Live Updates</h2>
          <ul className="space-y-4">
            {live.length === 0 && <p className="text-gray-500">No live updates yet.</p>}
            {live.map((item) => (
              <li
                key={item.id}
                className="
                  bg-white rounded-xl shadow-2xl p-6 transform transition-transform 
                  hover:scale-[1.02] hover:shadow-[0_20px_40px_rgba(0,0,0,0.1)]
                "
              >
                <div className="flex justify-between items-center">
                  <span className="font-mono text-indigo-600">[{item.method.toUpperCase()}]</span>
                  <small className="text-gray-500 text-xs">{new Date(item.timestamp).toLocaleTimeString()}</small>
                </div>
                <p className="mt-2 text-gray-700">{item.question}</p>
                {item.method==='quantum' ? (
                  <pre className="bg-gray-100 rounded-lg p-4 mt-2 overflow-x-auto text-sm">
                    {JSON.stringify(item.result, null, 2)}
                  </pre>
                ) : (
                  <p className="mt-2 text-gray-600">{item.answer}</p>
                )}
                <p className="mt-2 text-xs text-gray-400">CID: {item.cid}</p>
              </li>
            ))}
          </ul>
        </section>

        <section className="space-y-6">
          <h2 className="text-2xl font-semibold text-gray-800">History</h2>
          <ul className="space-y-4">
            {history.length===0 && <p className="text-gray-500">No history records.</p>}
            {history.map((item) => (
              <li
                key={item.id}
                className="
                  bg-white rounded-xl shadow-lg p-6
                "
              >
                <div className="flex justify-between items-center">
                  <span className="font-mono text-indigo-600">[{item.method.toUpperCase()}]</span>
                  <small className="text-gray-500 text-xs">{new Date(item.timestamp).toLocaleString()}</small>
                </div>
                <p className="mt-2 text-gray-700">{item.question}</p>
                {item.method==='quantum' ? (
                  <pre className="bg-gray-100 rounded-lg p-4 mt-2 overflow-x-auto text-sm">
                    {JSON.stringify(item.result, null, 2)}
                  </pre>
                ) : (
                  <p className="mt-2 text-gray-600">{item.answer}</p>
                )}
                <p className="mt-2 text-xs text-gray-400">CID: {item.cid}</p>
              </li>
            ))}
          </ul>
        </section>

      </div>
    </div>
  );
}

export default App
