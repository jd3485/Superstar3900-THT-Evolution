#!/usr/bin/env python3
"""Native KiCad pin-net check plus IDEAL DC screen of existing D803 gate clamp.

This is not a real 48V, automotive or fault-safe qualification. The onsemi
1N4742A 12V nominal specification is given at a 21mA test current, far above
the current in this illustrative gate circuit. Do not infer guaranteed VGS.
"""
from itertools import product
from pathlib import Path
import argparse,json,runpy

def ideal_gate(vin,r_source,r_sink,low,vz):
    raw_vsg=max(0.,(vin-low)*r_source/(r_source+r_sink))
    vsg=min(raw_vsg,vz)  # deliberately ideal Zener, NOT vendor model
    gate=vin-vsg
    i_sink=max(0.,(gate-low)/r_sink)
    i_source=vsg/r_source
    iz=max(0.,i_sink-i_source)
    return dict(vsg=vsg,vsg_open=raw_vsg,iz_mA=1000*iz,pz_mW=1000*vsg*iz)

def audit_native_netlist(filename):
    root=Path(__file__).resolve().parents[2]
    h=runpy.run_path(str(root/"03_Verifiche/V1.0/verify_kicad_netlist_v10.py"))
    nets=h["read_nets"](Path(filename))
    assert len(nets)==76,(len(nets),"V2.6 net count changed")
    def get(pin):
        matches=[name for name,pins in nets.items() if pin in pins]
        assert len(matches)==1,(pin,matches)
        return matches[0]
    def same(a,b):
        assert get(a)==get(b),(a,b,get(a),get(b))
    # D803 pin1=K, pin2=A; Q801 pin1=G, pin3=S.
    same(("D803","1"),("Q801","3"))
    same(("D803","2"),("Q801","1"))
    same(("D803","1"),("R1008","1"))
    same(("D803","2"),("R1008","2"))
    same(("D803","2"),("R1009","1"))
    assert get(("D803","1"))!=get(("D803","2"))
    return len(nets)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("netlist",nargs="?")
    p.add_argument("--math-only",action="store_true")
    args=p.parse_args()
    assert args.math_only != bool(args.netlist),"supply netlist or --math-only"
    cases=[(vin,ideal_gate(vin,rs,rd,vol,vz)) for vin,rs,rd,vol,vz in product(
        (11.,13.8,16.5,24.,36.,48.),
        (44650.,47000.,49350.),
        (9500.,10000.,10500.),
        (.1,.3,.6),
        (11.4,12.,12.6))]
    assert len(cases)==486
    normal=[row for vin,row in cases if vin==13.8]
    high=[row for vin,row in cases if vin==48.]
    assert min(x["vsg_open"] for x in high)>20.
    assert max(row["vsg"] for _,row in cases)<=12.6+1e-9
    assert max(x["iz_mA"] for x in high)<5.
    assert max(x["pz_mW"] for x in high)<60.
    verified=None if args.math_only else audit_native_netlist(args.netlist)
    result={
        "gate":"PASS_D803_NATIVE_TOPOLOGY_AND_IDEAL_MATH_ONLY" if verified is not None else "PASS_D803_IDEAL_MATH_PREFLIGHT_ONLY",
        "native_nets_verified":verified,
        "cases":len(cases),
        "D803":"onsemi 1N4742A 12V/1W axial THT already in V2.6",
        "vsg_13p8_ideal_range_V":[round(min(x["vsg"] for x in normal),3),round(max(x["vsg"] for x in normal),3)],
        "vsg_48_if_D803_OPEN_range_V":[round(min(x["vsg_open"] for x in high),3),round(max(x["vsg_open"] for x in high),3)],
        "iz_48_ideal_zener_range_mA":[round(min(x["iz_mA"] for x in high),3),round(max(x["iz_mA"] for x in high),3)],
        "pz_48_ideal_zener_max_mW":round(max(x["pz_mW"] for x in high),3),
        "assumed_vz_V":[11.4,12.6],
        "vz_guaranteed_at_predicted_current":False,
        "onsemi_vz_test_current_mA":21,
        "mosfet_vgs_max_abs_V":20,
        "vendor_transient_and_fault_qualified":False,
        "LM393_48V_qualified":False,
        "NO_FAB":True,"NO_TX":True}
    print(json.dumps(result,sort_keys=True))

if __name__=="__main__":
    main()
