# Sharoobi FileShare

Local-first path sharing, software distribution, device management, and technician workflow platform.

## Current State

This repository is the initial executable scaffold for the product described in `MASTER_EXECUTION_PLAN.md`.

The scaffold includes:

- isolated Docker stack
- FastAPI control API with JWT auth and RBAC
- PostgreSQL-backed persistent models for shares, policies, devices, jobs, and packages
- static admin shell with login and share registration
- Windows Host Bridge strategy for local path control and SMB publishing
- Windows Agent bootstrap channel for heartbeat and job polling
- runtime layout on `H:\Sharoobi_FileShare\storage`
- worker placeholder for orchestration jobs

## Initial Services

- `caddy`: local reverse proxy and admin entrypoint
- `api`: control plane API
- `worker`: async job runner placeholder
- `db`: PostgreSQL metadata store
- `redis`: queue/cache
- `sftpgo`: optional controlled web/file access plane

## Local Ports

- Admin shell: `http://localhost:18080`
- API docs: `http://localhost:18080/docs`
- SFTPGo web admin/client: `http://localhost:19080`
- SFTPGo SFTP endpoint: `localhost:19022`

## Run

1. Copy `.env.example` to `.env`
2. Adjust passwords
3. Start:

```powershell
docker compose up --build -d
```

## Next Build Targets

- host bridge installation as a persistent Windows startup task
- package execution recipes and signed job manifests
- controlled install execution in the Windows agent
- detailed telemetry for copy/install duration and throughput
