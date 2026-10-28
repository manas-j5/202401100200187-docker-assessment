# FestPass Docker Assessment

## Assessment identity

- Name: Manas Swaroop
- Registration number: 202401100200187
- Calculated frontend port: 170 (`80 + 90`)
- Docker Hub username: `msmanas`
- GitHub repository: <https://github.com/manas-j5/202401100200187-docker-assessment>

## Current status

Stages 1 and 2 have been implemented and locally validated.
The official starter code referenced by the assessment (pages 4–8) was not
available, so `backend/app.py`, `frontend/index.html`, and `frontend/nginx.conf`
are clearly labeled minimal replacements rather than copied assessment starter
files.

The backend exposes `/api/health`, `/api/registrations`, and
`POST /api/registrations`. Stage 1 uses the required initial `python:3.9` base
image and pinned dependencies.

## Stage 1 commands

```powershell
docker build -t fest-backend:0.1 .\backend
docker run --name backend -p 170:5000 -e REGNO=8090 fest-backend:0.1
Invoke-WebRequest http://localhost:170/api/health
docker ps
docker logs backend
docker rm -f backend
```

The standalone health response is expected to report `"database": false` because
PostgreSQL is not connected during Stage 1.

## Stage 2 commands

Create `.env` locally from `.env.example`, set a private `POSTGRES_PASSWORD`,
then run:

```powershell
docker compose config
docker compose up -d --build
docker compose ps
docker compose logs db backend frontend
Invoke-WebRequest http://localhost:170/api/health
docker network inspect 202401100200187-docker-assessment_frontend-backend
docker network inspect 202401100200187-docker-assessment_backend-db
docker compose down
docker compose up -d
docker volume ls
```

The health response should report `"database": true` after PostgreSQL is ready.
Do not use `docker compose down -v` during the persistence test.

## Stage 3 status

The original `fest-backend:0.1` image was scanned and the full report is saved
at [reports/trivy-before.txt](./reports/trivy-before.txt). The hardened
`fest-backend:0.2` image was scanned and the full report is saved at
[reports/trivy-after.txt](./reports/trivy-after.txt).

| Image | Size | CRITICAL result |
|---|---:|---:|
| `fest-backend:0.1` | 412,104,981 bytes | Baseline report saved; formatted report has no machine-readable summary |
| `fest-backend:0.2` | 48,965,253 bytes | Gate failed: 7 CRITICAL vulnerabilities with available fixes |

The required gate was run with `--severity CRITICAL --ignore-unfixed
--exit-code 1` and returned exit code `1`. Further base-image remediation is
required before claiming a passing gate.

## Stages 4 and 5 status

The local release image was built and tagged as
`msmanas/fest-backend:1.0.0` and `msmanas/fest-backend:1.0`. Docker Hub
publication was not performed because the Docker Hub login/push requires an
interactive credential and explicit authorization. No registry digest is
claimed.

Cosign signing was not performed because the Cosign executable is not
installed. No key pair, signature, or verification result is claimed. After
installing Cosign from its official release, the required commands are:

```powershell
cosign generate-key-pair
cosign sign --key cosign.key msmanas/fest-backend@sha256:<actual-registry-digest>
cosign verify --key cosign.pub msmanas/fest-backend@sha256:<actual-registry-digest>
```

The private `cosign.key` must remain ignored and must never be committed.

## Evidence

Required screenshots must be captured on the assessment machine and are not
fabricated by this repository. Save Stage 1 evidence as
`screenshots/S1-2.png` and `screenshots/S1-3.png`.

Trivy, Docker Hub publication, and Cosign evidence will be added only after the
corresponding commands have actually run and their outputs have been checked.

## Checklist

- [x] Stage 1 image built and standalone health endpoint tested.
- [x] Stage 2 Compose services started and database healthcheck passed.
- [x] Stage 2 frontend/backend connectivity verified on port 170.
- [x] Stage 2 frontend/database network isolation verified by network membership.
- [x] Two registrations persisted across `docker compose down` and `docker compose up -d`.
- [x] Baseline and hardened Trivy reports saved.
- [ ] Trivy CRITICAL gate passed.
- [ ] Docker Hub images published and digest recorded.
- [ ] Cosign key pair generated and image signature verified.
- [ ] Required screenshots captured manually.
