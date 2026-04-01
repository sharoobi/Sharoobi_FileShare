# SMB Strategy

## Goal

Expose only approved Windows paths over SMB, with policy-driven naming and visibility, without sharing entire drives blindly.

## Rules

- Never share an entire drive just because it exists.
- Publish only paths that are registered in the API as `shares`.
- Let policy decide whether SMB is allowed.
- Prefer read-only SMB unless a specific technician workflow requires write access.
- Keep guest access isolated to separate shares with separate policies.

## Flow

1. Admin registers a share in the control plane.
2. Policy marks whether SMB exposure is allowed.
3. Windows Host Bridge pulls the bootstrap plan from `GET /api/host-bridge/bootstrap`.
4. Host Bridge validates the local path.
5. Host Bridge creates or updates the SMB share name on Windows.
6. Bridge reports publish state back to the API through `POST /api/host-bridge/telemetry`.

## Why This Matters

Your business need is to serve files already on the current device. Native SMB must stay a Windows concern so the platform can safely work with existing NTFS paths and permissions.
