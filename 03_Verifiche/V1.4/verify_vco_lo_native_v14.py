#!/usr/bin/env python3
"""Real KiCad9 native netlist V1.4 cross-sheet CAD gate.
Check preservation of EVERY V1.3 component pin group while adding a candidate VCO and buffer.
Zero ERC does NOT prove RF oscillation, logic thresholds, closed-loop lock or fabrication.
"""
import json, runpy, sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
helper=runpy.run_path(str(root/"03_Verifiche/V1.0/verify_kicad_netlist_v10.py"))
old=helper["read_nets"](Path(sys.argv[1]))
new=helper["read_nets"](Path(sys.argv[2]))
if len(old)!=33:raise AssertionError(f"V1.3 expected 33 baseline nets, got {len(old)}")
where={}
for name,pins in new.items():
    for pin in pins:
        if pin in where:raise AssertionError(f"Duplicate net membership {pin}: {where[pin]}, {name}")
        where[pin]=name
mapping={}
for old_name,pins in old.items():
    present={where.get(pin) for pin in pins}
    if None in present or len(present)!=1:
        raise AssertionError(f"Legacy net {old_name} split or missing: {present}")
    target=next(iter(present))
    if target in mapping:
        raise AssertionError(f"Old nets {mapping[target]} and {old_name} were SHORTED together in V1.4!")
    mapping[target]=old_name
def on(pin):return where.get(pin)
def group(name,pins):
    groups={on(p) for p in pins}
    if None in groups or len(groups)!=1:raise AssertionError(f"Broken {name}: {list(pins)} -> {groups}")
    return next(iter(groups))
gnd=group("GND", {("U401","2"),("U803","4"),("U520","7"),("R502","2"),("J520","2"),("J521","2")})
tune=group("VTUNE closed wiring at CAD level", {("R805","2"),("J903","1"),("D501","2"),("C505","1"),("J524","1")})
clock=group("AC14 digital output through R513 to /2 clock", {("R513","2"),("J522","1"),("U402","3"),("J403","1")})
group("AC14 stage 2 driver", {("U520","4"),("R513","1")})
group("AC14 first inverter to second", {("U520","2"),("U520","3")})
group("AC14 RF input coupling", {("C510","2"),("U520","1"),("R512","2")})
group("BB204G two tied anodes", {("D501","1"),("D501","3"),("C504","2"),("R505","1")})
group("Colpitts tank", {("Q501","3"),("L501","2"),("C502","1"),("C504","1"),("C506","1")})
group("Q501 base bias", {("Q501","2"),("R501","2"),("R502","1"),("C501","1")})
group("Q501 emitter", {("Q501","1"),("R503","1"),("C502","2"),("C503","1")})
group("Q502 base", {("Q502","2"),("R506","2"),("R507","1"),("C506","2")})
group("Q502 emitter", {("Q502","1"),("R508","1"),("C507","1")})
group("analog LO output", {("C507","2"),("C510","1"),("R509","1"),("J523","1")})
vco5=group("external VCO supply", {("J520","1"),("Q502","3"),("L501","1"),("R501","1"),("R506","1"),("PWR520","1")})
buf5=group("external buffer supply", {("J521","1"),("U520","14"),("C511","1"),("R510","1"),("PWR521","1")})
for a,b in [(vco5,buf5),(vco5,tune),(buf5,tune),(clock,buf5),(clock,gnd)]:
    if a==b:raise AssertionError("Forbidden short between VCO, BUF, VTUNE, LO and GND")
for pin in [("U520",str(x)) for x in (5,9,11,13)]:
    if on(pin)!=gnd:raise AssertionError(f"Unused 74AC14 input {pin} must be grounded")
for pin in [("U520",str(x)) for x in (6,8,10,12)]:
    if on(pin) is not None and len(new[on(pin)])>1:
        raise AssertionError(f"Unused output {pin} unexpectedly connected to {new[on(pin)]}")
for ref,n in [("U401",28),("U402",14),("U803",8),("Q501",3),("Q502",3),("D501",3)]:
    if len([p for p in where if p[0]==ref])!=n:
        raise AssertionError(f"{ref} has not exactly {n} netlisted pins")
p=Path(sys.argv[2])
s=p.read_text()
tokens=helper["PAT"].findall(s)
ast,end=helper["parse_expr"](tokens)
if end!=len(tokens):raise AssertionError("Trailing native netlist text")
comp=helper["child"](ast,"components")
sp={}
for x in comp[1:]:
    if not isinstance(x,list) or not x or x[0]!="comp":continue
    sheet=helper["optional_child"](x,"sheetpath")
    if sheet:
        names=helper["optional_child"](sheet,"names")
        sp[str(helper["child"](x,"ref")[1])]=str(names[1]) if names else str(sheet)
if len({sp.get("U401"),sp.get("U803"),sp.get("Q501")})!=3 or not all(sp.get(x) for x in ("U401","U803","Q501")):
    raise AssertionError("No true three-child hierarchy: "+repr(sp))
result={"status":"PASS_NATIVE_V14_VCO_WIRING_ONLY","legacy_net_count":len(old),
        "all_legacy_pin_partitions_preserved":True,"new_net_count":len(new),
        "connected_vtune_to_dual_varactor_cathode_pin2":True,
        "connected_CMOS_clock_to_U402_pin3":True,
        "BB204G_anode_pins_1_and_3_tied":True,"unused_AC14_inputs_grounded":True,
        "three_distinct_real_child_sheetpaths":True,
        "RF_oscillation_with_buffer":"NOT_TESTED","phase_margin":"NOT_TESTED",
        "closed_PLL_lock":"NOT_TESTED","component_vendor_stock":"NOT_VERIFIED",
        "coil_footprint":"UNSELECTED","PCB_DRC":"NOT_RUN","RF_lab":"NOT_RUN",
        "fab_authorized":False,"tx_authorized":False}
p.parent.joinpath("v14_native_pin_net_evidence.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,sort_keys=True))
