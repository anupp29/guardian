# Start ADK Web Server on port 3000 (PowerShell)

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $scriptPath "..")
adk web --port 3000





