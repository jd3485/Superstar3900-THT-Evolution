#!/usr/bin/env python3
"""V2.6 R1011/D806/D804 thermal and fault screen. NOT hardware qualification.
Manufacturer anchors: Vishay PR03 P70 3 W Cu-lead, derating 70->200 C
(2025 datasheet); Diotec 1N5352B 14.2..15.8 V at 75 mA;
Vishay 1N5819 40 V repetitive peak reverse. Ideal Zener is NOT guaranteed.
"""
from __future__ import annotations
import argparse
from itertools import product
from pathlib import Path
import json
import runpy

def pr03_allowed_w(ambient):
    if ambient <= 70.: return 3.
    if ambient >= 200.: return 0.
    return 3.*(200.-ambient)/(200.-70.)

def r1011_ideal_zener(vin,vf,res,vclamp):
    drop=max(0.,vin-vf-vclamp)
    current=drop/res
    return current*current*res,1000.*current, vclamp*current

def check_native(path):
    root=Path(__file__).resolve().parents[2]
    h=runpy.run_path(str(root/"03_Verifiche/V1.0/verify_kicad_netlist_v10.py"))
    nets=h["read_nets"](path)
    assert len(nets)==76,("Unexpected V2.6 net groups",len(nets))
    def net(part):
        matching=[name for name,pins in nets.items() if part in pins]
        assert len(matching)==1,(part,matching)
        return matching[0]
    def same(a,b):
        assert net(a)==net(b),(a,b,net(a),net(b))
    # D804 is K=1, A=2. D806 K=1, A=2.
    same(("D804","2"),("R1002","1")) # raw input
    same(("D804","1"),("R1011","1")) # preclamp
    same(("R1011","2"),("D806","1")) # LM393 controller supply
    same(("D806","1"),("U801","8"))
    same(("D806","1"),("R1001","1"))
    same(("D806","2"),("U801","4")) # GND
    same(("D805","1"),("D806","1"))
    same(("D805","2"),("D806","2"))
    assert net(("D804","2"))!=net(("R1011","2"))
    assert net(("D806","1"))!=net(("D806","2"))
    return len(nets)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("netlist",nargs="?",type=Path)
    parser.add_argument("--math-only",action="store_true")
    args=parser.parse_args()
    assert args.math_only != bool(args.netlist),"Supply real netlist or --math-only"
    rows=[]
    for vin,vf,res,vz,ambient in product(
        (13.8,16.5,24.,36.,48.),
        (.2,.4,.7),
        (779.,820.,861.),
        (14.2,15.0,15.8),
        (70.,110.,125.,140.,150.)):
        power,iz,pz=r1011_ideal_zener(vin,vf,res,vz)
        allow=pr03_allowed_w(ambient)
        rows.append((vin,ambient,power,iz,pz,allow,power>allow))
    assert len(rows)==675
    assert abs(pr03_allowed_w(140.)-3.*60./130.)<1e-12
    at48=[x for x in rows if x[0]==48. and x[1]==140.]
    at36=[x for x in rows if x[0]==36. and x[1]==140.]
    assert len(at48)==27 and len(at36)==27
    assert any(x[6] for x in at48)
    assert not any(x[6] for x in at36)
    short36=(36.-.2)**2/779.
    assert short36>pr03_allowed_w(140.)
    assert 40.<48. # Vishay 1N5819 VRRM; actual diode stress needs fault-path study
    native=None if args.math_only else check_native(args.netlist)
    result={
        "gate":"PASS_UPSTREAM_THERMAL_AND_FAULT_RISKS_DETECTED_NOT_A_RELEASE",
        "native_v26_net_groups":native,
        "cases":len(rows),
        "pr03_allowed_140c_w":round(pr03_allowed_w(140.),4),
        "pr03_allowed_150c_w":round(pr03_allowed_w(150.),4),
        "r1011_48v_140c_ideal_15v_zener_w":[round(min(x[2] for x in at48),4),
                                            round(max(x[2] for x in at48),4)],
        "r1011_48v_140c_over_derated_limit_cases":sum(x[6] for x in at48),
        "r1011_36v_140c_over_limit_ideal_clamp_cases":sum(x[6] for x in at36),
        "r1011_36v_d806_short_w":round(short36,4),
        "diotec_d806_vz_test_current_mA":75,
        "vishay_d804_reverse_rating_v":40,
        "zener_vz_at_circuit_current_guaranteed":False,
        "diode_reverse_48v_fault_path_qualified":False,
        "lm393_upstream_fault_qualified":False,
        "no_vendor_spice":True,
        "NO_FAB":True,"NO_TX":True,"NO_BATTERY_VEHICLE":True,
    }
    print(json.dumps(result,sort_keys=True))

if __name__=="__main__":main()
