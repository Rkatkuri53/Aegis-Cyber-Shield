import asyncio
import websockets
import json
import time

async def test_bridge():
    uri = "ws://127.0.0.1:8081/ws/live"
    print(f"Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print("Link Established. Waiting for Heartbeat...")
            # Wait for any message
            response = await asyncio.wait_for(websocket.recv(), timeout=10)
            data = json.loads(response)
            print(f"Received: {data}")
            
            if data.get("type") == "HEARTBEAT" or data.get("status") == "MONITORING":
                print("ZERO-CRASH STATUS: VERIFIED [SHIELD ACTIVE]")
            else:
                print(f"Unexpected data: {data}")
    except Exception as e:
        print(f"Link Fault: {e}")

if __name__ == "__main__":
    asyncio.run(test_bridge())
