# Start backend (FastAPI on :8000) and frontend (Vite on :5173) together. Windows.
# Uses uv when it is installed, otherwise the active Python (e.g. a venv made with pip).
# No --reload: on Windows its restart signal can hang the old worker, which keeps serving
# stale code. Restart this script after backend changes (it also ends live games).
$env:PYTHONUTF8 = "1"
$root = $PSScriptRoot
$serve = "-m", "uvicorn", "aiplays.main:app", "--port", "8000", "--timeout-graceful-shutdown", "3"
if (Get-Command uv -ErrorAction SilentlyContinue) {
    $api = Start-Process -PassThru -NoNewWindow uv -ArgumentList (@("run", "python") + $serve) -WorkingDirectory $root
} else {
    $api = Start-Process -PassThru -NoNewWindow python -ArgumentList $serve -WorkingDirectory $root
}
try {
    Set-Location "$root\frontend"
    if (-not (Test-Path node_modules)) { npm install }
    npm run dev
} finally {
    Stop-Process -Id $api.Id -Force -ErrorAction SilentlyContinue
}
