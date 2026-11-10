#!/usr/bin/env python3
"""KiCad 9 native FULL pin-partition verification: V1.4 (50 nets) + V1.5 (6 nets) -> V1.6 (52 nets).
Only four deliberate electrical joins allowed. Not a regulator, PLL, RF, thermal or PCB qualification.
"""
import json,runpy,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
read=runpy.run_path(str(ROOT/"03_Verifiche/V1.0/verify_kicad_netlist_v10.py"))["read_nets"]
old14=read(Path(sys.argv[1]));old15=read(Path(sys.argv[2]));new=read(Path(sys.argv[3]))
if (len(old14),len(old15))!=(50,6):
    raise AssertionError(f"Unrecognized V1.4/V1.5 baselines: {len(old14)} / {len(old15)}")
assert len(new)==52,f"Need exactly 52 KiCad9 electrical groups (50+6-4), got {len(new)}"
where={}
for net,pins in new.items():
    for pin in pins:
        if pin in where:raise AssertionError(f"Duplicated pin in new netlist {pin}")
        where[pin]=net
def preserve(title,old):
    mapping={}
    for oldnet,pins in old.items():
        target={where.get(p) for p in pins}
        if None in target or len(target)!=1:
            raise AssertionError(f"{title} net broken/missing {oldnet}: {target}")
        net=next(iter(target))
        if net in mapping:
            raise AssertionError(f"{title} two formerly isolated nets SHORTED: {mapping[net]} & {oldnet}")
        mapping[net]=oldnet
    return mapping
old4_targets=preserve("V1.4",old14)
old5_targets=preserve("V1.5",old15)
shared={old5_targets[n].split("/")[-1] for n in set(old4_targets)&set(old5_targets)}
required_shared={"GND","+5V_PLL","VCC_VCO5","VCC_BUF5"}
if shared!=required_shared:
    raise AssertionError(f"Wrong shared nets between original native KiCad schematics: {shared}")
def group(label,*pins):
    target={where.get(p) for p in pins}
    if None in target or len(target)!=1:
        raise AssertionError(f"{label}: required pins disconnected {pins} / actual {target}")
    return next(iter(target))
gnd=group("common GND",("U601","2"),("J601","2"),("U401","2"),("U803","4"),("U520","7"))
pll=group("PLL rail behind R611",("R611","2"),("U401","3"),("U402","14"),("J402","1"),("C611","1"))
vco=group("VCO rail behind R612",("R612","2"),("L501","1"),("J520","1"),("C612","1"))
buffer=group("LO buffer rail behind R613",("R613","2"),("U520","14"),("J521","1"),("C613","1"))
vin=group("unprotected external supply assumption",("U601","1"),("J601","1"),("D601","1"))
regulated=group("7805 output before series isolation",("U601","3"),("D601","2"),("R611","1"),("R612","1"),("R613","1"))
rails=[gnd,pll,vco,buffer,vin,regulated]
if len(rails)!=len(set(rails)):
    raise AssertionError(f"Unintended inter-rail short: {rails}")
group("VTUNE remains connected",("R805","2"),("D501","2"))
group("CMOS LO remains connected",("R513","2"),("U402","3"))
result={"status":"PASS_REAL_5_SHEET_RX_PLL_5V_INTEGRATION_ONLY",
"baseline_v14_nets":len(old14),"baseline_v15_nets":len(old15),"combined_v16_nets":len(new),
"legacy_v14_all_pin_groups_preserved":True,"legacy_v15_all_pin_groups_preserved":True,
"four_intentional_shared_nets":sorted(shared),"5v_branches_distinct":True,"vtune_lo_legacy_links_unchanged":True,
"protected_13v8_input":"NOT_IMPLEMENTED","20v_vtune_rail":"EXTERNAL",
"current_load_thermal":"NOT_QUALIFIED","PLL_lock_RF":"NOT_TESTED",
"pcb_exists":False,"pcb_drc":"NOT_RUN","fab_authorized":False,"tx_authorized":False}
Path(sys.argv[3]).parent.joinpath("v16_evidence.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,sort_keys=True))
