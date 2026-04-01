param(
  [string]$ConfigPath = "H:\Sharoobi_FileShare\agent\windows-agent\host-bridge.config.json",
  [switch]$ApplySmb,
  [switch]$DeepScan,
  [switch]$WhatIf
)

$ErrorActionPreference = "Stop"

function Get-BridgeConfig {
  param([string]$Path)

  if (-not (Test-Path -LiteralPath $Path)) {
    throw "Host bridge config was not found at $Path"
  }

  return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
}

function Invoke-BridgeApi {
  param(
    [ValidateSet("GET", "POST")]
    [string]$Method,
    [string]$ApiBaseUrl,
    [string]$BootstrapToken,
    [string]$Path,
    [object]$Body = $null
  )

  $headers = @{
    Authorization = "Bearer $BootstrapToken"
  }

  $params = @{
    Method      = $Method
    Uri         = ($ApiBaseUrl.TrimEnd("/") + $Path)
    Headers     = $headers
    ErrorAction = "Stop"
  }

  if ($null -ne $Body) {
    $params["ContentType"] = "application/json"
    $params["Body"] = ($Body | ConvertTo-Json -Depth 8)
  }

  return Invoke-RestMethod @params
}

function Get-PreferredIpAddress {
  $routes = Get-NetRoute -AddressFamily IPv4 -DestinationPrefix "0.0.0.0/0" -ErrorAction SilentlyContinue |
    Sort-Object -Property RouteMetric, InterfaceMetric

  foreach ($route in $routes) {
    $ip = Get-NetIPAddress -AddressFamily IPv4 -InterfaceIndex $route.InterfaceIndex -ErrorAction SilentlyContinue |
      Where-Object { $_.IPAddress -notlike "169.254*" } |
      Sort-Object -Property SkipAsSource |
      Select-Object -First 1
    if ($ip) {
      return $ip.IPAddress
    }
  }

  return "127.0.0.1"
}

function Get-ShareReadPrincipal {
  param([bool]$AllowGuest)

  if ($AllowGuest) {
    return "Everyone"
  }

  return "Authenticated Users"
}

function Get-PathScanMetrics {
  param(
    [string]$SourcePath,
    [bool]$EnableDeepScan
  )

  $exists = Test-Path -LiteralPath $SourcePath
  $kind = "missing"
  $fileCount = $null
  $sizeBytes = $null

  if ($exists) {
    $item = Get-Item -LiteralPath $SourcePath
    $kind = if ($item.PSIsContainer) { "directory" } else { "file" }

    if ($EnableDeepScan) {
      if ($item.PSIsContainer) {
        $measure = Get-ChildItem -LiteralPath $SourcePath -File -Recurse -Force -ErrorAction SilentlyContinue |
          Measure-Object -Property Length -Sum
        $fileCount = [int]$measure.Count
        $sizeBytes = if ($null -ne $measure.Sum) { [int64]$measure.Sum } else { 0 }
      }
      else {
        $fileCount = 1
        $sizeBytes = [int64]$item.Length
      }
    }
  }

  return [pscustomobject]@{
    path_exists = [bool]$exists
    path_kind   = $kind
    file_count  = $fileCount
    size_bytes  = $sizeBytes
  }
}

function Sync-SmbShare {
  param(
    [pscustomobject]$Share,
    [bool]$PathExists,
    [switch]$ApplyChanges,
    [switch]$DryRun
  )

  $shareName = $Share.smb_share_name
  $shouldPublish = [bool]($Share.is_enabled -and $Share.expose_via_smb -and $PathExists)
  $existing = Get-SmbShare -Name $shareName -ErrorAction SilentlyContinue
  $message = "No SMB action required."
  $published = $false

  if (-not $shouldPublish) {
    if ($existing) {
      $message = "SMB share should be removed."
      if ($ApplyChanges -and -not $DryRun) {
        Remove-SmbShare -Name $shareName -Force
      }
    }
    else {
      $message = "SMB share not published by policy."
    }
    return [pscustomobject]@{
      message       = $message
      smb_published = $false
    }
  }

  $readPrincipal = Get-ShareReadPrincipal -AllowGuest ([bool]$Share.allow_guest)
  $published = $true

  if (-not $existing) {
    $message = "SMB share should be created."
    if ($ApplyChanges -and -not $DryRun) {
      New-SmbShare -Name $shareName -Path $Share.source_path -ReadAccess $readPrincipal | Out-Null
      $message = "SMB share created."
    }
  }
  elseif ($existing.Path -ne $Share.source_path) {
    $message = "SMB share path drift detected and should be recreated."
    if ($ApplyChanges -and -not $DryRun) {
      Remove-SmbShare -Name $shareName -Force
      New-SmbShare -Name $shareName -Path $Share.source_path -ReadAccess $readPrincipal | Out-Null
      $message = "SMB share recreated with the current path."
    }
  }
  else {
    $message = "SMB share already aligned."
  }

  return [pscustomobject]@{
    message       = $message
    smb_published = $published
  }
}

function Get-SharePlans {
  param([pscustomobject]$Config)

  if ($Config.api_base_url -and $Config.bootstrap_token) {
    $bootstrap = Invoke-BridgeApi `
      -Method "GET" `
      -ApiBaseUrl $Config.api_base_url `
      -BootstrapToken $Config.bootstrap_token `
      -Path "/api/host-bridge/bootstrap"
    if ($bootstrap.node_name) {
      $Config.node_name = $bootstrap.node_name
    }
    return $bootstrap.shares
  }

  return $Config.shares
}

$config = Get-BridgeConfig -Path $ConfigPath
$plans = @(Get-SharePlans -Config $config)
$results = @()

Write-Host "Host Bridge loaded for node $($config.node_name)"
Write-Host ("Share plans loaded: {0}" -f $plans.Count)

foreach ($share in $plans) {
  $scan = Get-PathScanMetrics -SourcePath $share.source_path -EnableDeepScan:$DeepScan
  $smb = Sync-SmbShare -Share $share -PathExists $scan.path_exists -ApplyChanges:$ApplySmb -DryRun:$WhatIf

  $accessState = if (-not $scan.path_exists) {
    "path-missing"
  }
  elseif ($share.expose_via_smb) {
    if ($ApplySmb) { "smb-synced" } else { "smb-plan-ready" }
  }
  else {
    "path-validated"
  }

  $message = $smb.message
  Write-Host ("[{0}] {1} -> {2}" -f $share.slug, $share.source_path, $accessState)

  $results += [pscustomobject]@{
    slug           = $share.slug
    source_path    = $share.source_path
    path_exists    = $scan.path_exists
    path_kind      = $scan.path_kind
    file_count     = $scan.file_count
    size_bytes     = $scan.size_bytes
    access_state   = $accessState
    message        = $message
    smb_share_name = $share.smb_share_name
    smb_published  = $smb.smb_published
  }
}

if ($config.api_base_url -and $config.bootstrap_token) {
  $payload = @{
    node_name     = $config.node_name
    agent_version = "host-bridge-0.2.0"
    ip_address    = Get-PreferredIpAddress
    shares        = $results
  }

  $response = Invoke-BridgeApi `
    -Method "POST" `
    -ApiBaseUrl $config.api_base_url `
    -BootstrapToken $config.bootstrap_token `
    -Path "/api/host-bridge/telemetry" `
    -Body $payload

  Write-Host ("Telemetry submitted. Updated shares: {0}" -f $response.updated)
}
else {
  Write-Host "API sync skipped because api_base_url/bootstrap_token are not configured."
}

Write-Host "Host Bridge execution finished."
