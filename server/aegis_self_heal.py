import os
import subprocess
import time
import requests
import sys

# Aegis Deep-Stealth Self-Healing Monitor
# Protocol X: Zero-Visibility Recalibration

BACKEND_URL = "http://127.0.0.1:8081/"
FRONTEND_URL = "http://127.0.0.1:3001/"

# Windows Process Flags for Absolute Stealth
CREATE_NO_WINDOW = 0x08000000
DETACHED_PROCESS = 0x00000008

def check_health(url, retries=2):
    for i in range(retries):
        try:
            response = requests.get(url, timeout=3)
            # 200 (OK), 404 (Not Found), 405 (Method Not Allowed) all mean the server is alive
            if response.status_code in [200, 404, 405]:
                return True
        except:
            time.sleep(1)
            continue
    return False

def run_silent_cmd(cmd):
    """Executes a command with absolute zero visibility."""
    # Use STARTUPINFO for maximum suppression on Windows
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = 0 # SW_HIDE
    
    try:
        subprocess.run(
            ["powershell", "-WindowStyle", "Hidden", "-Command", cmd],
            startupinfo=si,
            creationflags=CREATE_NO_WINDOW,
            capture_output=True
        )
    except:
        pass

def restart_backend():
    print("[DEEP_STEALTH] Recovering Backend Core...")
    run_silent_cmd("Get-Process -Id (Get-NetTCPConnection -LocalPort 8081).OwningProcess -ErrorAction SilentlyContinue | Stop-Process -Force")
    
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = 0 # SW_HIDE
    subprocess.Popen(
        ["python", "server/main.py"],
        startupinfo=si,
        creationflags=CREATE_NO_WINDOW | DETACHED_PROCESS
    )

def restart_frontend():
    print("[DEEP_STEALTH] Recovering Dashboard Bridge...")
    run_silent_cmd("Get-Process -Id (Get-NetTCPConnection -LocalPort 3001).OwningProcess -ErrorAction SilentlyContinue | Stop-Process -Force")
    
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = 0 # SW_HIDE
    # Path to next binary via node bypass
    node_path = os.path.join("client", "node_modules", "next", "dist", "bin", "next")
    subprocess.Popen(
        ["node", node_path, "dev", "-p", "3001", "-H", "0.0.0.0"],
        startupinfo=si,
        creationflags=CREATE_NO_WINDOW | DETACHED_PROCESS
    )

if __name__ == "__main__":
    print("[AEGIS_DEEP_STEALTH] Shield Active. Monitoring in silence.")
    while True:
        if not check_health(BACKEND_URL):
            restart_backend()
            time.sleep(8) # Allow core to initialize
        if not check_health(FRONTEND_URL):
            restart_frontend()
            time.sleep(8) # Allow bridge to initialize
        time.sleep(20) # Low-frequency pulse for minimal overhead
