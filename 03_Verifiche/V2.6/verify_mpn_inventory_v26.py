#!/usr/bin/env python3
"""Check 138 physical KiCad V2.6 CAD refs against unqualified lifecycle inventory."""
from pathlib import Path
import csv,re
ROOT=Path(__file__).resolve().parents[2]
SHEETS=("PLL_RX_HIERARCHICAL_MASTER_V2.6.kicad_sch","PLL_CORE_DIGITAL_V2.6.kicad_sch",
"PD_FILTER_DRIVER_V2.6.kicad_sch","VCO_RX_AND_LOBUF_V2.6.kicad_sch",
"POWER5_DISTRIBUTION_V2.6.kicad_sch","INPUT_FUSE_REVERSE_TVS_OVP_V2.6.kicad_sch",
"POWER20_VTUNE_BOOST_LDO_V2.6.kicad_sch")
PATTERN=re.compile(r'\(symbol \(lib_id "([^"]+)"[\s\S]*?\(property "Reference" "([^"]+)"[\s\S]*?\(property "Value" "([^"]+)"[\s\S]*?\(property "Footprint" "([^"]+)"')
def main():
    found=[]
    for sheet in SHEETS:
        content=(ROOT/"04_KiCad/V2.6"/sheet).read_text()
        for m in PATTERN.finditer(content):
            lib,ref,value,foot=m.groups()
            assert not ref.startswith("#"),ref
            assert foot and not re.search(r"(^|:)Package_[^:]*SMD",foot),(ref,foot)
            found.append((ref,sheet,lib,value,foot))
    assert len(found)==138,len(found)
    assert len({x[0] for x in found})==138
    with (ROOT/"03_Verifiche/V2.6/INVENTARIO_MPN_V26.csv").open(newline="") as f:
        rows=list(csv.DictReader(f))
    assert len(rows)==138,len(rows)
    actual={tuple(r[k] for k in ("reference","sheet","kicad_library_symbol","cad_value","footprint")) for r in rows}
    assert actual==set(found),"CSV inventory differs from KiCad source"
    assert all(r["mpn_exact_confirmed"]=="NO" and r["manufacturer_lifecycle"]=="DA_VERIFICARE" for r in rows)
    print("PASS_V26_138_CAD_REFERENCES_INVENTORIED_NO_MPN_LIFECYCLE_FALSIFIED")
if __name__=="__main__":main()
