import asyncio
import httpx
import json

async def simulate_coordinated_attack():
    url = "http://localhost:8081"
    print("INITIATING COORDINATED TEAM ATTACK [3 HACKERS]...")
    
    # Stage 1: Initial Probing (Low Proximity)
    print("\n--- STAGE 1: PERIPHERAL PROBING ---")
    payload_stage_1 = {
        "threat_type": "Distributed_Brute_Force",
        "details": {
            "attacker_count": 3,
            "stage_progression": 0.2
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{url}/swarm", json=payload_stage_1)
        data = response.json()
        print(f"AEGIS STATUS: {data['status']}")
        print(f"SENTINEL AGENTS DEPLOYED: {data['agent_count']}")
        print(f"PROTOCOL: {data['protocol'][:100]}...")

    await asyncio.sleep(2)

    # Stage 2: Final Target Proximity (The Mirage Trigger)
    print("\n--- STAGE 2: TARGET PROXIMITY [95%] ---")
    payload_stage_2 = {
        "threat_type": "Core_Database_Exfiltration",
        "details": {
            "attacker_count": 3,
            "stage_progression": 0.95
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{url}/swarm", json=payload_stage_2)
        data = response.json()
        print(f"AEGIS STATUS: {data['status']}")
        print(f"SILENT STALKER COUNT: {data['agent_count']}")
        print(f"MIRAGE ACTIVE: {data['is_mirage']}")
        print(f"REDIRECTION PAYLOAD: {data['protocol']}")

    print("\nSIMULATION COMPLETE: ATTACKER TRAPPED IN HYDRA MIRAGE.")

if __name__ == "__main__":
    try:
        asyncio.run(simulate_coordinated_attack())
    except Exception as e:
        print(f"TEST FAILED: Ensure Aegis server is running on :8080. Error: {e}")
