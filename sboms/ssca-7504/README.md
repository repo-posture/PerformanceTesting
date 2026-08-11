# SSCA-7504 — CycloneDX SBOM Ingestion Validation

Validates [SSCA-7504](https://harness.atlassian.net/browse/SSCA-7504): scorecard handling when **ingesting** a pre-built CycloneDX SBOM (vs generating one in-pipeline).

## Files

| File | Description |
|---|---|
| `autosscauser-auto-134.cyclonedx.json` | CycloneDX **1.7** SBOM for `autosscauser/autosscauser-auto:134` (from Humanshu's Slack attachment) |
| `SSCA_7504_SBOM_Ingestion_TEST.yaml` | Harness pipeline — import into **SSCA / SSCA_Sanity_Automation** on QA |

## Expected behavior

- **Generation** (`SCS_CYCLONEDX_DOCKER_ALL_STEPS_CI_TEST`): no scorecard warning; scorecard present in API response.
- **Ingestion** (this pipeline): step should succeed; logs may show a **scorecard warning** because the SBOM uses CycloneDX spec **1.7** (generation was fixed to **1.6**).

## How to run

1. Push `sboms/ssca-7504/` to the `PerformanceTesting` repo (`main` branch).
2. In QA, create or update pipeline from `SSCA_7504_SBOM_Ingestion_TEST.yaml` in project **SSCA_Sanity_Automation**.
3. Run the pipeline and check the **SBOM Ingestion Autosscauser Auto 134** step logs for scorecard output.

## Image

The SBOM metadata references:

- Image: `autosscauser/autosscauser-auto:134`
- Digest: `sha256:45173bb6905ec910483f877cfda04e71405c20681a34bd1434565c8acee6272e`

Ensure this tag exists in Docker Hub before running.
