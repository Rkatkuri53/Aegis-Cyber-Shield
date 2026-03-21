from google import genai
import PIL.Image
import io
import os
import asyncio
import json
import re
import time
import traceback
from fastapi import WebSocket

# Conditional import for Windows Event Log access
try:
    import platform
    if platform.system() == "Windows":
        import win32evtlog
        HAS_WIN32 = True
    else:
        HAS_WIN32 = False
except ImportError:
    HAS_WIN32 = False

from typing import Optional, List, Any
from schemas import AegisState

class AegisAgent:
    """
    AEGIS: The Multimodal Cyber-Shield Agent.
    Forced Sync Mode: Aligns with user's specific field requirements.
    """
    def __init__(self, api_key: str):
        self.api_key: str = api_key
        self.client: Any = genai.Client(api_key=api_key, http_options={'api_version': 'v1alpha'})
        self.active_session: Optional[Any] = None
        self.log_queue: asyncio.Queue = asyncio.Queue(maxsize=100) # Throttling Buffer

    def get_windows_logs(self, log_type="Security", count=5):
        """Siphons Windows Event Logs with graceful fallbacks."""
        if not HAS_WIN32:
            return [{"time": time.strftime("%H:%M:%S"), "msg": "OS_SHIELD: Log Siphoning Unavailable (Linux/No-Lib)", "type": "warning"}]
        
        logs = []
        try:
            hand = win32evtlog.OpenEventLog(None, log_type)
            flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
            events = win32evtlog.ReadEventLog(hand, flags, 0)
            for event in events[:count]:
                msg = f"EVT_{log_type}: {event.SourceName} (ID: {event.EventID})"
                logs.append({"time": event.TimeGenerated.Format(), "msg": msg, "type": "system"})
        except Exception as e:
            error_str = str(e)
            if "Access is denied" in error_str:
                if log_type == "Security":
                    return self.get_windows_logs(log_type="Application") # Level 2 Fallback
                elif log_type == "Application":
                    return self.get_windows_logs(log_type="System") # Level 3 Fallback
            logs.append({"time": time.strftime("%H:%M:%S"), "msg": f"LOG_ERR: {error_str[:30]}", "type": "error"})
        return logs

    async def run_live_stream(self, ctx: AegisState, websocket: WebSocket, session_id: str = "default_session"):
        model_id = "gemini-2.0-flash-exp"
        config = {
            "response_modalities": ["AUDIO", "TEXT"],
            "speech_config": {
                "voice_config": {
                    "prebuilt_voice_config": {
                        "voice_name": "Puck" # Guardian Voice
                    }
                }
            }
        }
        
        reflexive_prompt = "AEGIS_RECOVERY_PROTOCOL: Stream disconnected. Resume tactical context. Monitoring active."
        
        # Ensure stale sessions are closed before starting
        if self.active_session:
            print("[LIVE-CORE] Killing Zombie Session...", flush=True)
            self.active_session = None

        self.active_session = None
        
        tasks = []
        while True:
            try:
                print(f"[LIVE-CORE] Connecting to Gemini Live Session: {session_id}...", flush=True)
                
                # Mock Mode for Stress Testing / No Key
                if self.api_key == "DEVELOPMENT_KEY":
                    print("[LIVE-CORE] WARNING: Running in MOCK MODE (No API Key)", flush=True)
                    while True:
                        await asyncio.sleep(0.1)
                        audit_logs = []
                        if not self.log_queue.empty():
                            audit_logs = await self.log_queue.get()
                        
                        analysis_data = {
                            "detection_confidence": 0.50,
                            "system_entropy": 0.42,
                            "threat_stream": audit_logs,
                            "quantum_diagnostics": {"threat_type": "MOCK_ANALYSIS", "description": "Running without API Key."},
                            "threat_detected": False
                        }
                        
                        if any("999" in str(l.get("msg", "")) for l in audit_logs):
                            analysis_data["threat_detected"] = True
                            analysis_data["quantum_diagnostics"]["threat_type"] = "CRITICAL INTERRUPT"
                        
                        await websocket.send_json({"type": "ANALYSIS", "data": analysis_data})
                        await asyncio.sleep(5) # Slow down mock loop
                        
                async with self.client.aio.live.connect(model=model_id, config=config) as session:
                    self.active_session = session
                    
                    tasks = []
                    
                    async def log_producer():
                        """Background task to siphon logs without blocking the main loop."""
                        while True:
                            try:
                                logs = self.get_windows_logs()
                                if self.log_queue.full():
                                    await self.log_queue.get() # Pop old
                                await self.log_queue.put(logs)
                                await asyncio.sleep(1) # Throttling: 1 check per second
                            except asyncio.CancelledError:
                                break
                            except Exception as e:
                                print(f"[LOG-PRODUCER-ERR] {e}", flush=True)
                                await asyncio.sleep(5)
                    
                    async def handle_outbound():
                        try:
                            while True:
                                data = await websocket.receive_bytes()
                                await session.send(data)
                        except Exception as e:
                            print(f"[LIVE-OUTBOUND] WebSocket closed: {e}", flush=True)
                            raise e

                    async def handle_inbound():
                        async for message in session:
                            try:
                                if hasattr(message, 'error') and message.error:
                                    asyncio.create_task(session.send(reflexive_prompt, end_of_turn=True))
                                    await websocket.send_json({"type": "SYSTEM", "msg": "Aegis // Re-syncing...", "type": "system"})

                                if hasattr(message, 'server_content') and message.server_content:
                                    content_str = str(message.server_content)
                                    # Siphon logs from the queue
                                    audit_logs = []
                                    if not self.log_queue.empty():
                                        audit_logs = await self.log_queue.get()
                                    
                                    analysis_data = {
                                        "detection_confidence": 0.50,
                                        "system_entropy": 0.42,
                                        "threat_stream": audit_logs + [{"time": time.strftime("%H:%M:%S"), "msg": "Real-Time Neural Stream Active", "type": "success"}],
                                        "quantum_diagnostics": {"threat_type": "Real-Time Analysis", "description": content_str},
                                        "threat_detected": "attack" in content_str.lower(),
                                        "confidence": 0.50,
                                        "description": content_str
                                    }

                                    if any(k in content_str.lower() for k in ["attack", "breach", "threat"]):
                                        analysis_data["detection_confidence"] = 0.95
                                        analysis_data["confidence"] = 0.95
                                        analysis_data["threat_stream"][0]["type"] = "danger"
                                        analysis_data["threat_stream"][0]["msg"] = "THREAT DETECTED: " + content_str[:50]

                                    # Voice Trigger: Force verbal alert for Critical / Brute Force
                                    if any(k in str(audit_logs).lower() for k in ["4625", "critical", "brute force"]):
                                        voice_trigger_prompt = "AEGIS_GUARD: Critical breach attempt detected. Verbally notify the team of the threat and suggested containment."
                                        asyncio.create_task(session.send(voice_trigger_prompt, end_of_turn=True))

                                    json_match = re.search(r'\{.*\}', content_str, re.DOTALL)
                                    if json_match:
                                        try:
                                            parsed = json.loads(json_match.group())
                                            analysis_data.update(parsed)
                                            if "confidence" in parsed: analysis_data["detection_confidence"] = parsed["confidence"]
                                        except: pass

                                    if hasattr(message, 'server_content') and message.server_content.model_turn:
                                        for part in message.server_content.model_turn.parts:
                                            if hasattr(part, 'inline_data') and part.inline_data:
                                                import base64
                                                audio_b64 = base64.b64encode(part.inline_data.data).decode('utf-8')
                                                await websocket.send_json({
                                                    "type": "AUDIO",
                                                    "data": audio_b64
                                                })

                                    payload = {
                                        "type": "ANALYSIS",
                                        "data": analysis_data
                                    }
                                    await websocket.send_json(payload)

                            except Exception as e:
                                print(f"[LIVE-INBOUND-ERR] {e}", flush=True)

                    outbound_task = asyncio.create_task(handle_outbound())
                    inbound_task = asyncio.create_task(handle_inbound())
                    producer_task = asyncio.create_task(log_producer())
                    tasks = [outbound_task, inbound_task, producer_task]
                    
                    await asyncio.gather(*tasks)

            except Exception as e:
                print(f"[LIVE-CORE-ERR] Runtime Exception: {e}", flush=True)
                # Bulletproof Cleanup
                for task in tasks:
                    if not task.done():
                        task.cancel()
                if self.active_session:
                    # Attempt graceful close if supported, otherwise just drop
                    self.active_session = None
                await asyncio.sleep(2)
                continue
            finally:
                self.active_session = None

    async def analyze_dashboard(self, ctx, image_bytes):
        try:
            image = PIL.Image.open(io.BytesIO(image_bytes))
            prompt = "Analyze this SOC dashboard for threats. Return JSON."
            response = await self.client.aio.models.generate_content(model='gemini-2.0-flash-exp', contents=[prompt, image])
            return response.text
        except Exception as e:
            return json.dumps({"threat_detected": False, "description": "Offline fallback."})
