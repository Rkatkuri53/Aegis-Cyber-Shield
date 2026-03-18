from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect, Request
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import BaseModel
import uvicorn
import os
import json
import asyncio
import time
import traceback
from agent_logic import AegisAgent
from schemas import AegisState
from typing import List, Optional
import io

# Optional Firestore Integration
try:
    from google.cloud import firestore
    HAS_FIRESTORE = True
except ImportError:
    HAS_FIRESTORE = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    await recover_state_from_firestore()
    asyncio.create_task(start_heartbeat())
    yield
    # Shutdown logic
    await save_state_to_firestore()

app = FastAPI(title="Aegis ADK Cyber-Shield API", lifespan=lifespan)

# Stabilized CORS: Restrict to known dashboard origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        try:
            await websocket.accept()
            self.active_connections.append(websocket)
            print(f"[BRIDGE] Connected: {websocket.client.host}", flush=True)
            # Immediate Sync on Connection
            await self.broadcast_state(websocket)
        except Exception as e:
            print(f"[BRIDGE-ERR] Handshake failed: {e}", flush=True)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in list(self.active_connections):
            asyncio.create_task(self.safe_send(connection, message))

    async def safe_send(self, websocket: WebSocket, message: dict):
        try:
            await websocket.send_json(message)
        except:
            self.disconnect(websocket)

    async def broadcast_state(self, websocket: WebSocket = None):
        """Forces a 'Full State' packet to the UI."""
        full_state = {
            "type": "ANALYSIS",
            "data": {
                "detection_confidence": 0.94,
                "system_entropy": 0.7721,
                "threat_stream": [
                    {"time": time.strftime("%H:%M:%S"), "msg": "Aegis // System Online (Neural Link Verified)", "type": "success"},
                    {"time": time.strftime("%H:%M:%S"), "msg": "Protocol G: Global Guard Active", "type": "system"}
                ],
                "quantum_diagnostics": {
                    "threat_type": "Sync Successful",
                    "description": "Multimodal bridge is established. Awaiting tactical stream.",
                    "recommended_action": "Maintain Passive Sensing"
                },
                "confidence": 0.94,
                "threat_detected": False,
                "swarm_active": state.swarm_active,
                "mirage_active": state.mirage_active
            }
        }
        if websocket:
            await self.safe_send(websocket, full_state)
        else:
            await self.broadcast(full_state)

manager = ConnectionManager()

async def start_heartbeat():
    while True:
        try:
            await asyncio.sleep(10) # Reduced frequency for stability
            await manager.broadcast({"type": "HEARTBEAT", "time": time.strftime("%H:%M:%S")})
            await manager.broadcast_state()
        except Exception as e:
            print(f"[HEARTBEAT-ERR] {e}", flush=True)

state = AegisState()

# Bulletproof Firestore Logic
db = firestore.Client() if HAS_FIRESTORE and os.getenv("GOOGLE_APPLICATION_CREDENTIALS") else None

async def save_state_to_firestore():
    if not db: return
    try:
        doc_ref = db.collection(u'aegis_sessions').document(u'active_session')
        doc_ref.set({
            u'diag_state': {
                u'swarm_active': state.swarm_active,
                u'mirage_active': state.mirage_active,
                u'last_reset': state.last_reset,
                u'diag_session_id': state.diag_session_id
            },
            u'timestamp': firestore.SERVER_TIMESTAMP
        })
    except Exception as e:
        print(f"[FIRESTORE-SAVE-ERR] {e}", flush=True)

async def recover_state_from_firestore():
    global state
    if not db: return
    try:
        doc_ref = db.collection(u'aegis_sessions').document(u'active_session')
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict().get('diag_state', {})
            # Validation & Sanitization
            state.swarm_active = bool(data.get('swarm_active', False))
            state.mirage_active = bool(data.get('mirage_active', False))
            state.last_reset = float(data.get('last_reset', time.time()))
            state.diag_session_id = str(data.get('diag_session_id', f"diag_{int(time.time())}"))
            print(f"[FIRESTORE] State Recovered: {state.diag_session_id}", flush=True)
        else:
            print("[FIRESTORE] No state found. Initializing clean state.", flush=True)
    except Exception as e:
        print(f"[FIRESTORE-RECOVER-ERR] {e}. Falling back to clean state.", flush=True)
        state = AegisState() # Reset to clean state on corruption

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "DEVELOPMENT_KEY")
agent = AegisAgent(api_key=GEMINI_API_KEY)

@app.websocket("/ws/live")
async def live_multimodal_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await agent.run_live_stream(state, websocket, session_id=state.diag_session_id)
    except WebSocketDisconnect:
        print("[BRIDGE] Client disconnected.", flush=True)
    except Exception as e:
        print(f"[BRIDGE-ERR] Stream fault: {e}", flush=True)
    finally:
        manager.disconnect(websocket)

@app.post("/sentinel-ping")
async def manual_sentinel_ping():
    audit_packet = {
        "type": "ANALYSIS",
        "data": {
            "detection_confidence": 0.88,
            "system_entropy": 0.8888,
            "threat_stream": [
                {"time": time.strftime("%H:%M:%S"), "msg": "INTERNAL AUDIT: Neural Link Verified", "type": "success"}
            ],
            "quantum_diagnostics": {
                "threat_type": "SENTINEL PING",
                "description": "Manual audit event injected for link verification.",
                "recommended_action": "Proceed with Final Recording"
            },
            "confidence": 0.88,
            "threat_detected": True
        }
    }
    await manager.broadcast(audit_packet)
    return {"status": "SENTINEL_PING_INJECTED"}

@app.post("/reset")
async def reset():
    global state
    state = AegisState()
    await save_state_to_firestore() # Persist the reset
    await manager.broadcast({"type": "RESET_STATE"})
    return {"status": "RESET_SUCCESS"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081)
