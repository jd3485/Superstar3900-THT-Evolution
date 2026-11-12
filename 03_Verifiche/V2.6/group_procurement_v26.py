#!/usr/bin/env python3
"""Deterministic procurement grouping for 138 physical MAIN THT placements.

Groups by (cad_value, footprint); grouping is NOT equivalence qualification:
references are retained and lifecycle approval stays per placement. No network
requests and no change to the source CSV or KiCad files.
"""
import csv
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "INVENTARIO_MPN_V26.csv"
OUTPUT = HERE / "RAGGRUPPAMENTO_ACQUISTI_V26.csv"
FIELDS = ("cad_value", "footprint", "quantity", "references",
          "manufacturer_lifecycle_summary", "next_gate")


def build():
    with SOURCE.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 138:
        raise ValueError(f"Expected 138 physical placements, got {len(rows)}")
    ids = [r["reference"] for r in rows]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate reference")
    bins = defaultdict(list)
    for row in rows:
        bins[(row["cad_value"], row["footprint"])].append(row)
    result = []
    for (value, footprint), placements in sorted(bins.items()):
        refs = sorted(r["reference"] for r in placements)
        states = sorted(set(r["manufacturer_lifecycle"] for r in placements))
        approved = all(r["manufacturer_lifecycle"] == "ATTIVO_CONFERMATO"
                       for r in placements)
        result.append({
            "cad_value": value, "footprint": footprint,
            "quantity": len(refs), "references": ";".join(refs),
            "manufacturer_lifecycle_summary": ";".join(states),
            "next_gate": "CHECK_ELECTRICAL_AND_PACKAGE" if approved
                         else "QUALIFY_EXACT_OEM_MPN_PER_REFERENCE",
        })
    if sum(int(r["quantity"]) for r in result) != len(rows):
        raise ValueError("Placement coverage lost")
    return result


def main():
    result = build()
    with OUTPUT.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(result)
    print(f"GROUPING_ONLY: {len(result)} bins / "
          f"{sum(int(r['quantity']) for r in result)} physical references; "
          "NO BOM APPROVAL")


if __name__ == "__main__":
    main()
