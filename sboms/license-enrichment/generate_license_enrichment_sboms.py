#!/usr/bin/env python3
"""Generate SBOM license-enrichment test scenarios from the redis:7.2-alpine base SBOM.

Each scenario mutates license fields so ingestion can be validated against redis:7.2-alpine.
Run from repo root: python3 sboms/license-enrichment/generate_license_enrichment_sboms.py
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE / "base-redis-7.2-alpine.spdx.json"
MANIFEST = HERE / "scenarios.json"

# Packages with well-known licenses in the real redis:7.2-alpine image.
TRACKED = {
    "alpine-baselayout": {"actual": "GPL-2.0-only", "family": "Copyleft"},
    "musl": {"actual": "MIT", "family": "Permissive"},
    "zlib": {"actual": "Zlib", "family": "Permissive"},
}


def load_base() -> dict:
    with BASE.open(encoding="utf-8") as f:
        return json.load(f)


def pkg_by_name(doc: dict, name: str) -> dict | None:
    for pkg in doc.get("packages", []):
        if pkg.get("name") == name:
            return pkg
    return None


def set_license(pkg: dict, value: str) -> None:
    pkg["licenseDeclared"] = value
    pkg["licenseConcluded"] = value


def write_scenario(filename: str, doc: dict) -> None:
    out = HERE / filename
    with out.open("w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)
        f.write("\n")
    print(f"  wrote {out.name}")


def main() -> None:
    base = load_base()
    manifest = []

    # LIC-ENR-01: all tracked components use placeholder licenses
    doc01 = copy.deepcopy(base)
    for name in TRACKED:
        pkg = pkg_by_name(doc01, name)
        if pkg:
            set_license(pkg, "NOASSERTION")
    write_scenario("lic-enr-01-noassertion.spdx.json", doc01)
    manifest.append(
        {
            "id": "LIC-ENR-01",
            "file": "lic-enr-01-noassertion.spdx.json",
            "target": "redis:7.2-alpine",
            "mutation": "Set alpine-baselayout, musl, zlib to NOASSERTION",
            "expect_after_ingest": {
                "alpine-baselayout": "GPL-2.0-only",
                "musl": "MIT",
                "zlib": "Zlib",
            },
        }
    )

    # LIC-ENR-02: copyleft component tagged with wrong permissive license
    doc02 = copy.deepcopy(base)
    pkg = pkg_by_name(doc02, "alpine-baselayout")
    if pkg:
        set_license(pkg, "MIT")
    write_scenario("lic-enr-02-wrong-mit.spdx.json", doc02)
    manifest.append(
        {
            "id": "LIC-ENR-02",
            "file": "lic-enr-02-wrong-mit.spdx.json",
            "target": "redis:7.2-alpine",
            "mutation": "Set alpine-baselayout (GPL) to MIT",
            "expect_after_ingest": {"alpine-baselayout": "GPL-2.0-only"},
        }
    )

    # LIC-ENR-03: mixed — one placeholder, one wrong, one correct
    doc03 = copy.deepcopy(base)
    if pkg_by_name(doc03, "alpine-baselayout"):
        set_license(pkg_by_name(doc03, "alpine-baselayout"), "NOASSERTION")
    if pkg_by_name(doc03, "musl"):
        set_license(pkg_by_name(doc03, "musl"), "Apache-2.0")
    # zlib left as-is (Zlib)
    write_scenario("lic-enr-03-mixed.spdx.json", doc03)
    manifest.append(
        {
            "id": "LIC-ENR-03",
            "file": "lic-enr-03-mixed.spdx.json",
            "target": "redis:7.2-alpine",
            "mutation": "alpine-baselayout=NOASSERTION, musl=Apache-2.0, zlib unchanged",
            "expect_after_ingest": {
                "alpine-baselayout": "GPL-2.0-only",
                "musl": "MIT",
                "zlib": "Zlib",
            },
        }
    )

    # LIC-ENR-04: baseline control — unmodified SBOM
    write_scenario("lic-enr-04-baseline.spdx.json", base)
    manifest.append(
        {
            "id": "LIC-ENR-04",
            "file": "lic-enr-04-baseline.spdx.json",
            "target": "redis:7.2-alpine",
            "mutation": "None (real Syft SBOM)",
            "expect_after_ingest": {
                "alpine-baselayout": "GPL-2.0-only",
                "musl": "MIT",
                "zlib": "Zlib",
            },
        }
    )

    with MANIFEST.open("w", encoding="utf-8") as f:
        json.dump({"target_image": "redis:7.2-alpine", "scenarios": manifest}, f, indent=2)
        f.write("\n")
    print(f"  wrote {MANIFEST.name}")


if __name__ == "__main__":
    main()
