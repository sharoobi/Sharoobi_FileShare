$projectRoot = Split-Path -Parent $PSScriptRoot | Split-Path -Parent
Set-Location $projectRoot

if (-not (Test-Path ".env")) {
  Copy-Item ".env.example" ".env"
}

& (Join-Path $projectRoot "infra\scripts\bootstrap-storage.ps1")
docker compose up --build -d
