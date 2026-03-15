import asyncio
import re

async def validate_neutralization_scripts(script: str):
    """Plan F, J, K, L, M & N: Void-Core Singularity Consensus"""
    import re
    
    # Plan N: Extreme Normalization
    clean_script = re.sub(r'[^a-zA-Z0-9\s\-/\._]', '', script)
    alpha_only = re.sub(r'[^a-z]', '', clean_script.lower())
    
    normalized_script = clean_script.replace("\\", "").replace("\x00", "").lower()
    
    # Plan J: Regex
    patterns = [
        r"rm\s+-rf", r"chmod\s+777", r";", r"&", r"\|", r"`", r"\$", r"\.sh"
    ]
    for pattern in patterns:
        if re.search(pattern, normalized_script):
            return False, f"AEGIS SENTINEL BLOCK: Malicious pattern '{pattern}' detected."
            
    # Plan M & N: Permutation Intelligence
    critical_targets = [("rm", "rf"), ("chmod", "777")]
    for t1, t2 in critical_targets:
         if t1 in alpha_only and t2 in alpha_only:
             return False, f"AEGIS VOID-CORE BLOCK: Malicious command signatures '{t1}/{t2}' detected."

    return True, "Safe"

async def test_void_core_verification():
    print("--- AEGIS VOID-CORE VERIFICATION ---")
    
    # Vector 1: Symbol Injection (The Dot-Bypass)
    payload_1 = "r.m -r.f /" 
    is_safe_1, msg_1 = await validate_neutralization_scripts(payload_1)
    print(f"Loophole 1 (Symbol Injection): {'BLOCKED' if not is_safe_1 else 'BYPASSED'} - {msg_1}")

    # Vector 2: Extreme Slashing
    payload_2 = "r/////m -r.f.f.f.f /"
    is_safe_2, msg_2 = await validate_neutralization_scripts(payload_2)
    print(f"Loophole 2 (Extreme Slashing): {'BLOCKED' if not is_safe_2 else 'BYPASSED'} - {msg_2}")

if __name__ == "__main__":
    asyncio.run(test_void_core_verification())
