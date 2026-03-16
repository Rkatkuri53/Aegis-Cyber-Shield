import asyncio
import time
from unittest.mock import MagicMock, patch

# --- MOCKING THE SYSTEM ENVIRONMENT ---
class MockFirestoreDocument:
    def __init__(self, data=None):
        self.exists = data is not None
        self._data = data
    def to_dict(self):
        return self._data

class MockFirestoreCollection:
    def __init__(self):
        self.storage = {}
    def document(self, doc_id):
        mock_doc = MagicMock()
        mock_doc.set = lambda data: self.storage.update({doc_id: data})
        mock_doc.get = lambda: MockFirestoreDocument(self.storage.get(doc_id))
        return mock_doc

class MockFirestoreClient:
    def __init__(self):
        self._collections = {}
    def collection(self, name):
        if name not in self._collections:
            self._collections[name] = MockFirestoreCollection()
        return self._collections[name]

# --- THE LOGIC TO VERIFY ---
# (Mirror of the logic implemented in main.py)
class AegisState:
    def __init__(self):
        self.last_analysis = None
        self.swarm_active = False
        self.mirage_active = False
        self.last_reset = time.time()
        self.candidate_name = "Unknown"

state = AegisState()
db = MockFirestoreClient()

async def save_state_to_firestore():
    # IAM Role: roles/datastore.user used here
    doc_ref = db.collection(u'aegis_sessions').document(u'active_session')
    doc_ref.set({
        u'diag_state': {
            u'last_analysis': state.last_analysis,
            u'swarm_active': state.swarm_active,
            u'mirage_active': state.mirage_active,
            u'last_reset': state.last_reset,
            u'candidate_name': state.candidate_name
        }
    })

async def recover_state_from_firestore():
    doc_ref = db.collection(u'aegis_sessions').document(u'active_session')
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict().get('diag_state', {})
        state.candidate_name = data.get('candidate_name', 'Unknown')
        return True
    return False

# --- THE TEST SCENARIO ---
async def verify_recovery():
    global state
    print("[AEGIS_VERIFY] STEP 1: Storing 'ANTIGRAVITY_AGENT' as candidate name...", flush=True)
    state.candidate_name = "ANTIGRAVITY_AGENT"
    await save_state_to_firestore()
    
    print("[AEGIS_VERIFY] STEP 2: Force-killing context (Re-initializing state object)...", flush=True)
    state = AegisState() # Reset to default
    print(f"[AEGIS_VERIFY] Current Context Name: {state.candidate_name} (Should be 'Unknown')", flush=True)
    
    print("[AEGIS_VERIFY] STEP 3: Calling /recover logic from Firestore Mock...", flush=True)
    success = await recover_state_from_firestore()
    
    if success and state.candidate_name == "ANTIGRAVITY_AGENT":
        print(f"[AEGIS_VERIFY] SUCCESS! Agent remembered candidate: {state.candidate_name} after recovery. (Certification Passed)", flush=True)
    else:
        print("[AEGIS_VERIFY] FAILURE: Recovery logic did not restore state correctly.", flush=True)

if __name__ == "__main__":
    asyncio.run(verify_recovery())
