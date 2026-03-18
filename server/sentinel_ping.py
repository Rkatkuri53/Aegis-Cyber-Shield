import asyncio
import json
import websockets
import time

async def sentinel_ping():
    uri = "ws://localhost:8081/ws/live"
    print(f"[PING] Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            # 1. Inject Audit Event & Spike Confidence
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
                    # Legacy fallback
                    "confidence": 0.88,
                    "threat_detected": True
                }
            }
            
            print("[PING] Sending Audit Packet (88% Confidence)...")
            await websocket.send(json.dumps(audit_packet))
            
            # Keep alive for 5 seconds as requested for the spike
            print("[PING] Spike active for 5 seconds...")
            await asyncio.sleep(5)
            
            print("[PING] Sentinel Ping Complete.")
            
    except Exception as e:
        print(f"[PING-ERROR] {e}")

if __name__ == "__main__":
    asyncio.run(sentinel_ping())
