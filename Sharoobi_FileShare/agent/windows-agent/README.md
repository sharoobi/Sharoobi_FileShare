# Windows Host Bridge And Agent Plan

This folder now represents two native Windows responsibilities:

1. `Host Bridge`
   - validates local Windows paths
   - scans accessibility and drive usage
   - publishes or removes SMB shares according to API policy
   - reports share status back to the control API
2. `Windows Agent`
   - enrolls devices
   - runs controlled install jobs
   - reports execution results, duration, and status

## Why It Exists

The product must share files already present on the same Windows machine. That means Docker should not become the owner of `H:\` or any other business path.

Native Windows operations stay here so the platform can work with:

- `H:\`
- exact subfolders like `H:\Office\2024`
- existing NTFS permissions
- Windows SMB publishing
- future install-only execution

## Planned Runtime Features

- runs as a Windows service or scheduled service host
- local cache folder for manifests only
- no forced file re-upload into the platform
- signed job manifests
- silent install support
- cleanup policy support
- share publish and revoke workflow

## Current Bootstrap Files

- `host-bridge.ps1`
  - pulls share plans from the API
  - validates local paths
  - can create or remove SMB shares
  - reports telemetry back to the API
- `register-host-bridge-task.ps1`
  - registers a startup scheduled task for the bridge
- `agent.ps1`
  - sends heartbeat
  - polls the next install job
  - prints the manifest without executing it yet
