# API Overview

## Auth

- `POST /api/auth/login`
- `GET /api/auth/me`

## Host Bridge

- `GET /api/host-bridge/bootstrap`
- `POST /api/host-bridge/telemetry`

## Agent Runtime

- `POST /api/agent/heartbeat`
- `GET /api/agent/jobs/next`
- `POST /api/agent/jobs/{job_id}/status`

## Core Routes

- `GET /health`
- `GET /api/overview`
- `GET /api/shares`
- `POST /api/shares`
- `GET /api/devices`
- `POST /api/devices`
- `GET /api/jobs`
- `POST /api/jobs`
- `GET /api/policies`
- `POST /api/policies`
- `GET /api/packages`
- `POST /api/packages`

## Current Role of the API

The API is now a persistent control plane backed by PostgreSQL. It stores:

- users and roles
- shares mapped to real Windows paths
- policies
- packages
- devices
- jobs

It does not move your shared files into the database or into Docker-managed storage.

## Next Expansion

- signed enrollment keys instead of bootstrap token
- execution receipts
- throughput and timing telemetry
- install command recipes and execution policies
