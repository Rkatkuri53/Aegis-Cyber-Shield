# Aegis Workspace Cleanup Script
# Stops processes and clears caches to resolve Pyre2 crash loops

Write-Host "Stopping Aegis processes (Python/Node)..." -ForegroundColor Cyan
Stop-Process -Name "python" -ErrorAction SilentlyContinue
Stop-Process -Name "node" -ErrorAction SilentlyContinue

Write-Host "Clearing cache directories (.pyre, .antigravity, __pycache__)..." -ForegroundColor Yellow
$dirs = @(".pyre", ".antigravity", "server/__pycache__", "client/__pycache__")
foreach ($dir in $dirs) {
    if (Test-Path $dir) {
        Remove-Item -Path $dir -Recurse -Force
        Write-Host "Removed: $dir"
    }
}

Write-Host "Resetting language server..." -ForegroundColor Green
# In VS Code, this usually happens automatically when files change or via command palette, 
# but clearing the .pyre/ directory forces a fresh index on restart.

Write-Host "Workspace Stabilized." -ForegroundColor Cyan
