$ErrorActionPreference = "Stop"

param(
  [string]$ProjectRoot = "H:\Sharoobi_FileShare"
)

$scriptPath = Join-Path $ProjectRoot "agent\windows-agent\host-bridge.ps1"
$taskName = "Sharoobi Host Bridge"
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`" -ApplySmb"
$trigger = New-ScheduledTaskTrigger -AtStartup
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "Runs the Sharoobi Host Bridge on startup." -Force | Out-Null
Write-Host "Scheduled task registered: $taskName"
