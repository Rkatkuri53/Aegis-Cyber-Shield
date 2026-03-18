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
    import win32evtlog
    HAS_WIN32 = True
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
        config = {"content_type": "audio/pcm"} 
        
        reflexive_prompt = "AEGIS_RECOVERY_PROTOCOL: Stream disconnected. Resume tactical context. Monitoring active."

        while True:
            try:
                print(f"[LIVE-CORE] Connecting to Gemini Live Session: {session_id}...", flush=True)
                async with self.client.aio.live.connect(model=model_id, config=config) as session:
                    self.active_session = session
                    
                    tasks = []
                    
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
                                    
                                    # Siphon logs to inject into the stream
                                    audit_logs = self.get_windows_logs()
                                    
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

                                    json_match = re.search(r'\{.*\}', content_str, re.DOTALL)
                                    if json_match:
                                        try:
                                            parsed = json.loads(json_match.group())
                                            analysis_data.update(parsed)
                                            if "confidence" in parsed: analysis_data["detection_confidence"] = parsed["confidence"]
                                        except: pass

                                    payload = {
                                        "type": "ANALYSIS",
                                        "data": analysis_data
                                    }
                                    await websocket.send_json(payload)

                            except Exception as e:
                                print(f"[LIVE-INBOUND-ERR] {e}", flush=True)

                    outbound_task = asyncio.create_task(handle_outbound())
                    inbound_task = asyncio.create_task(handle_inbound())
                    tasks = [outbound_task, inbound_task]
                    
                    await asyncio.gather(*tasks)

            except Exception as e:
                print(f"[LIVE-CORE-ERR] Runtime Exception: {e}", flush=True)
                # Cleanup tasks if they are still running to prevent leaks
                for task in tasks:
                    if not task.done():
                        task.cancel()
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
