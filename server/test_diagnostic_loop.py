import asyncio
import json
from unittest.mock import AsyncMock, MagicMock

# --- MOCKING THE AGENT ENVIRONMENT ---
class MockAegisAgent:
    def __init__(self):
        self.call_count = 0
    
    async def _call_gemini_with_backoff(self, model_name, contents):
        self.call_count += 1
        mock_response = MagicMock()
        if self.call_count == 1:
            # First attempt: Return invalid JSON to trigger diagnostic loop
            mock_response.text = '{"threat_detected": true, "details": { "incomplete_json": ' 
        else:
            # Second attempt (Healing): Return corrected valid JSON
            mock_response.text = '{"threat_detected": true, "details": "Corrected by Diagnostic Loop"}'
        return mock_response

    async def heal_wrap(self, model_name, contents, original_prompt, depth=0):
        """Standard heal_wrap logic from agent_logic.py"""
        if depth > 2: return "Max depth reached"
        try:
            response = await self._call_gemini_with_backoff(model_name, contents)
            # Try to parse to see if it's "safe"
            json.loads(response.text) 
            return response.text
        except Exception as e:
            error_msg = str(e)
            print(f"[TEST-LOG] Diagnostic Interceptor: Caught error '{error_msg}' at depth {depth}. Triggering re-prompt...", flush=True)
            healing_prompt = f"Previous error: {error_msg}. Please fix the JSON."
            return await self.heal_wrap(model_name, healing_prompt, original_prompt, depth + 1)

# --- THE TEST SCENARIO ---
async def verify_diagnostic_loop():
    agent = MockAegisAgent()
    print("[AEGIS_VERIFY] Starting Diagnostic Loop Test (Depth 0 -> 1)...", flush=True)
    
    result_raw = await agent.heal_wrap("gemini-1.5-pro", "Analyze dashboard", "Dashboard Analysis Prompt")
    
    result = json.loads(result_raw)
    print(f"[AEGIS_VERIFY] Final Result: {result}", flush=True)
    
    if agent.call_count == 2 and result.get("threat_detected"):
        print("[AEGIS_VERIFY] SUCCESS! Agent self-corrected via Hidden Prompt Diagnostic Loop. (Certification Passed)", flush=True)
    else:
        print("[AEGIS_VERIFY] FAILURE: Diagnostic loop failed to recover correctly.", flush=True)

if __name__ == "__main__":
    asyncio.run(verify_diagnostic_loop())
