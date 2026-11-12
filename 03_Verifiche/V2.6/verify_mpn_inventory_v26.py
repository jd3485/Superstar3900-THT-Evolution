#!/usr/bin/env python3
"""V2.6 manufacturer lifecycle inventory: compare 138 actual KiCad PCB components.
Parse distinct placed symbol blocks, NEVER search across multiple symbols.
A successful test proves inventory integrity, not product lifecycle.
"""
from pathlib import Path
import csv, re
ROOT=Path(__file__).resolve().parents[2]
SHEETS=("PLL_RX_HIERARCHICAL_MASTER_V2.6.kicad_sch",
"PLL_CORE_DIGITAL_V2.6.kicad_sch","PD_FILTER_DRIVER_V2.6.kicad_sch",
"VCO_RX_AND_LOBUF_V2.6.kicad_sch","POWER5_DISTRIBUTION_V2.6.kicad_sch",
"INPUT_FUSE_REVERSE_TVS_OVP_V2.6.kicad_sch","POWER20_VTUNE_BOOST_LDO_V2.6.kicad_sch")
LIB=re.compile(r'^\(symbol \(lib_id "([^"]+)"')
REF=re.compile(r'\(property "Reference" "([^"]+)"')
VAL=re.compile(r'\(property "Value" "([^"]+)"')
FP=re.compile(r'\(property "Footprint" "([^"]+)"')
def read_cad():
    result=[]
    for sheet in SHEETS:
        content=(ROOT/"04_KiCad/V2.6"/sheet).read_text(encoding="utf-8")
        for block in re.split(r'(?=\(symbol \(lib_id ")',content)[1:]:
            lib=LIB.search(block)
            ref=REF.search(block)
            value=VAL.search(block)
            fp=FP.search(block)
            if not (lib and ref and value and fp):
                # Electrical-only PWR_FLAGs do not have physical footprints.
                assert "in_bom no" in block and "on_board no" in block, (
                    "Malformed physical component",sheet,block[:120])
                continue
            assert "(in_bom yes)" in block[:300], (sheet,ref.group(1))
            assert "(on_board yes)" in block[:300], (sheet,ref.group(1))
            result.append((ref.group(1),sheet,lib.group(1),value.group(1),fp.group(1)))
    return result
def main():
    actual=read_cad()
    assert len(actual)==138,len(actual)
    assert len({r[0] for r in actual})==138
    with (ROOT/"03_Verifiche/V2.6/INVENTARIO_MPN_V26.csv").open(newline="",encoding="utf-8") as f:
        rows=list(csv.DictReader(f))
    assert len(rows)==138,len(rows)
    physical={tuple(r[k] for k in ("reference","sheet","kicad_library_symbol","cad_value","footprint")) for r in rows}
    assert physical==set(actual),(
        "Missing",sorted(set(actual)-physical),"Extra",sorted(physical-set(actual)))
    ids={r["reference"] for r in rows}
    assert {"Q801","D804","R1011"}.issubset(ids)
    assert not ({"PWR701","PWR801","PWR802"} & ids)
    allowed={"ATTIVO_CONFERMATO","DA_VERIFICARE","CONFLITTO_FONTI","EOL_NRND"}
    assert all(r["manufacturer_lifecycle"] in allowed for r in rows)
    confirmed={r["reference"] for r in rows if r["manufacturer_lifecycle"]=="ATTIVO_CONFERMATO"}
    assert confirmed=={"Q801","U802","U520","U601","U911","D806"},confirmed
    assert all(r["mpn_exact_confirmed"]=="SI" and r["official_source"].startswith("https://")
               for r in rows if r["manufacturer_lifecycle"]=="ATTIVO_CONFERMATO")
    assert all(r["mpn_exact_confirmed"]=="NO"
               for r in rows if r["manufacturer_lifecycle"]!="ATTIVO_CONFERMATO")
    # Procurement groups must cover every exact physical reference; groups
    # never promote a lifecycle status and do not alter the release gate.
    from group_procurement_v26 import build
    bins = build()
    assert len(bins) == 114, len(bins)
    assert sum(int(group["quantity"]) for group in bins) == 138
    grouped_ids = [ref for group in bins for ref in group["references"].split(";")]
    assert len(grouped_ids) == len(set(grouped_ids)) == 138
    assert set(grouped_ids) == ids
    import sys
    if "--release" in sys.argv:
        unresolved=[r["reference"] for r in rows if r["manufacturer_lifecycle"]!="ATTIVO_CONFERMATO"]
        assert not unresolved, f"BOM_RELEASE_BLOCKED: {len(unresolved)} refs need active manufacturer MPN: {unresolved}"
    print("PASS_V26_CAD_INVENTORY_INTEGRITY_ONLY_BOM_RELEASE_BLOCKED_132")
if __name__=="__main__":
    main()
