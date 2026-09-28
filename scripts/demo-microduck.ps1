param(
    [string]$PythonPath = "C:\Users\kevin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $PythonPath)) {
    throw "Python executable not found: $PythonPath"
}

Write-Host "[1/5] Configuration and hardware doctor"
& $PythonPath -m microduck_bringup --dry-run doctor

Write-Host "[2/5] Servo bus scan"
& $PythonPath -m microduck_bringup --dry-run scan

Write-Host "[3/5] Live state sample"
& $PythonPath -m microduck_bringup --dry-run monitor --samples 1 --interval 0

Write-Host "[4/5] Safety-limit rejection"
& $PythonPath -m microduck_bringup --dry-run safety-check --joint left_knee --target 999

Write-Host "[5/5] Emergency stop"
& $PythonPath -m microduck_bringup --dry-run estop --reason "demo complete"

Write-Host "MicroDuck Software Bring-up MVP v0.1 demo passed. Logs are in .\logs"

