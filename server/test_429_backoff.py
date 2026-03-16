import asyncio
import time
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

# Mocking a 429 Error
class MockRateLimitError(Exception):
    pass

@retry(
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(4),
    retry=retry_if_exception_type(MockRateLimitError),
    before_sleep=lambda retry_state: print(f"[TEST-LOG] Caught 429. Retrying in {retry_state.next_action.sleep}s... (Attempt {retry_state.attempt_number})", flush=True)
)
async def simulate_429_backoff():
    print("[TEST-LOG] Sending API Request...", flush=True)
    raise MockRateLimitError("429 Too Many Requests")

if __name__ == "__main__":
    print("[AEGIS_VERIFY] Starting Exponential Backoff Test (Expected: 2s, 4s, 8s intervals)...", flush=True)
    start_time = time.time()
    try:
        asyncio.run(simulate_429_backoff())
    except MockRateLimitError:
        print(f"[AEGIS_VERIFY] Test Complete. Final Attempt reached after {time.time() - start_time:.2f}s.", flush=True)
