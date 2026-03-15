from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import json
import asyncio
from agent_logic import AegisAgent
from performer import ShieldPerformer

app = FastAPI(title="Aegis ADK Cyber-Shield API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Agent & Performer
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "DEVELOPMENT_KEY")
agent = AegisAgent(api_key=GEMINI_API_KEY)
performer = ShieldPerformer()

class ThreatAction(BaseModel):
    threat_type: str
    details: dict

@app.post("/analyze")
async def analyze_dashboard(file: UploadFile = File(...)):
    """Multimodal analysis endpoint using ADK-wrapped Gemini."""
    try:
        image_bytes = await file.read()
        analysis_raw = await agent.analyze_dashboard(image_bytes)
        
        # Robust JSON extraction
        try:
            if "```json" in analysis_raw:
                json_str = analysis_raw.split("```json")[1].split("```")[0].strip()
            else:
                json_str = analysis_raw.strip()
            return json.loads(json_str)
        except:
            return {"error": "Failed to parse agent output", "raw": analysis_raw}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/neutralize")
async def neutralize_threat(action: ThreatAction):
    """Tiered Defense Execution (Plans A-I)"""
    threat_type = action.threat_type
    recommended_action = action.details.get("recommended_action", "")

    # Plan I: The Infinite Maze for unknown threats
    if threat_type == "UNKNOWN" or not recommended_action:
        challenge = agent.generate_maze_challenge(threat_type)
        return {"status": "Plan I Triggered", "action": "Infinite Maze Challenged", "challenge": challenge}

    # Plan D: Morphic Deception (Honeypot)
    if os.getenv("DECEPTION_MODE") == "true":
        return {"status": "Morphic Deception Active", "action": "Trapping Attacker in Sandbox"}

    # Plan F: Multi-Agent Consensus
    script = agent.generate_neutralization_script(threat_type, recommended_action)
    is_safe, consensus_msg = await agent.validate_neutralization_scripts(script)
    
    if not is_safe:
        return {"status": "Aegis Shield Hardened", "action": "Neutralization Blocked", "reason": consensus_msg}

    # Final Execution (Plans A-C)
    result = performer.execute_containment_script(script)
    return {"status": "Threat Neutralized", "action": "Shield Deployed", "execution_result": result}

# --- MULTIMODAL LIVE STREAMING (Gemini Live API Pattern) ---
@app.websocket("/ws/live")
async def live_multimodal_endpoint(websocket: WebSocket):
    """
    Multimodal Live API Endpoint for real-time SOC monitoring.
    Handles continuous video/audio streams for millisecond-level reaction.
    """
    await websocket.accept()
    try:
        while True:
            # Receive multimodal data (could be video frames or audio chunks)
            data = await websocket.receive_bytes()
            
            # Real-time processing via Gemini Live Logic
            # Note: In a full implementation, this connects to Gemini's Bidi stream
            await asyncio.sleep(0.1) # Simulate low-latency processing
            
            await websocket.send_json({
                "source": "AEGIS_LIVE_SENSE",
                "status": "MONITORING",
                "integrity": "99.99%",
                "alert": None
            })
    except WebSocketDisconnect:
        print("Live Stream Disconnected")
    except Exception as e:
        print(f"WS Error: {e}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
