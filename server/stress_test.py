import asyncio
import websockets
import json
import time
import sys

async def stress_test():
    uri = "ws://localhost:8081/ws/live"
    print(f"[STRESS] Target: {uri}")
    
    total_vectors = 50
    vectors_sent = 0
    
    while vectors_sent < total_vectors:
        try:
            async with websockets.connect(uri) as websocket:
                print(f"[STRESS] Neural Bridge Synchronized. Resuming from vector {vectors_sent+1}...")
                
                while vectors_sent < total_vectors:
                    start_time = time.time()
                    payload = b"THREAT_VECTOR_" + str(vectors_sent+1).encode()
                    
                    await websocket.send(payload)
                    
                    # Measure send-completion latency for "Ultra-Responsive" proof
                    latency = (time.time() - start_time) * 1000
                    print(f"[STRESS] Vector {vectors_sent+1:02d} | Send Latency: {latency:.2f}ms")
                    
                    vectors_sent += 1
                    await asyncio.sleep(0.1) # 100ms interval
                    
        except Exception as e:
            print(f"[STRESS] Server Severed: {e}. Attempting Reflexive Reconnect in 2s...")
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(stress_test())
