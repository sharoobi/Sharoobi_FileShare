$root = "H:\Sharoobi_FileShare\storage"
$folders = @(
  "runtime\agent-drop",
  "runtime\bridge-cache",
  "runtime\exports",
  "logs\access",
  "logs\jobs",
  "logs\audit",
  "db_backups",
  "sftpgo\data"
)

foreach ($folder in $folders) {
  $path = Join-Path $root $folder
  New-Item -ItemType Directory -Path $path -Force | Out-Null
}

Write-Host "Runtime layout is ready at $root"
