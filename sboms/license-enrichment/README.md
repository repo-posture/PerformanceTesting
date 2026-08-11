# SBOM License Enrichment Scenarios

Validates whether Harness **enriches/replaces** placeholder or wrong licenses when ingesting a pre-built SBOM against `redis:7.2-alpine`.

## How to get the SBOM files

These are **not** the large CycloneDX performance SBOMs in `sboms/sbom_cyclonedx_*.json`. For license testing we use a small, real Syft SPDX export of `redis:7.2-alpine` as the base:

1. **Base SBOM** — `base-redis-7.2-alpine.spdx.json` (copied from Syft output for `docker.io/library/redis:7.2-alpine`)
2. **Regenerate scenarios** — run:

```bash
python3 sboms/license-enrichment/generate_license_enrichment_sboms.py
```

This writes four scenario files plus `scenarios.json` (expected outcomes).

## Scenarios

| ID | File | What we inject | Expected after ingest |
|---|---|---|---|
| LIC-ENR-01 | `lic-enr-01-noassertion.spdx.json` | `NOASSERTION` on alpine-baselayout, musl, zlib | GPL-2.0-only, MIT, Zlib |
| LIC-ENR-02 | `lic-enr-02-wrong-mit.spdx.json` | MIT on alpine-baselayout (actually GPL) | GPL-2.0-only |
| LIC-ENR-03 | `lic-enr-03-mixed.spdx.json` | NOASSERTION on baselayout, Apache-2.0 on musl, zlib unchanged | GPL-2.0-only, MIT, Zlib |
| LIC-ENR-04 | `lic-enr-04-baseline.spdx.json` | Unmodified real SBOM (control) | Same as input |

## Manual verification (post-ingest)

After pipeline run, in Harness QA → SSCA → Artifacts → `redis:7.2-alpine`:

1. Open the SBOM / component list for the pipeline execution
2. Search for `alpine-baselayout`, `musl`, `zlib`
3. Compare stored license vs `scenarios.json` → `expect_after_ingest`

## Push before running Harness pipeline

The QA pipeline clones `repo-posture/PerformanceTesting` (branch `main`). Commit and push this folder first:

```bash
git add sboms/license-enrichment/
git commit -m "Add SBOM license enrichment test scenarios"
git push origin main
```

## Harness pipeline

- **Name:** SBOM License Enrichment TEST
- **Project:** SSCA / SSCA_Sanity_Automation
- **YAML:** see `Deepeval/license-test/SBOM_License_Enrichment_TEST.yaml`
