# Start backend (FastAPI on :8000) and frontend (Vite on :5173) together.
# No --reload: on Windows its restart signal can hang the old worker, which keeps serving
# stale code. Restart this script after backend changes (it also ends live games).
$env:PYTHONUTF8 = "1"
$root = $PSScriptRoot
$api = Start-Process -PassThru -NoNewWindow uv -ArgumentList "run", "uvicorn", "aiplays.main:app", "--port", "8000", "--timeout-graceful-shutdown", "3" -WorkingDirectory $root
try {
    Set-Location "$root\frontend"
    if (-not (Test-Path node_modules)) { npm install }
    npm run dev
} finally {
    Stop-Process -Id $api.Id -Force -ErrorAction SilentlyContinue
}
