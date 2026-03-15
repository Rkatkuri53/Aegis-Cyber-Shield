'use client'

import { useState, useEffect } from 'react'

export default function Home() {
  const [status, setStatus] = useState('Shield Active')
  const [analysisResult, setAnalysisResult] = useState(null)
  const [apiKey, setApiKey] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [logs, setLogs] = useState([
    { time: '09:42:12', msg: 'Aegis System Online', type: 'system' }
  ])
  const [isLive, setIsLive] = useState(false)

  useEffect(() => {
    // Connect to Multimodal Live WebSocket
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const wsUrl = apiUrl.replace('http', 'ws') + '/ws/live'
    const ws = new WebSocket(wsUrl)
    
    ws.onopen = () => {
      setIsLive(true)
      addLog('Live Multimodal Stream Connected', 'success')
    }
    ws.onmessage = (e) => {
      // Periodic heartbeat/analysis from Gemini Live
      const data = JSON.parse(e.data)
      if (data.alert) addLog(`ALERT: ${data.alert}`, 'danger')
    }
    ws.onclose = () => setIsLive(false)
    return () => ws.close()
  }, [])

  const addLog = (msg, type = 'info') => {
    const time = new Date().toLocaleTimeString([], { hour12: false })
    setLogs(prev => [{ time, msg, type }, ...prev].slice(0, 10))
  }

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    setIsAnalyzing(true)
    addLog(`Analyzing visual data: ${file.name}`, 'scan')
    
    const formData = new FormData()
    formData.append('file', file)

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    
    try {
      const res = await fetch(`${apiUrl}/analyze`, {
        method: 'POST',
        body: formData
      })
      const data = await res.json()
      setAnalysisResult(data)
      
      if (data.threat_detected) {
          addLog(`THREAT DETECTED: ${data.threat_type}`, 'danger')
      } else {
          addLog('Analysis Complete: No threats found.', 'success')
      }
    } catch (err) {
      addLog('Error: Verification Server Unreachable', 'danger')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleNeutralize = async () => {
    if (!analysisResult) return
    setIsAnalyzing(true)
    addLog(`Deploying Shield: ${analysisResult.recommended_action}`, 'danger')
    
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    try {
      const res = await fetch(`${apiUrl}/neutralize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          threat_type: analysisResult.threat_type,
          details: { recommended_action: analysisResult.recommended_action }
        })
      })
      const data = await res.json()
      
      if (data.status === 'Morphic Deception Active') {
          addLog(`DECEPTION LAYER ENABLED: Attacker Trapped`, 'success')
      } else if (data.status === 'Aegis Shield Hardened') {
          addLog(`HIJACK BLOCKED: Validation Failed`, 'danger')
      } else {
          addLog(`SUCCESS: ${data.status}`, 'success')
      }
      
      addLog(`STATUS: ${data.action}`, 'system')
    } catch (err) {
      addLog('Error: Command Execution Failed', 'danger')
    } finally {
      setIsAnalyzing(false)
    }
  }

  return (
    <div className="dashboard-container">
      <header>
        <div className="logo">AEGIS // SHIELD</div>
        <div style={{display: 'flex', gap: '20px', alignItems: 'center'}}>
            <input 
                type="password" 
                placeholder="GEMINI_API_KEY" 
                className="card" 
                style={{margin: 0, padding: '8px 15px', width: '200px', fontSize: '11px'}}
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
            />
            <div className="system-status">
            <span className="status-indicator" style={{
                background: isLive ? '#39ff14' : (isAnalyzing ? 'yellow' : '#333'),
                boxShadow: isLive ? '0 0 10px #39ff14' : 'none'
            }}></span>
            {isLive ? 'LIVE SENSING' : (isAnalyzing ? 'ANALYZING...' : 'DISCONNECTED')}
            </div>
        </div>
      </header>

      <div className="side-panel">
        <h2>Shield Integrity</h2>
        <div className="card">
          <p style={{fontSize: '12px', color: '#a0a0a0'}}>Visual Sensitivity</p>
          <div style={{height: '4px', background: '#333', marginTop: '10px', borderRadius: '2px'}}>
            <div style={{width: '85%', height: '100%', background: 'var(--accent-color)'}}></div>
          </div>
        </div>
        <div className="card">
          <p style={{fontSize: '12px', color: '#a0a0a0'}}>Detection Confidence</p>
          <p style={{fontSize: '24px', fontWeight: 'bold'}}>
            {analysisResult ? `${(analysisResult.confidence * 100).toFixed(0)}%` : '0%'}
          </p>
        </div>
        
        <div className="card" style={{border: '1px dashed var(--accent-color)', cursor: 'pointer', textAlign: 'center'}}>
            <input type="file" id="dashboard-upload" hidden onChange={handleFileUpload} />
            <label htmlFor="dashboard-upload" style={{cursor: 'pointer', fontSize: '12px', display: 'block', padding: '10px'}}>
                DROP DASHBOARD SCREENSHOT
            </label>
        </div>
      </div>

      <div className="main-view">
        {analysisResult && analysisResult.threat_detected ? (
            <div style={{padding: '40px', background: 'rgba(255, 62, 62, 0.1)', height: '100%'}}>
               <h1 style={{color: 'var(--danger-color)', marginBottom: '10px'}}>⚠️ ATTACK VECTOR IDENTIFIED</h1>
               <h3 style={{marginBottom: '20px'}}>{analysisResult.threat_type}</h3>
               <div className="card" style={{background: 'rgba(0,0,0,0.3)'}}>
                  <p style={{marginBottom: '10px'}}>{analysisResult.description}</p>
                  <p style={{color: 'var(--accent-color)', fontWeight: 'bold'}}>AGI ACTION RECOMMENDED:</p>
                  <code style={{display: 'block', padding: '10px', background: '#000', borderRadius: '4px', marginTop: '10px'}}>
                      {analysisResult.recommended_action}
                  </code>
               </div>
               <button className="card" onClick={handleNeutralize} style={{
                   width: '100%', 
                   background: 'var(--danger-color)', 
                   color: 'white', 
                   fontWeight: 'bold', 
                   marginTop: '20px',
                   cursor: 'pointer'
               }}>
                   {isAnalyzing ? 'DEPLOYING...' : 'EXECUTE NEUTRALIZATION PROTOCOL'}
               </button>
            </div>
        ) : (
            <div style={{padding: '40px', textAlign: 'center', opacity: isAnalyzing ? 1 : 0.5}}>
                <div style={{fontSize: '80px', marginBottom: '20px', animation: isAnalyzing ? 'pulse 2s infinite' : 'none'}}>
                    {isAnalyzing ? '🛰️' : '🛡️'}
                </div>
                <h3>{isAnalyzing ? 'Deep Visual Inspection in Progress...' : 'Sensing Live SOC Dashboard...'}</h3>
                <p>Gemini 1.5 Pro is standing by to analyze visual traffic patterns.</p>
            </div>
        )}
        
        <div style={{
          position: 'absolute',
          bottom: '20px',
          left: '20px',
          right: '20px',
          height: '150px',
          background: 'linear-gradient(transparent, rgba(0, 242, 255, 0.1))',
          borderTop: '1px solid rgba(0, 242, 255, 0.2)',
          padding: '20px'
        }}>
          <h2>Threat Vector Analysis</h2>
          <div style={{display: 'flex', gap: '5px', alignItems: 'flex-end', height: '60px'}}>
             {[...Array(30)].map((_, i) => (
               <div key={i} style={{
                 flex: 1, 
                 height: `${Math.random() * 100}%`, 
                 background: analysisResult?.threat_detected ? 'var(--danger-color)' : 'var(--accent-color)',
                 opacity: 0.3 + (Math.random() * 0.7)
                }}></div>
             ))}
          </div>
        </div>
      </div>

      <div className="side-panel">
        <h2>Shield Event Log</h2>
        {logs.map((log, i) => (
            <div key={i} className="card" style={{borderColor: log.type === 'danger' ? 'var(--danger-color)' : 'var(--glass-border)'}}>
                <p style={{fontSize: '11px', color: log.type === 'danger' ? 'var(--danger-color)' : (log.type === 'success' ? '#39ff14' : 'var(--text-dim)')}}>
                    {log.time} - {log.type.toUpperCase()}
                </p>
                <p style={{fontSize: '12px'}}>{log.msg}</p>
            </div>
        ))}
      </div>
      
      <style jsx global>{`
        @keyframes pulse {
            0% { transform: scale(1); opacity: 0.5; }
            50% { transform: scale(1.1); opacity: 1; }
            100% { transform: scale(1); opacity: 0.5; }
        }
      `}</style>
    </div>
  )
}
