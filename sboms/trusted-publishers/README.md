# Trusted Publishers SBOM fixtures (SSCA-8436 / SCS_TRUSTED_PUBLISHERS)

CycloneDX 1.5 fixtures with `supplier.name` + `dependencies` graph.

**Pipeline:** `SBOM_Trusted_Publishers_TEST`  
**Policy:** `license_expression_family_qe_policy_set` (allow Permissive, deny Copyleft)

**Publishers (account Configurations):**
1. `Amazon` — Supplier contains `Amazon`
2. `AWS SDK PURL` — PURL starts with `pkg:npm/@aws-sdk/`

| Stage | File | Expected (publisher ON) |
| --- | --- | --- |
| TP01 | tp-01-trusted-transitive-skip.cdx.json | PASS |
| TP02 | tp-02-direct-untrusted-deny.cdx.json | FAIL |
| TP03 | tp-03-purl-fallback-skip.cdx.json | PASS |
| TP04 | tp-04-untrusted-supplier-deny.cdx.json | FAIL |
| TP05 | tp-05-trusted-publisher-self-skip.cdx.json | PASS |
| TP06 | tp-06-deep-transitive-skip.cdx.json | PASS |
