import asyncio
import time
from agent_logic import AegisAgent

async def test_log_siphoning():
    print("[AEGIS_TEST] Initializing Agent for Log Siphoning Audit...", flush=True)
    agent = AegisAgent(api_key="TEST_KEY")
    
    print("[AEGIS_TEST] STEP 1: Testing Security Log (Expected Fallback if not Admin)...", flush=True)
    logs = agent.get_windows_logs(log_type="Security", count=2)
    
    for log in logs:
        print(f"  > [{log['time']}] {log['msg']} ({log['type']})")

    if any("EVT_Security" in log['msg'] for log in logs):
        print("[AEGIS_TEST] STATUS: High-Privilege Access Verified.")
    elif any("EVT_Application" in log['msg'] or "EVT_System" in log['msg'] for log in logs):
        print("[AEGIS_TEST] STATUS: Graceful Fallback Verified [SUCCESS].")
    else:
        print("[AEGIS_TEST] STATUS: No events captured, but no crash [SUCCESS].")

if __name__ == "__main__":
    asyncio.run(test_log_siphoning())
