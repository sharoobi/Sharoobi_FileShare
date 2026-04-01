$projectRoot = Split-Path -Parent $PSScriptRoot | Split-Path -Parent

Write-Host "Validating compose..."
docker compose -f (Join-Path $projectRoot "docker-compose.yml") config | Out-Null

Write-Host "Validating Python syntax..."
python -m compileall `
  (Join-Path $projectRoot "backend\api\app") `
  (Join-Path $projectRoot "backend\worker") | Out-Null

Write-Host "Validating admin shell JavaScript..."
node --check (Join-Path $projectRoot "frontend\admin-web\app.js") | Out-Null

Write-Host "Validating PowerShell automation..."
$null = $null
$errors = $null
[System.Management.Automation.Language.Parser]::ParseFile((Join-Path $projectRoot "agent\windows-agent\host-bridge.ps1"), [ref]$null, [ref]$errors) | Out-Null
if ($errors.Count -gt 0) { throw "host-bridge.ps1 failed PowerShell parsing." }
$errors = $null
[System.Management.Automation.Language.Parser]::ParseFile((Join-Path $projectRoot "agent\windows-agent\agent.ps1"), [ref]$null, [ref]$errors) | Out-Null
if ($errors.Count -gt 0) { throw "agent.ps1 failed PowerShell parsing." }

Write-Host "Validation completed"
