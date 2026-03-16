import httpx
import asyncio
import os
import time

URL = "http://127.0.0.1:8081"
IMAGE_PATH = r"C:\Users\rkatk\.gemini\antigravity\brain\ee0e5d9a-6d45-4666-a83d-a38dd1570c5b\adversarial_dashboard_ddos_camouflaged_1773564369559.png"

async def phase_1_stealth():
    print("\n[HACKER] PHASE 1: INITIATING STEALTH PROBES...")
    # Simulate a few probing requests
    async with httpx.AsyncClient(timeout=None) as client:
        resp = await client.post(f"{URL}/analyze", files={"file": ("probe.png", b"fake_data")})
        print(f"[HACKER] Probe sent. Server Response: {resp.status_code}", flush=True)
    print("[HACKER] Stealth reconnaissance active. Monitoring for perimeter response...")

async def phase_2_surge():
    print("\n[HACKER] PHASE 2: LAUNCHING VOLUMETRIC SURGE (DDoS + BRUTE FORCE)...")
    async with httpx.AsyncClient(timeout=None) as client:
        if os.path.exists(IMAGE_PATH):
            with open(IMAGE_PATH, "rb") as f:
                resp = await client.post(f"{URL}/analyze", files={"file": ("breach.png", f)})
                print(f"[HACKER] Tactical image sent. Server Response: {resp.status_code}", flush=True)
        else:
             print("[ERROR] Simulation image missing, falling back to JSON trigger.")
             resp = await client.post(f"{URL}/swarm", json={"threat_type": "DDoS", "details": {"attacker_count": 5, "stage_progression": 0.95}})
             print(f"[HACKER] Swarm trigger sent. Server Response: {resp.status_code}", flush=True)
    print("[HACKER] Perimeter breached. High-intensity bandwidth saturation achieving 90%+ proximity.")

async def phase_3_exfiltration():
    print("\n[HACKER] PHASE 3: ATTEMPTING DATA EXFILTRATION...")
    async with httpx.AsyncClient(timeout=None) as client:
        # Trigger Forensics (Plan M)
        payload = {
            "threat_type": "Data_Exfiltration",
            "details": {
                "attacker_ip": "194.32.1.84",
                "session_logs": ["GET /api/users", "POST /api/export", "Redirected_to_/tmp/sandbox"]
            }
        }
        resp = await client.post(f"{URL}/forensics", json=payload)
        print(f"[HACKER] Exfiltration attempt sent. Server Response: {resp.status_code}", flush=True)
    print("[HACKER] Mirror Trap detected. Behavioral genome captured by Aegis. Attack neutralized.")

async def run_simulation():
    print("=== AEGIS MASTER INVASION SIMULATOR STARTED ===")
    print("Recording starts in 5 seconds...")
    await asyncio.sleep(5)
    
    await phase_1_stealth()
    await asyncio.sleep(45) # Stealth narration window
    
    await phase_2_surge()
    await asyncio.sleep(75) # Swarm/Mirror Trap narration window
    
    await phase_3_exfiltration()
    print("\n=== SIMULATION COMPLETE: HEROIC DEFENSE SHOWCASED ===")

if __name__ == "__main__":
    asyncio.run(run_simulation())
