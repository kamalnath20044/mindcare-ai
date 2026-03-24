import { useState, useRef, useCallback } from 'react';
import { detectEmotion } from '../api/client';
import { useAuth } from '../context/AuthContext';

const EMOJIS = { Happy: '😊', Sad: '😢', Angry: '😠', Fear: '😨', Surprise: '😲', Disgust: '🤢', Neutral: '😐' };

export default function EmotionDetection() {
  const { user } = useAuth();
  const userId = user?.user_id || user?.id || 'demo-user';
  const [cameraOn, setCameraOn] = useState(false);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [history, setHistory] = useState([]);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480, facingMode: 'user' } });
      streamRef.current = stream;
      if (videoRef.current) videoRef.current.srcObject = stream;
      setCameraOn(true);
      setError('');
    } catch {
      setError('Camera access denied.');
    }
  };

  const stopCamera = () => {
    if (streamRef.current) streamRef.current.getTracks().forEach(t => t.stop());
    setCameraOn(false);
    setResult(null);
  };

  const capture = useCallback(async () => {
    if (!videoRef.current || !canvasRef.current) return;
    setLoading(true);
    setError('');
    const v = videoRef.current, c = canvasRef.current;
    c.width = v.videoWidth; c.height = v.videoHeight;
    c.getContext('2d').drawImage(v, 0, 0);
    const b64 = c.toDataURL('image/jpeg', 0.8);
    try {
      const res = await detectEmotion(b64, userId);
      if (res.data.error) { setError(res.data.error); setResult(null); }
      else {
        setResult(res.data);
        setHistory(prev => [{ emotion: res.data.emotion, confidence: res.data.confidence, time: new Date().toLocaleTimeString() }, ...prev.slice(0, 9)]);
      }
    } catch {
      setError('Backend not reachable.');
    }
    setLoading(false);
  }, [userId]);

  const pipeline = ['📷 Webcam', '🖼️ Capture', '📡 API', '👤 OpenCV', '🧠 TensorFlow', '✅ Result'];

  return (
    <div>
      <div className="page-header">
        <span className="page-tag">😊 Computer Vision</span>
        <h1>Facial Emotion Detection</h1>
        <p>Real-time analysis using OpenCV + TensorFlow CNN</p>
      </div>

      <div className="processing-pipeline" style={{ marginBottom: 20 }}>
        {pipeline.map((s, i) => (
          <span key={i} style={{ display: 'contents' }}>
            <span className="pipeline-step">{s}</span>
            {i < pipeline.length - 1 && <span className="pipeline-arrow">→</span>}
          </span>
        ))}
      </div>

      <div className="grid-2">
        <div>
          <div className="webcam-container">
            {cameraOn ? <video ref={videoRef} autoPlay playsInline muted /> : (
              <div className="webcam-placeholder">
                <span className="camera-icon">📷</span>
                <p>Camera is off</p>
              </div>
            )}
          </div>
          <canvas ref={canvasRef} style={{ display: 'none' }} />
          <div style={{ display: 'flex', gap: 10, marginTop: 14 }}>
            {!cameraOn ? (
              <button className="btn btn-primary btn-lg" style={{ flex: 1 }} onClick={startCamera}>📷 Start Camera</button>
            ) : (
              <>
                <button className="btn btn-primary btn-lg" style={{ flex: 1 }} onClick={capture} disabled={loading}>
                  {loading ? '⏳ Analyzing...' : '🔍 Capture & Detect'}
                </button>
                <button className="btn btn-danger" onClick={stopCamera}>⏹️ Stop</button>
              </>
            )}
          </div>
          {error && <div className="alert-banner alert-high" style={{ marginTop: 14 }}><span className="alert-icon">⚠️</span><div className="alert-content"><p>{error}</p></div></div>}
          <div className="card" style={{ marginTop: 14, padding: 14 }}>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>🔒 Frames are processed server-side and deleted immediately.</p>
          </div>
        </div>

        <div>
          {result ? (
            <div className="emotion-result" style={{ marginBottom: 18 }}>
              <div className="emotion-emoji">{EMOJIS[result.emotion] || '😐'}</div>
              <div className="emotion-label">{result.emotion}</div>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: 4 }}>Confidence: {(result.confidence * 100).toFixed(1)}%</p>
              <div className="confidence-bar"><div className="confidence-fill" style={{ width: `${result.confidence * 100}%` }} /></div>
              {result.suggestion && <p style={{ marginTop: 14, fontSize: '0.85rem', color: 'var(--text-secondary)' }}>💡 {result.suggestion}</p>}
            </div>
          ) : (
            <div className="card" style={{ textAlign: 'center', padding: 40 }}>
              <div style={{ fontSize: '3rem', opacity: 0.3, marginBottom: 10 }}>🎭</div>
              <p style={{ color: 'var(--text-muted)' }}>Start camera and capture to detect emotions</p>
            </div>
          )}
          {history.length > 0 && (
            <div className="card">
              <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 12 }}>Detection History</h3>
              {history.map((h, i) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: i < history.length - 1 ? '1px solid var(--border-light)' : 'none' }}>
                  <span>{EMOJIS[h.emotion]} {h.emotion}</span>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{(h.confidence * 100).toFixed(1)}% • {h.time}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
