#!/usr/bin/env python3
"""THT V2.6: risk-based *design* gating, distinct from complete BOM-release.

Every placed reference receives exactly one risk class. An ordinary passive
may be specified generically while schematic engineering proceeds; it is
NOT qualified, orderable or approved for fabrication. Safety/RF/unique
components keep functional verification gates before dependent circuits.
"""
import csv
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "INVENTARIO_MPN_V26.csv"
OUT = HERE / "CLASSIFICAZIONE_RISCHIO_V26.csv"
FIELDS = ("reference", "risk_class", "design_policy", "bom_release_policy", "rationale")

RF_CAPS = {"C403", "C404"} | {f"C{i}" for i in range(500, 513)} - {"C509", "C512"}
SAFETY_RES = {f"R{i}" for i in range(1001, 1018)} | {f"R{i}" for i in range(920, 928)}
SAFETY_CAPS = {"C803"} | {f"C{i}" for i in range(920, 930)}
DNI = {"C805"}


def classify(row):
    ref = row["reference"]
    if ref in DNI:
        return "DNI_REVIEW", "NOT_INSTALLED_PENDING_CAD_CONFIRMATION", (
            "Value denotes DNI; decide stuffed vs not stuffed and count in assembly BOM")
    if ref in SAFETY_RES:
        return "SAFETY_POWER", "REVIEW_VALUE_POWER_DERATING_FAULT_FIRST", (
            "Protection/boost setpoint, fault current, dissipation or tolerance")
    if ref in SAFETY_CAPS:
        return "SAFETY_POWER", "REVIEW_VOLTAGE_RIPPLE_LIFE_FIRST", (
            "Protection/boost capacitor; ripple, lifetime, startup and single faults")
    if ref in RF_CAPS:
        return "RF_PRECISION", "REVIEW_RF_DIELECTRIC_Q_TOLERANCE_FIRST", (
            "PLL crystal load or RF VCO tuning/coupling, dielectric and parasitics matter")
    if ref.startswith("R"):
        return "STANDARD_PASSIVE", "SPECIFICATION_ONLY_DURING_SCHEMATIC", (
            "Specify resistance, tolerance, power, TCR and THT envelope per reference")
    if ref.startswith("C"):
        return "STANDARD_PASSIVE", "SPECIFICATION_ONLY_DURING_SCHEMATIC", (
            "Specify C, dielectric, voltage, ESR/ESL, ripple, THT envelope per reference")
    if ref.startswith("J"):
        return "INTERFACE_THT", "SCHEMATIC_OK_PINOUT_BEFORE_LAYOUT", (
            "Pin count, gender, pitch, mating counterpart, current and mechanical clearance")
    if ref in {"U401", "L501", "X401", "D501"}:
        return "UNIQUE_RF", "OEM_AVAILABILITY_AND_RF_REVIEW_BEFORE_DEPENDENT_DESIGN_LOCK", (
            "PLL, tunable coil, varactor or crystal: exact functional specification")
    if ref in {"F701", "D702", "U801", "U802", "Q801", "Q802", "Q803",
               "D803", "D804", "D805", "D806", "D701", "L920",
               "U911", "U912", "D920", "D921", "D922", "U803"}:
        return "SAFETY_POWER", "REVIEW_LIMITS_AND_SINGLE_FAULT_FIRST", (
            "Input/protection, regulator, boost, comparator or analog rail dependency")
    return "ACTIVE_COMPONENT", "CHECK_FUNCTION_AND_PACKAGE_BEFORE_DEPENDENT_DESIGN_LOCK", (
        "Non-passive IC/diode/transistor requires proper pinout and lifecycle strategy")


def build():
    with SOURCE.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 138:
        raise ValueError("Expected V2.6 CAD inventory with 138 physical references")
    out = []
    seen = set()
    for row in rows:
        ref = row["reference"]
        if ref in seen:
            raise ValueError(f"Duplicate reference {ref}")
        seen.add(ref)
        risk, design, rationale = classify(row)
        out.append({
            "reference": ref, "risk_class": risk, "design_policy": design,
            "bom_release_policy": "EXACT_ACTIVE_OEM_MPN_AND_THT_FIT_REQUIRED",
            "rationale": rationale,
        })
    if set(r["reference"] for r in out) != seen or len(out) != 138:
        raise AssertionError("Incomplete design-risk coverage")
    assert {"U401", "L501", "X401", "D501", "F701", "U801", "L920",
            "C403", "C404", "C805", "R1011"}.issubset(seen)
    assert all(x["risk_class"] != "STANDARD_PASSIVE" for x in out
               if x["reference"] in {"U401", "L501", "X401", "D501", "F701",
                                    "U801", "L920", "C403", "C404", "C805", "R1011"})
    assert all(x["bom_release_policy"] == "EXACT_ACTIVE_OEM_MPN_AND_THT_FIT_REQUIRED"
               for x in out)
    return out


def main():
    rows = build()
    with OUT.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print("DESIGN_RISK_CLASSIFICATION_ONLY; release-gate unchanged; counts:",
          dict(sorted(Counter(r["risk_class"] for r in rows).items())))


if __name__ == "__main__":
    main()
