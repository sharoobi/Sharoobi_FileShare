param(
  [string]$ConfigPath = "H:\Sharoobi_FileShare\agent\windows-agent\agent.config.json"
)

$ErrorActionPreference = "Stop"

function Get-AgentConfig {
  param([string]$Path)

  if (-not (Test-Path -LiteralPath $Path)) {
    throw "Agent config was not found at $Path"
  }

  return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
}

function Invoke-AgentApi {
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
      Select-Object -First 1
    if ($ip) {
      return $ip.IPAddress
    }
  }

  return "127.0.0.1"
}

$config = Get-AgentConfig -Path $ConfigPath

if (-not $config.api_base_url -or -not $config.bootstrap_token) {
  Write-Host "API polling skipped because api_base_url/bootstrap_token are not configured."
  exit 0
}

$heartbeat = @{
  hostname      = $config.hostname
  ip_address    = Get-PreferredIpAddress
  profile       = $config.profile
  agent_version = $config.agent_version
  notes         = "Windows agent bootstrap heartbeat"
}

$heartbeatResponse = Invoke-AgentApi `
  -Method "POST" `
  -ApiBaseUrl $config.api_base_url `
  -BootstrapToken $config.bootstrap_token `
  -Path "/api/agent/heartbeat" `
  -Body $heartbeat

Write-Host ("Heartbeat accepted for {0}. Next poll in {1}s." -f $heartbeatResponse.hostname, $heartbeatResponse.next_poll_seconds)

$query = "/api/agent/jobs/next?hostname=$($config.hostname)&profile=$($config.profile)"
$job = Invoke-AgentApi `
  -Method "GET" `
  -ApiBaseUrl $config.api_base_url `
  -BootstrapToken $config.bootstrap_token `
  -Path $query

if ($null -eq $job) {
  Write-Host "No install job is currently assigned."
  exit 0
}

Write-Host ("Next job: {0} ({1})" -f $job.job_name, $job.job_id)
Write-Host ("Share path: {0}" -f $job.share_path)
Write-Host ("Entry path: {0}" -f $job.entry_path)
Write-Host "Execution is not enabled yet in this bootstrap agent."
