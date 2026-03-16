import httpx
import asyncio
import json

async def simulate_forensic_trap():
    url = "http://localhost:8081"
    print("INITIATING FORENSIC MIRROR TRAP [PLAN M]...")
    
    # Step 1: Trigger Swarm/Mirage first
    payload_swarm = {
        "threat_type": "Data_Exfiltration",
        "details": {
            "attacker_count": 2,
            "stage_progression": 0.95
        }
    }
    
    async with httpx.AsyncClient() as client:
        print("\n--- TRIGGERING HYDRA MIRAGE ---")
        await client.post(f"{url}/swarm", json=payload_swarm)
        
        # Step 2: Extract Forensics
        print("\n--- EXTRACTING FORENSIC DOSSIER ---")
        payload_forensics = {
            "threat_type": "Data_Exfiltration",
            "details": {
                "attacker_ip": "194.32.1.84",
                "session_logs": [
                    "nmap -sV -T4 10.0.0.5",
                    "sqlmap -u http://target/api --dbs",
                    "Mirage_Redirection_Success: redirected to /tmp/sandbox_v4"
                ]
            }
        }
        
        response = await client.post(f"{url}/forensics", json=payload_forensics)
        data = response.json()
        
        # Handle possible nested string from agent output
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except:
                pass
            
        print(f"\nFORENSIC ATTRITION SUCCESSFUL:")
        if isinstance(data, dict):
            print(f"GENOME HASH: {data.get('genome_hash')}")
            print(f"PROBABLE ORIGIN: {data.get('geo_origin')}")
            print(f"MOTIVE: {data.get('motive_analysis')}")
            print(f"EVIDENCE SECURED: {data.get('evidence_captured')}")
        else:
            print(f"RAW DATA: {data}")

    print("\nSIMULATION COMPLETE: ATTACKER TRACED AND PROFILED.")

if __name__ == "__main__":
    try:
        asyncio.run(simulate_forensic_trap())
    except Exception as e:
        print(f"TEST FAILED: {e}")
