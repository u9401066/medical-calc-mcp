# Production Readiness

## Honest Status

This repository is technically strong, but it was not honestly production-grade before the readiness work in this document.

What was already strong:
- Domain coverage, calculator breadth, and formula provenance checks
- CI quality gates for lint, type check, tests, and consistency
- Docker packaging and basic health checks

What was missing:
- A true readiness contract separate from liveness
- An enforceable production deployment gate
- Explicit runtime checks for auth, rate limiting, CORS hardening, and TLS expectations

After the changes in this phase, the project is closer to production-ready, but it still should not be marketed as full enterprise-grade without additional operational work listed below.

## Implemented Now

- Shared readiness model in `src/shared/production_readiness.py`
- REST API readiness endpoint at `/ready`
- MCP readiness endpoint at `/ready`
- Deployment gate script: `scripts/check_production_readiness.py`
- CI job that runs readiness checks under a production-like profile
- Docker validation that checks `/ready`, not only `/health`

## Readiness Rules

The readiness gate currently enforces these conditions:

- All expected calculators are loaded
- Discovery indexes are built
- Formula provenance manifest has no coverage gaps
- Production auth is enabled and API keys are configured
- Production rate limiting is enabled
- Production CORS is not wildcard `*`
- TLS is enabled directly or trusted via reverse proxy

Development environments downgrade perimeter issues to warnings so local work stays usable.

## CI Production Profile

The CI readiness job uses a production-like profile with these environment variables:

```bash
APP_ENV=production
SECURITY_AUTH_ENABLED=true
SECURITY_API_KEYS=ci-production-key
SECURITY_RATE_LIMIT_ENABLED=true
CORS_ORIGINS=https://ci.example.com
TRUST_REVERSE_PROXY_SSL=true
```

To run the same check locally:

```bash
uv run python scripts/check_production_readiness.py --service all --environment production
```

## Still Required For True Commercial / Enterprise Grade

These gaps remain outside the current code-level readiness work:

- Centralized observability: metrics, structured audit logs, distributed tracing, alerting
- Secret management: vault/KMS integration, rotation policy, zero plain-text shared keys
- Supply-chain controls: SBOM generation, dependency signing/verification, image signing, CVE policy
- Operational resilience: load tests, chaos drills, backup/restore verification, disaster recovery runbooks
- Compliance posture: access reviews, PHI handling boundaries, formal retention and incident response policies
- Runtime governance: deployment manifests, autoscaling policy, WAF/reverse proxy baselines, SLOs/SLIs

Those items are the difference between a strong open-source service and a repo that can honestly claim commercial production maturity.
