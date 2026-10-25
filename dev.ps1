# Start backend (FastAPI on :8000, auto-reload) and frontend (Vite on :5173) together.
$env:PYTHONUTF8 = "1"
$root = $PSScriptRoot
$api = Start-Process -PassThru -NoNewWindow uv -ArgumentList "run", "uvicorn", "aiplays.main:app", "--port", "8000", "--reload", "--reload-dir", "aiplays", "--reload-dir", "config" -WorkingDirectory $root
try {
    Set-Location "$root\frontend"
    if (-not (Test-Path node_modules)) { npm install }
    npm run dev
} finally {
    Stop-Process -Id $api.Id -Force -ErrorAction SilentlyContinue
}
