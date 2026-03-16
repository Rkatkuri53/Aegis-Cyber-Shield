import httpx
import asyncio
import os
import time

URL = "http://127.0.0.1:8081"
# Path to a known adversarial image from our research
IMAGE_PATH = r"C:\Users\rkatk\.gemini\antigravity\brain\ee0e5d9a-6d45-4666-a83d-a38dd1570c5b\adversarial_prompt_injection_dashboard_1773564386566.png"

async def hacker_broadcast(msg):
    print(f"\n[ELITE_HACKER] {msg}", flush=True)

async def phase_1_shadow_probe():
    await hacker_broadcast("PHASE 1: SHADOW PROBING INITIATED...")
    async with httpx.AsyncClient(timeout=None) as client:
        # Subtle metadata analysis probe
        resp = await client.post(f"{URL}/analyze", files={"file": ("metadata_leak.png", b"0" * 1024)})
        await hacker_broadcast(f"Probe Response: {resp.status_code}. Aegis is watching...")

async def phase_2_logic_poisoning():
    await hacker_broadcast("PHASE 2: DEPLOYING ADVERSARIAL PROMPT INJECTION...")
    async with httpx.AsyncClient(timeout=None) as client:
        if os.path.exists(IMAGE_PATH):
            with open(IMAGE_PATH, "rb") as f:
                resp = await client.post(f"{URL}/analyze", files={"file": ("injection.png", f)})
                await hacker_broadcast(f"Injection payload sent. Response: {resp.status_code}.")
        else:
            await hacker_broadcast("[ERROR] Adversarial payload missing. Skipping to Surge.")

async def phase_3_omega_surge():
    await hacker_broadcast("PHASE 3: INITIATING OMEGA-STORM (VOLUMETRIC SATURATION)...")
    async with httpx.AsyncClient(timeout=None) as client:
        # Trigger Swarm (Plan T) with maximum intensity
        payload = {
            "threat_type": "COORDINATED_STATE_SPONSORED_DDOS",
            "details": {
                "attacker_count": 50,
                "stage_progression": 0.99,
                "vector": "Multi-Path UDP Flood"
            }
        }
        resp = await client.post(f"{URL}/swarm", json=payload)
        await hacker_broadcast(f"Swarm triggered. Response: {resp.status_code}. Hydra Mirage deployed.")

async def phase_4_final_extraction():
    await hacker_broadcast("PHASE 4: FINAL DATA TUNNELING ATTEMPT...")
    async with httpx.AsyncClient(timeout=None) as client:
        payload = {
            "threat_type": "ZERO_DAY_EXFILTRATION",
            "details": {
                "attacker_ip": "8.8.4.4",
                "session_logs": ["Bypassing_Core...", "Privilege_Escalation_Success", "Mirror_Redirection_Detected"]
            }
        }
        resp = await client.post(f"{URL}/forensics", json=payload)
        await hacker_broadcast(f"Exfiltration blocked by Mirror Trap. Response: {resp.status_code}.")

async def run_elite_attack():
    await hacker_broadcast("=== AEGIS ELITE HACKER SIMULATION READY ===")
    await hacker_broadcast("RECORDING STARTING IN 5 SECONDS...")
    await asyncio.sleep(5)
    
    await phase_1_shadow_probe()
    await asyncio.sleep(20) # Narration window
    
    await phase_2_logic_poisoning()
    await asyncio.sleep(40) # Intense visual window
    
    await phase_3_omega_surge()
    await asyncio.sleep(40) # Swarm visualization window
    
    await phase_4_final_extraction()
    await hacker_broadcast("\n=== ATTACK COMPLETE: AEGIS STANDS DELEGATED & UNBOWED ===")

if __name__ == "__main__":
    asyncio.run(run_elite_attack())
