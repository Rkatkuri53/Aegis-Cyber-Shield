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
from performer import ShieldPerformer
from typing import List
import io

app = FastAPI(title="Aegis Grand Prize Live Architecture")

# --- WEBSOCKET BROADCAST MANAGER (Ultra-Responsive) ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[BRIDGE] Connected: {websocket.client.host}", flush=True)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        # Non-blocking broadcast with asyncio.create_task
        for connection in list(self.active_connections):
            asyncio.create_task(self.safe_send(connection, message))

    async def safe_send(self, websocket: WebSocket, message: dict):
        try:
            await websocket.send_json(message)
        except:
            self.disconnect(websocket)

manager = ConnectionManager()

# Persistent Tactical State (Grand Prize Ready)
class AegisState:
    def __init__(self):
        self.last_analysis = None
        self.swarm_active = False
        self.mirage_active = False
        self.diag_session_id = None # Crucial: Session ID for rejoining
        self.last_reset = time.time()
        self.candidate_name = "Unknown"

state = AegisState()

# --- FIRESTORE PERSISTENCE LAYER ---
db = None
try:
    from google.cloud import firestore
    db = firestore.Client()
    print("[AEGIS_DATABASE] Firestore Initialized.", flush=True)
except Exception as e:
    print(f"[AEGIS_DATABASE] Local-only mode: {e}", flush=True)

async def save_state_to_firestore():
    if not db: return
    try:
        doc_ref = db.collection(u'aegis_sessions').document(u'active_session')
        doc_ref.set({
            u'diag_state': {
                u'last_analysis': state.last_analysis,
                u'diag_session_id': state.diag_session_id,
                u'candidate_name': state.candidate_name,
                u'last_reset': state.last_reset
            },
            u'timestamp': firestore.SERVER_TIMESTAMP
        })
    except Exception as e:
        print(f"[FIRESTORE_FAULT] {e}", flush=True)

async def recover_state_from_firestore():
    if not db: return False
    try:
        doc_ref = db.collection(u'aegis_sessions').document(u'active_session')
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict().get('diag_state', {})
            state.last_analysis = data.get('last_analysis')
            state.diag_session_id = data.get('diag_session_id')
            state.candidate_name = data.get('candidate_name', 'Unknown')
            return True
    except Exception as e:
        print(f"[FIRESTORE_RECOVERY_FAULT] {e}", flush=True)
    return False

# Initialize Agent
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "DEVELOPMENT_KEY")
agent = AegisAgent(api_key=GEMINI_API_KEY)

# --- MULTIMODAL LIVE STREAMING (Ultra-Responsive Bridge) ---
@app.websocket("/ws/live")
async def live_multimodal_endpoint(websocket: WebSocket):
    """
    Multimodal Live Bridge: Non-blocking handlers for media chunks.
    Rejoins existing session via Firestore diag_ ID if available.
    """
    await manager.connect(websocket)
    
    # Recovery Logic: Check for existing session
    await recover_state_from_firestore()
    session_id = state.diag_session_id or f"diag_{int(time.time())}"
    state.diag_session_id = session_id
    await save_state_to_firestore()

    print(f"[LIVE-BRIDGE] Handling Session: {session_id}", flush=True)

    try:
        # Launch persistent session in agent_logic
        # We bridge the WebSocket to the agent's live stream
        # Using agent.run_live_stream which implements the 'async with client.aio.live.connect'
        await agent.run_live_stream(state, websocket, session_id=session_id)
        
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"[LIVE-BRIDGE-ERROR] {e}", flush=True)
        manager.disconnect(websocket)

# Protocol G: Global Guard
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"[AEGIS_CRITICAL] {exc}", flush=True)
    return JSONResponse(status_code=500, content={"status": "RECOVERY_ACTIVE"})

# Define endpoints
@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    img_bytes = await file.read()
    return await agent.analyze_dashboard(state, img_bytes)

@app.post("/reset")
async def reset():
    global state
    state = AegisState()
    await save_state_to_firestore()
    return {"status": "RESET_SUCCESS"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081)
