# Trusted Publishers SBOM fixtures (SSCA-8436 / SCS_TRUSTED_PUBLISHERS)

Used by pipeline `SBOM_Trusted_Publishers_TEST`.

**Before run**
1. Enable FF `SCS_TRUSTED_PUBLISHERS`
2. Create account Trusted Publishers:
   - Name: `Amazon` — rule: Supplier contains `Amazon` (Enabled)
   - Name: `AWS SDK PURL` — rule: PURL starts with `pkg:npm/@aws-sdk/` (Enabled)  *(or `pkg:npm/%40aws-sdk/` depending on stored PURL encoding)*
3. Policy set: `license_expression_family_qe_policy_set` (allow Permissive, deny Copyleft)
4. Expected-FAIL stages use MarkAsSuccess

| Stage | File | What it proves | Expected (publisher ON) |
| --- | --- | --- | --- |
| TP01 | tp-01-trusted-transitive-skip.spdx.json | Amazon supplier + AGPL transitive skipped | PASS |
| TP02 | tp-02-direct-untrusted-deny.spdx.json | Direct AGPL still evaluated | FAIL |
| TP03 | tp-03-purl-fallback-skip.spdx.json | No supplier → PURL starts-with match | PASS |
| TP04 | tp-04-untrusted-supplier-deny.spdx.json | Non-matching supplier not skipped | FAIL |
| TP05 | tp-05-trusted-publisher-self-skip.spdx.json | Trusted Publisher package itself skipped | PASS |
| TP06 | tp-06-deep-transitive-skip.spdx.json | Deeper transitive under Amazon skipped | PASS |

Manual after pipeline: disable Amazon publisher and re-run TP01 → should FAIL (TP-08/TP-25).
