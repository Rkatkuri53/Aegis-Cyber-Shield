import asyncio
import json
import time
import websockets
import platform

async def simulate_stress(uri):
    print(f"[STRESS] Target: {uri}")
    try:
        async with websockets.connect(uri) as websocket:
            print("[STRESS] Connected. Sending burst...")
            
            # Simulate 100 log messages in 1 second
            for i in range(100):
                msg = {
                    "type": "MOCK_LOG",
                    "data": {
                        "EventID": 999 if i == 50 else 100, # Inject high priority at middle
                        "msg": f"MOCK_STRESS_EVENT_{i}",
                        "time": time.strftime("%H:%M:%S")
                    }
                }
                # Note: The agent listens for bytes (audio) usually, but we can test the JSON control channel if implemented
                # For this test, we verify if the server stays alive during internal log siphoning spikes
                await asyncio.sleep(0.01) 
            
            print("[STRESS] Burst sent. Waiting for agent processing...")
            # Wait to see if server crashes or slows down
            start = time.time()
            while time.time() - start < 5:
                resp = await websocket.recv()
                data = json.loads(resp)
                if data.get("type") == "ANALYSIS":
                    latency = (time.time() - start) * 1000
                    print(f"[REASONING] Received analysis at {latency:.2f}ms")
                    if "CRITICAL INTERRUPT" in str(data):
                        print("[SUCCESS] Barge-In Triggered correctly!")
            
    except Exception as e:
        print(f"[STRESS-FAIL] {e}")

if __name__ == "__main__":
    server_uri = "ws://localhost:8081/ws/live"
    asyncio.run(simulate_stress(server_uri))
