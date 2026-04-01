# Architecture Decisions

## ADR-001

The product is local-first and LAN-oriented. Internet exposure is not required for the first release.

## ADR-002

Direct SMB sharing is not the only access mechanism. The product uses a controlled access plane.

## ADR-003

`SFTPGo` is the primary file access and policy-capable service for the first executable version.

## ADR-004

Windows `install-only` behavior will be implemented through a future agent, not through plain file shares.

## ADR-005

The project runs in a Docker stack isolated from the current `sharoobi` services.

## ADR-006

Shared content remains in its original Windows paths such as `H:\` or any exact folder chosen by the operator. The platform manages metadata, access policy, and orchestration around those paths.

## ADR-007

Docker containers do not own the Windows file roots directly. A native Windows Host Bridge layer is responsible for validating paths, scanning local state, and publishing SMB shares safely.
