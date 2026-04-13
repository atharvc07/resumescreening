import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Upload, FileText, CheckCircle, XCircle, Loader2, Sparkles, ArrowRight } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE = 'http://localhost:8000';

function App() {
  const [file, setFile] = useState(null);
  const [jd, setJd] = useState('');
  const [loading, setLoading] = useState(false);
  const [evalId, setEvalId] = useState(null);
  const [status, setStatus] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let interval;
    if (evalId && status !== 'completed' && status !== 'failed') {
      interval = setInterval(async () => {
        try {
          const res = await axios.get(`${API_BASE}/evaluations/${evalId}`);
          setStatus(res.data.status);
          if (res.data.status === 'completed') {
            setResult(res.data.result);
            setLoading(false);
            clearInterval(interval);
          } else if (res.data.status === 'failed') {
            setError(res.data.error_message || 'Evaluation failed');
            setLoading(false);
            clearInterval(interval);
          }
        } catch (err) {
          console.error('Polling error:', err);
        }
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [evalId, status]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file || !jd) return;

    setLoading(true);
    setError(null);
    setResult(null);
    setStatus('pending');

    const formData = new FormData();
    formData.append('resume', file);
    formData.append('job_description', jd);

    try {
      const res = await axios.post(`${API_BASE}/evaluations`, formData);
      setEvalId(res.data.evaluation_id);
      setStatus(res.data.status);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to submit resume');
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <motion.header 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1>AI Resume Screener</h1>
        <p className="subtitle">Evaluate candidates instantly using state-of-the-art AI</p>
      </motion.header>

      <main className="glass-card">
        <div className="grid-layout">
          {/* Step 1: Upload */}
          <div className="input-group">
            <label>1. Upload Resume (PDF)</label>
            <div 
              className={`upload-zone ${file ? 'active' : ''}`}
              onClick={() => document.getElementById('fileInput').click()}
            >
              <input 
                id="fileInput"
                type="file" 
                accept=".pdf" 
                hidden 
                onChange={(e) => setFile(e.target.files[0])}
              />
              {file ? (
                <div style={{ textAlign: 'center' }}>
                  <FileText size={48} color="#6366f1" style={{ marginBottom: '1rem' }} />
                  <p style={{ fontWeight: 600 }}>{file.name}</p>
                  <p className="subtitle" style={{ fontSize: '0.8rem' }}>Click to change</p>
                </div>
              ) : (
                <>
                  <Upload size={48} color="#94a3b8" style={{ marginBottom: '1rem' }} />
                  <p style={{ fontWeight: 600 }}>Drop your PDF here</p>
                  <p className="subtitle">or click to browse</p>
                </>
              )}
            </div>
          </div>

          {/* Step 2: Job Description */}
          <div className="input-group">
            <label>2. Job Description</label>
            <textarea 
              placeholder="Paste the job requirements here..."
              value={jd}
              onChange={(e) => setJd(e.target.value)}
            />
          </div>
        </div>

        <button 
          className="btn-primary" 
          onClick={handleSubmit}
          disabled={loading || !file || !jd}
        >
          {loading ? (
            <>
              <Loader2 className="animate-spin" />
              {status === 'processing' ? 'AI is analyzing...' : 'Submitting...'}
            </>
          ) : (
            <>
              Run Evaluation <Sparkles size={18} />
            </>
          )}
        </button>

        {error && (
          <div className="status-card" style={{ color: '#ef4444', background: 'rgba(239, 68, 68, 0.1)' }}>
            <XCircle /> {error}
          </div>
        )}

        <AnimatePresence>
          {result && (
            <motion.div 
              className="results-section"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem' }}>
                <div>
                  <h2 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>Evaluation Summary</h2>
                  <span className={`verdict-tag verdict-${result.verdict}`}>
                    {result.verdict.replace('_', ' ')}
                  </span>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <p className="subtitle" style={{ fontSize: '0.8rem', textTransform: 'uppercase' }}>Match Score</p>
                  <div className="score-badge">{result.score}%</div>
                </div>
              </div>

              <div className="grid-layout">
                <div>
                  <label>Justification</label>
                  <p className="justification">{result.justification}</p>
                </div>
                <div>
                  <label>Missing Requirements</label>
                  <ul className="requirements-list">
                    {result.missing_requirements.map((req, i) => (
                      <li key={i}><XCircle size={14} color="#ef4444" /> {req}</li>
                    ))}
                    {result.missing_requirements.length === 0 && (
                      <li><CheckCircle size={14} color="#10b981" /> No missing requirements found</li>
                    )}
                  </ul>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      <footer style={{ marginTop: '4rem', textAlign: 'center', paddingBottom: '2rem' }}>
        <p className="subtitle" style={{ fontSize: '0.8rem' }}>
          Powered by Advanced LLM Screening • Secure & Confidential
        </p>
      </footer>
    </div>
  );
}

export default App;
