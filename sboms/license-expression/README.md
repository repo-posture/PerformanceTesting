# License Expression SBOM fixtures (SSCA-7533 / SCS_LICENSE_EXPRESSION)

Used by pipeline `SBOM_License_Expression_TEST`.

Policy set: `lfc_family_test_policy_set` (Permissive allowed, Copyleft denied).

| File | License expression | Expected enforcement |
| --- | --- | --- |
| le-01-and-deny.spdx.json | MIT AND GPL-3.0-only | FAIL |
| le-02-and-pass.spdx.json | MIT AND Apache-2.0 | PASS |
| le-03-or-pass.spdx.json | MIT OR GPL-3.0-only | PASS (key FF-on behavior) |
| le-04-or-deny.spdx.json | GPL-2.0-only OR LGPL-3.0-only | FAIL |
| le-05-comma-exact.spdx.json | MIT, Apache-2.0 | Exact-match / non-logical |
| le-06-single-mit.spdx.json | MIT | PASS |
| le-07-single-gpl.spdx.json | GPL-3.0-only | FAIL |
| le-08-brackets-exact.spdx.json | (MIT OR Apache-2.0) AND BSD-3-Clause | Exact-match |
| le-09-with-exact.spdx.json | GPL-2.0-only WITH Classpath-exception-2.0 | Exact-match |
