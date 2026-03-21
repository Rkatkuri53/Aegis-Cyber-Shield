'use client'

import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Shield, 
  Terminal, 
  Activity, 
  Lock, 
  ChevronRight, 
  ExternalLink, 
  AlertTriangle, 
  Zap, 
  Cpu, 
  Wifi, 
  ArrowRight,
  Volume2,
  VolumeX,
  RefreshCw,
  Mic,
  MicOff,
  Search,
  Database
} from 'lucide-react';
import AudioPlayer from './AudioPlayer';
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

const NeuralPulse = ({ active }: { active: boolean }) => {
  return (
    <div className="flex items-center gap-3">
      <div className="relative flex items-center justify-center w-12 h-6">
        <svg width="48" height="24" viewBox="0 0 48 24" className={cn("transition-colors duration-500", active ? "text-aegis-mint" : "text-gray-600")}>
          <motion.path
            d="M0 12 H10 L14 4 L18 20 L22 12 H48"
            fill="transparent"
            stroke="currentColor"
            strokeWidth="2"
            animate={active ? {
              pathLength: [0, 1],
              pathOffset: [0, 1],
            } : {}}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              ease: "linear",
            }}
          />
        </svg>
      </div>
      <span className={cn("text-[10px] font-bold tracking-widest uppercase transition-colors", active ? "text-aegis-mint" : "text-gray-600")}>
        {active ? "Neural Link: Active" : "Neural Link: Flatline"}
      </span>
    </div>
  )
}

const ConfidenceGauge = ({ value }: { value: number }) => {
  const radius = 30
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (value / 100) * circumference

  return (
    <div className="relative flex items-center justify-center w-24 h-24">
      <svg className="transform -rotate-90 w-24 h-24">
        <circle
          cx="48"
          cy="48"
          r={radius}
          stroke="currentColor"
          strokeWidth="6"
          fill="transparent"
          className="text-white/5"
        />
        <motion.circle
          cx="48"
          cy="48"
          r={radius}
          stroke="currentColor"
          strokeWidth="6"
          fill="transparent"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1, ease: "easeOut" }}
          className={cn(
            value > 80 ? "text-aegis-red" : value > 50 ? "text-aegis-amber" : "text-aegis-mint"
          )}
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="text-xl font-bold">{value}%</span>
        <span className="text-[8px] uppercase tracking-tighter opacity-50">Confidence</span>
      </div>
    </div>
  )
}

const EntropyHeatmap = ({ entropy }: { entropy: number }) => {
  return (
    <div className="grid grid-cols-10 gap-1 mt-2">
      {[...Array(30)].map((_, i) => (
        <motion.div
          key={i}
          animate={{
            backgroundColor: i / 30 < entropy ? (entropy > 0.8 ? '#FF3D00' : '#FFB800') : '#1F2937',
            opacity: i / 30 < entropy ? [0.4, 1, 0.4] : 0.2,
          }}
          transition={{ duration: 1, repeat: Infinity, delay: i * 0.02 }}
          className="w-full h-4 rounded-sm"
        />
      ))}
    </div>
  )
}

export default function Dashboard() {
  const [isLive, setIsLive] = useState(false)
  const [logs, setLogs] = useState<any[]>([])
  const [analysis, setAnalysis] = useState<any>(null)
  const [entropy, setEntropy] = useState(0.4211)
  const [isHydrating, setIsHydrating] = useState(false)
  const [isListening, setIsListening] = useState(true)
  const [swarmMode, setSwarmMode] = useState(false)
  const [swarmCount, setSwarmCount] = useState(0)
  const [isMirage, setIsMirage] = useState(false)
  const [isMuted, setIsMuted] = useState(false);
  const [currentAudio, setCurrentAudio] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  const scrollRef = useRef<HTMLDivElement>(null)
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "https://aegis-server-314798214199.us-central1.run.app"

  useEffect(() => {
    const connect = () => {
      const wsUrl = apiUrl.startsWith('https') 
        ? apiUrl.replace('https', 'wss') + '/ws/live' 
        : apiUrl.replace('http', 'ws') + '/ws/live'
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws
      
      ws.onopen = () => {
        setIsLive(true)
        addLog({ time: new Date().toLocaleTimeString(), msg: "SYSTEM: Sentinel Link Established", type: "success" })
      }
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        if (data.type === 'ANALYSIS') {
          setAnalysis(data.data)
          if (data.data.threat_stream) {
            data.data.threat_stream.forEach((l: any) => addLog(l))
          }
          if (data.data.system_entropy) setEntropy(data.data.system_entropy)
        } else if (data.type === 'AUDIO') {
          setCurrentAudio(data.data);
          // Auto-reset chunk after short delay to allow fresh state for next chunk
          setTimeout(() => setCurrentAudio(null), 50);
        } else if (data.type === 'SYSTEM') {
          addLog({ time: new Date().toLocaleTimeString(), msg: data.msg, type: "info" })
        }
      }
      
      ws.onclose = () => {
        setIsLive(false)
        setTimeout(connect, 3000)
      }
    }
    
    connect()
    return () => wsRef.current?.close()
  }, [])

  const addLog = (log: any) => {
    setLogs(prev => [log, ...prev].slice(0, 50))
  }

  const handleNeutralize = async () => {
    if (!analysis) return
    setIsAnalyzing(true)
    addLog({ time: new Date().toLocaleTimeString(), msg: `SENTINEL: Deploying Multi-Tier Shield: ${analysis.recommended_action}`, type: "danger" })
    
    try {
      const res = await fetch(`${apiUrl}/neutralize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          threat_type: analysis.threat_type,
          details: { recommended_action: analysis.recommended_action }
        })
      })
      const data = await res.json()
      addLog({ time: new Date().toLocaleTimeString(), msg: `OUTCOME: ${data.status}`, type: "success" })
    } catch (err) {
      addLog({ time: new Date().toLocaleTimeString(), msg: "ERROR: Command Recalibrating", type: "danger" })
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleSwarmDeployment = async () => {
    if (!analysis) return
    try {
      const res = await fetch(`${apiUrl}/swarm`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ threat_type: analysis.threat_type })
      })
      const data = await res.json()
      setSwarmMode(true)
      setSwarmCount(data.agent_count)
      setIsMirage(data.is_mirage)
      addLog({ time: new Date().toLocaleTimeString(), msg: `PLAN T: ${data.status} [Agents: ${data.agent_count}]`, type: "success" })
    } catch (err) {
      addLog({ time: new Date().toLocaleTimeString(), msg: "ERROR: Swarm Collision Detected", type: "danger" })
    }
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setIsAnalyzing(true)
    addLog({ time: new Date().toLocaleTimeString(), msg: `ANALYSIS: Processing SOC Feed: ${file.name}`, type: "system" })
    
    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch(`${apiUrl}/analyze`, {
        method: 'POST',
        body: formData
      })
      const data = await res.json()
      setAnalysis(data)
      addLog({ time: new Date().toLocaleTimeString(), msg: `RESULT: Analysis complete [Confidence: ${(data.confidence*100).toFixed(0)}%]`, type: data.threat_detected ? "danger" : "success" })
    } catch (err) {
      addLog({ time: new Date().toLocaleTimeString(), msg: "ERROR: Analysis Engine Offline", type: "danger" })
    } finally {
      setIsAnalyzing(false)
    }
  }

  const triggerMasterReset = async () => {
    try {
      addLog({ time: new Date().toLocaleTimeString(), msg: "SYSTEM: Master Reset Initiated", type: "system" })
      await fetch(`${apiUrl}/reset`, { method: 'POST' })
      setAnalysis(null)
      setSwarmMode(false)
    } catch (err) {
      addLog({ time: new Date().toLocaleTimeString(), msg: "ERROR: Reset Command Deflected", type: "danger" })
    }
  }

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = 0
    }
  }, [logs])

  return (
    <div className="min-h-screen bg-aegis-dark text-white p-6 font-sans selection:bg-aegis-mint/30">
      <input type="file" ref={fileInputRef} className="hidden" onChange={handleFileUpload} />
      
      {/* Header Area */}
      <header className="flex items-center justify-between mb-8 p-4 glass-card">
        <div className="flex items-center gap-6">
          <div className="flex flex-col cursor-pointer" onClick={triggerMasterReset}>
            <h1 className="text-xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-aegis-mint to-white">
              AEGIS // AGENTIC SENTINEL
            </h1>
            <span className="text-[10px] tracking-[0.3em] font-bold text-white/40 uppercase">
              Production Environment // Tier-4 Shield
            </span>
          </div>
          <div className="h-8 w-px bg-white/10" />
          <NeuralPulse active={isLive} />
        </div>

        <div className="flex items-center gap-4">
          <button 
            onClick={() => fileInputRef.current?.click()}
            className="flex items-center gap-2 px-4 py-2 bg-aegis-mint/10 border border-aegis-mint/20 text-aegis-mint text-[10px] font-black uppercase tracking-widest hover:bg-aegis-mint hover:text-black transition-all rounded-lg"
          >
            <Search className="w-3 h-3" /> Upload SOC Feed
          </button>
          <div className="h-6 w-px bg-white/10" />
          <button 
            onClick={() => setIsMuted(!isMuted)}
            className={clsx(
              "p-2 rounded-lg transition-all duration-300",
              isMuted ? "bg-red-500/20 text-red-400" : "bg-cyan-500/20 text-cyan-400 animate-pulse"
            )}
            title={isMuted ? "Unmute Guardian" : "Mute Guardian"}
          >
            {isMuted ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
          </button>

          <div className="flex items-center space-x-2 px-3 py-1.5 bg-black/40 border border-white/5 rounded-lg">
            {isHydrating ? (
              <RefreshCw className="w-3 h-3 text-aegis-mint animate-spin" />
            ) : (
              <Database className="w-3 h-3 text-aegis-mint" />
            )}
            <span className="text-[10px] font-bold text-aegis-mint uppercase tracking-wider">
              {isHydrating ? "Hydration Active..." : "Firestore: Synced"}
            </span>
          </div>
          <div 
            onClick={() => setIsListening(!isListening)}
            className={cn(
            "p-2 rounded-full transition-all duration-500 cursor-pointer",
            isListening ? "bg-aegis-mint/10 text-aegis-mint box-shadow-mint" : "bg-white/5 text-gray-500"
          )}>
            {isListening ? <Mic className="w-5 h-5 neural-pulse" /> : <MicOff className="w-5 h-5" />}
          </div>
        </div>
      </header>

      {/* Main Grid */}
      <div className="grid grid-cols-12 gap-6 h-[calc(100vh-180px)]">
        
        {/* Left Column: Diagnostics */}
        <div className="col-span-3 flex flex-col gap-6">
          <div className="glass-card p-5 flex flex-col items-center">
            <h2 className="w-full text-[10px] font-bold tracking-widest text-aegis-mint uppercase mb-4 flex items-center gap-2">
              <Shield className="w-3 h-3" /> System Integrity
            </h2>
            <ConfidenceGauge value={analysis ? Math.round((analysis.detection_confidence || 0.94) * 100) : 94} />
          </div>

          <div className="glass-card p-5 flex-1">
            <h2 className="text-[10px] font-bold tracking-widest text-aegis-mint uppercase mb-4 flex items-center gap-2 text-aegis-amber">
              <Activity className="w-3 h-3" /> Entropy Heatmap
            </h2>
            <p className="text-[10px] text-white/40 mb-2 uppercase tracking-tight">Active Vector Density</p>
            <div className="text-2xl font-mono font-bold text-aegis-amber mb-4">
              {entropy.toFixed(4)}
            </div>
            <EntropyHeatmap entropy={entropy} />
          </div>
          
          <div className="glass-card p-5 flex flex-col gap-2">
             {swarmMode && (
               <div className="p-3 bg-aegis-mint/5 border border-aegis-mint/20 rounded-lg mb-2">
                 <p className="text-[10px] font-black text-aegis-mint uppercase tracking-widest mb-1">Swarm Deployment:</p>
                 <div className="flex gap-1.5">
                   {[...Array(swarmCount)].map((_, i) => (
                     <div key={i} className="w-1.5 h-1.5 rounded-full bg-aegis-mint animate-pulse" style={{ animationDelay: `${i * 0.1}s` }} />
                   ))}
                 </div>
               </div>
             )}
             <button 
               onClick={triggerMasterReset}
               className="w-full py-3 bg-aegis-red/10 border border-aegis-red/20 text-aegis-red text-xs font-black uppercase tracking-widest hover:bg-aegis-red hover:text-white transition-all rounded-lg"
             >
                Initiate Core Purge
             </button>
          </div>
        </div>

        {/* Center Column: Reasoning Hub */}
        <div className="col-span-6 flex flex-col gap-6 px-4">
          <div className={cn(
            "glass-card p-8 flex-1 relative overflow-hidden flex flex-col justify-center",
            analysis?.threat_detected && "border-aegis-red/50 shadow-[0_0_50px_rgba(255,61,0,0.15)]"
          )}>
            {/* Shimmer Border Overlay */}
            {isAnalyzing && (
              <div className="absolute inset-0 animate-shimmer pointer-events-none border-2 border-aegis-mint/30 rounded-xl" />
            )}
            
            <div className="absolute top-0 right-0 p-6">
              <Cpu className={cn("w-8 h-8", analysis?.threat_detected ? "text-aegis-red animate-pulse" : "text-aegis-mint")} />
            </div>
            
            <h2 className="text-[10px] font-bold tracking-widest text-aegis-mint uppercase mb-8">
              Gemini Live v2 // Real-Time Reasoning Hub
            </h2>

            <div className="mb-10">
              <motion.h3 
                key={analysis?.threat_type}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-5xl font-black mb-4 tracking-tighter uppercase"
              >
                {analysis?.threat_type || "Passive Sensing..."}
              </motion.h3>
              <div className="flex gap-2">
                {analysis?.threat_detected ? (
                  <>
                    <span className="px-3 py-1 bg-aegis-red/10 text-aegis-red text-[10px] font-black rounded border border-aegis-red/20 tracking-widest uppercase">
                      T1059.003 // Command & Scripting
                    </span>
                    <span className="px-3 py-1 bg-white/5 text-white/40 text-[10px] font-black rounded border border-white/10 tracking-widest uppercase">
                      MITRE: Execution
                    </span>
                  </>
                ) : (
                  <span className="px-3 py-1 bg-aegis-mint/10 text-aegis-mint text-[10px] font-black rounded border border-aegis-mint/20 tracking-widest uppercase">
                    Protocol G // Global Guard Active
                  </span>
                )}
              </div>
            </div>

            <div className="relative p-8 bg-black/60 border border-white/5 rounded-2xl min-h-[200px] flex items-center shadow-2xl">
              <div className="absolute top-0 left-0 w-8 h-8 border-t-2 border-l-2 border-aegis-mint/30 rounded-tl-xl" />
              <div className="absolute bottom-0 right-0 w-8 h-8 border-b-2 border-r-2 border-aegis-mint/30 rounded-br-xl" />
              <p className="text-lg leading-relaxed text-white/90 font-medium italic">
                {analysis?.description || "Aegis is currently monitoring tactical neural streams. No immediate corrective action required for baseline entropy levels. Multimodal sensors are calibrated for sub-200ms latency reasoning."}
              </p>
            </div>

            <div className="mt-8 flex gap-4">
              <button 
                onClick={handleNeutralize}
                disabled={!analysis?.threat_detected || isAnalyzing}
                className={cn(
                  "flex-1 py-4 text-sm font-black uppercase tracking-[0.3em] rounded-xl transition-all",
                  analysis?.threat_detected 
                    ? "bg-aegis-red text-white shadow-[0_0_30px_rgba(255,61,0,0.3)] hover:scale-[1.02]" 
                    : "bg-white/5 text-white/20 cursor-not-allowed"
                )}
              >
                {isAnalyzing ? "Processing..." : "Initiate Neutralization"}
              </button>
              <button 
                onClick={handleSwarmDeployment}
                className="px-8 py-4 bg-white/5 border border-white/10 text-white/60 text-sm font-black uppercase tracking-widest hover:bg-white/10 transition-all rounded-xl"
              >
                Deploy Swarm
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Log Stream */}
        <div className="col-span-3 flex flex-col gap-6 overflow-hidden">
          <div className="glass-card p-0 flex flex-col flex-1 overflow-hidden border-white/5">
            <div className="p-4 border-b border-white/5 bg-white/5 flex items-center justify-between">
              <h2 className="text-[10px] font-bold tracking-widest text-white/60 uppercase m-0 flex items-center gap-2">
                <Terminal className="w-3 h-3" /> Log Siphon Stream
              </h2>
              <div className="flex gap-1.5">
                <div className="w-1.5 h-1.5 rounded-full bg-red-500/40" />
                <div className="w-1.5 h-1.5 rounded-full bg-yellow-500/40" />
                <div className="w-1.5 h-1.5 rounded-full bg-green-500/40" />
              </div>
            </div>
            
            <div className="p-4 overflow-y-auto font-mono text-[10px] leading-tight flex-1" ref={scrollRef}>
              <AnimatePresence initial={false}>
                {logs.map((log, i) => (
                  <motion.div
                    key={i + (log.time || '')}
                    initial={{ opacity: 0, x: -10, height: 0 }}
                    animate={{ opacity: 1, x: 0, height: 'auto' }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className={cn(
                      "mb-2 p-2 rounded transition-colors border-l-2",
                      log.type === 'danger' ? "bg-aegis-red/10 border-aegis-red text-aegis-red" : 
                      log.type === 'success' ? "bg-aegis-mint/5 border-aegis-mint text-aegis-mint" :
                      "bg-white/5 border-white/10 text-white/40"
                    )}
                  >
                    <div className="flex justify-between mb-1 opacity-50 font-bold">
                      <span>[{log.time}]</span>
                      <span className="uppercase">{log.type}</span>
                    </div>
                    <div className="break-all">{log.msg}</div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          </div>
        </div>

      </div>

      {/* Persistence Bar */}
      <div className="fixed bottom-0 left-0 right-0 h-1 bg-white/5">
        <motion.div 
          className="h-full bg-aegis-mint shadow-[0_0_10px_#00FF9D]"
          initial={{ width: "0%" }}
          animate={{ width: "100%" }}
          transition={{ duration: 60, repeat: Infinity, ease: "linear" }}
        />
      </div>

      <style jsx global>{`
        @font-face {
          font-family: 'JetBrains Mono';
          src: url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
        }
        .box-shadow-mint {
          box-shadow: 0 0 20px rgba(0, 255, 157, 0.2);
        }
      `}</style>

      {/* Audio Bridge Component */}
      <AudioPlayer audioChunk={currentAudio} isMuted={isMuted} />
    </div>
  )
}
