import { useState, useRef, useEffect } from 'react';
import { sendMessage, clearChatHistory, getChatHistory } from '../api/client';
import { useAuth } from '../context/AuthContext';
import EmergencyBanner from '../components/EmergencyBanner';
import CrisisModal from '../components/CrisisModal';

export default function Chat() {
  const { user } = useAuth();
  const userId = user?.user_id || user?.id || 'demo-user';
  const [messages, setMessages] = useState([
    {
      role: 'ai',
      content: "Hi there! 👋 How are you feeling today? I'm here to listen and support you.",
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [distress, setDistress] = useState(false);
  const [therapistMode, setTherapistMode] = useState(true);
  const [isRecording, setIsRecording] = useState(false);
  const [crisisData, setCrisisData] = useState(null);
  const chatEndRef = useRef(null);
  const mediaRecorderRef = useRef(null);

  // Load past chat history from database on mount
  useEffect(() => {
    const loadHistory = async () => {
      try {
        const res = await getChatHistory(userId);
        const history = res.data?.history;
        if (history && history.length > 0) {
          const pastMessages = history.map((msg) => ({
            role: msg.role === 'user' ? 'user' : 'ai',
            content: msg.content,
            time: new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            sentiment: msg.sentiment ? { label: msg.sentiment } : undefined,
          }));
          setMessages(pastMessages);
        }
      } catch {
        // If history fetch fails, keep the default greeting
      } finally {
        setHistoryLoading(false);
      }
    };
    if (userId !== 'demo-user') {
      loadHistory();
    } else {
      setHistoryLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    const text = input.trim();
    if (!text || loading) return;

    const userMsg = {
      role: 'user',
      content: text,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await sendMessage(text, userId, therapistMode);
      const data = res.data;
      setDistress(data.distress_detected);
      if (data.crisis && data.crisis.show_helplines) {
        setCrisisData(data.crisis);
      }

      setMessages(prev => [...prev, {
        role: 'ai',
        content: data.reply,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        sentiment: data.sentiment,
        emotion: data.emotion,
        contextAware: data.context_aware,
      }]);
    } catch {
      setMessages(prev => [...prev, {
        role: 'ai',
        content: "I'm having trouble connecting. Please ensure the backend is running on port 8000.",
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleClear = async () => {
    try { await clearChatHistory(userId); } catch {}
    setMessages([{
      role: 'ai',
      content: "Chat cleared! 🔄 How are you feeling?",
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }]);
    setDistress(false);
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      mediaRecorderRef.current = recorder;
      const chunks = [];
      recorder.ondataavailable = e => chunks.push(e.data);
      recorder.onstop = async () => {
        stream.getTracks().forEach(t => t.stop());
        const blob = new Blob(chunks, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append('audio', blob, 'recording.webm');
        formData.append('user_id', userId);
        setLoading(true);
        try {
          const { transcribeVoice } = await import('../api/client');
          const res = await transcribeVoice(formData);
          if (res.data.transcription) {
            setMessages(prev => [...prev,
              { role: 'user', content: `🎙️ ${res.data.transcription}`, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) },
              { role: 'ai', content: res.data.reply || 'Received.', time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }), sentiment: res.data.sentiment },
            ]);
          }
        } catch { /* ignore */ }
        setLoading(false);
      };
      recorder.start();
      setIsRecording(true);
    } catch {
      alert('Microphone access denied.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const formatContent = (text) => {
    return text.split('\n').map((line, i) => {
      const html = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      return <p key={i} style={{ margin: '2px 0' }} dangerouslySetInnerHTML={{ __html: html }} />;
    });
  };

  return (
    <div>
      <div className="page-header">
        <span className="page-tag">💬 AI-Powered Therapy</span>
        <h1>AI Therapist</h1>
        <p>Smart, empathetic conversations powered by machine learning</p>
      </div>

      {distress && <EmergencyBanner onClose={() => setDistress(false)} />}
      <CrisisModal crisis={crisisData} onClose={() => setCrisisData(null)} />

      <div className="chat-container">
        {/* Header — WhatsApp style */}
        <div className="chat-header">
          <div className="chat-header-left">
            <div className="chat-avatar">🧠</div>
            <div className="chat-header-info">
              <h3>AI Mental Health Assistant</h3>
              <div className="chat-status">
                <span className="dot"></span>
                Online • Ready to listen
              </div>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div className="therapist-toggle">
              <label>Therapist</label>
              <input type="checkbox" className="toggle-switch" checked={therapistMode} onChange={e => setTherapistMode(e.target.checked)} />
            </div>
            <button className="btn btn-ghost btn-sm" onClick={handleClear} style={{ color: '#fff' }} title="Clear chat">🗑️</button>
          </div>
        </div>

        {/* Messages — WhatsApp style */}
        <div className="chat-messages">
          {historyLoading && (
            <div className="message message-ai" style={{ textAlign: 'center', opacity: 0.7 }}>
              <p>Loading chat history...</p>
            </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} className={`message message-${msg.role === 'user' ? 'user' : 'ai'}`}>
              {formatContent(msg.content)}
              <span className="msg-time">{msg.time}</span>
              {(msg.sentiment || msg.contextAware) && (
                <div className="msg-meta">
                  {msg.sentiment && (
                    <span className={`sentiment-tag ${msg.sentiment.label === 'POSITIVE' ? 'sentiment-positive' : 'sentiment-negative'}`}>
                      {msg.sentiment.label === 'POSITIVE' ? '😊' : '😔'} {msg.sentiment.label}
                    </span>
                  )}
                  {msg.contextAware && <span className="context-badge">🔗 Context</span>}
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className="message message-ai">
              <div className="typing-indicator">
                <span></span><span></span><span></span>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input — WhatsApp style */}
        <div className="chat-input-area">
          <button
            className={`btn btn-icon ${isRecording ? 'btn-danger' : ''}`}
            onClick={isRecording ? stopRecording : startRecording}
            style={!isRecording ? { background: 'transparent', color: 'var(--text-muted)', border: 'none' } : {}}
          >
            {isRecording ? '⏹️' : '🎙️'}
          </button>
          <input
            className="chat-input"
            type="text"
            placeholder="Type a message..."
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
          />
          <button
            className="btn btn-icon btn-primary"
            style={{ width: 40, height: 40 }}
            onClick={handleSend}
            disabled={loading || !input.trim()}
          >
            ➤
          </button>
        </div>
      </div>
    </div>
  );
}
