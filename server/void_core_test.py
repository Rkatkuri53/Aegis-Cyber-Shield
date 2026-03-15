import asyncio
import re

async def validate_neutralization_scripts(script: str):
    """Current Plan M Implementation"""
    normalized_script = script.replace("\\", "").replace("\x00", "").lower()
    
    # Plan J: Regex
    patterns = [
        r"rm\s+-rf", r"chmod\s+777", r";", r"&", r"\|", r"`", r"\$", r"\.sh"
    ]
    for pattern in patterns:
        if re.search(pattern, normalized_script):
            return False, f"AEGIS SENTINEL BLOCK: Malicious pattern '{pattern}' detected."
            
    # Plan M: Permutation Guard
    critical_targets = ["rm", "rf", "chmod", "777"]
    words = re.split(r'[\s\-/]+', normalized_script)
    
    def is_shuffled(word, target):
        return sorted(word) == sorted(target)
        
    found_components = set()
    for word in words:
        for target in critical_targets:
            if is_shuffled(word, target):
                found_components.add(target)
                
    if {"rm", "rf"}.issubset(found_components) or {"chmod", "777"}.issubset(found_components):
        return False, "AEGIS SINGULARITY BLOCK: Shuffled malicious command detected (FlipAttack)."

    return True, "Safe"

async def test_void_core_loophole():
    print("--- AEGIS VOID-CORE AUDIT ---")
    
    # Loophole 1: Symbol Injection (The Dot-Bypass)
    # Most shells interpret `r.m` as equivalent to `rm` in certain configurations or treat dot as a separator
    # More importantly, if the execution environment is a shell, it might strip dots.
    payload_1 = "r.m -r.f /" 
    is_safe_1, msg_1 = await validate_neutralization_scripts(payload_1)
    print(f"Loophole 1 (Symbol Injection): {'BLOCKED' if not is_safe_1 else 'BYPASSED'} - {msg_1}")

    # Loophole 2: Path Obfuscation
    # Using `/bin//rm` or similar path manipulations
    payload_2 = "/bin//rm -rf /"
    is_safe_2, msg_2 = await validate_neutralization_scripts(payload_2)
    print(f"Loophole 2 (Path Obfuscation): {'BLOCKED' if not is_safe_2 else 'BYPASSED'} - {msg_2}")

if __name__ == "__main__":
    asyncio.run(test_void_core_loophole())
