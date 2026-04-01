# Operations Runbook

## Bootstrap

```powershell
Copy-Item .env.example .env
.\infra\scripts\bootstrap-storage.ps1
docker compose up --build -d
```

## Main Endpoints

- Admin shell: `http://localhost:18080`
- API docs: `http://localhost:18080/docs`
- SFTPGo admin/client: `http://localhost:19080`

## Stop

```powershell
docker compose down
```

## Reset Local Data

Be careful. This removes local metadata volumes:

```powershell
docker compose down -v
```

## Runtime Paths

- Runtime agent drop: `storage/runtime/agent-drop`
- Host bridge cache: `storage/runtime/bridge-cache`
- Exports: `storage/runtime/exports`
- Logs: `storage/logs`
- SFTPGo state: `storage/sftpgo`

## Important Architecture Rule

The files you want to share stay in their original Windows locations such as `H:\`, `H:\Office\2024`, or any exact folder you register.

Docker stores metadata and control-plane state only. Real path validation, SMB publishing, and native Windows access are handled by the future Host Bridge layer.
