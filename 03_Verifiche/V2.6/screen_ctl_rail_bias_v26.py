#!/usr/bin/env python3
"""V2.6 controller rail R1011/R1001 + ideal TL431/D806 DC network.
Analytical envelope ONLY, NOT SPICE, not start-up/transient/vendor guaranteed.
U801 load is an explicit assumption, not a measured/spec worst case.
"""
from itertools import product
from pathlib import Path
import argparse,json,runpy

VIN=(10.,11.5,13.8,16.5,24.,36.,48.)
VF=(.2,.4,.7)
RS=(779.,820.,861.)
RB=(1710.,1800.,1890.)
VREF=(2.45,2.50,2.55)
ICC=(.0005,.001,.002,.003)
CLAMP=15.

def rail(vin,vf,rs,rb,vref,icc,diode=True):
    # KCL: (VIN-VF-Vrail)/RS=ICC+(Vrail-Vref)/RB
    unloaded=(vin-vf-rs*icc+rs*vref/rb)/(1+rs/rb)
    assert unloaded>vref, "TL431 minimum-bias region not modeled"
    regulating=diode and unloaded>CLAMP
    vrail=CLAMP if regulating else unloaded
    ik=(vrail-vref)/rb
    iz=max(0.,(vin-vf-vrail)/rs-icc-ik) if regulating else 0.
    return vrail,ik,iz,regulating

def check_netlist(path):
    h=runpy.run_path(str(Path(__file__).resolve().parents[2]/
                 "03_Verifiche/V1.0/verify_kicad_netlist_v10.py"))
    nets=h["read_nets"](Path(path))
    assert len(nets)==76,("V2.6 native count",len(nets))
    def net(pair):
        names=[n for n,pins in nets.items() if pair in pins]
        assert len(names)==1,(pair,names)
        return names[0]
    for a,b in [
        (("D804","2"),("R1002","1")),
        (("D804","1"),("R1011","1")),
        (("R1011","2"),("D806","1")),
        (("R1011","2"),("R1001","1")),
        (("R1011","2"),("U801","8")),
        (("R1001","2"),("U802","1")),
        (("R1001","2"),("U802","3")),
        (("D806","2"),("U802","2")),
        (("D806","2"),("U801","4"))]:
        assert net(a)==net(b),(a,b,net(a),net(b))
    assert net(("R1001","1"))!=net(("R1001","2"))
    return len(nets)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("native_netlist",nargs="?")
    ap.add_argument("--math-only",action="store_true")
    args=ap.parse_args()
    assert (args.native_netlist is None)==args.math_only
    cases=list(product(VIN,VF,RS,RB,VREF,ICC))
    assert len(cases)==2268
    normal={v:[rail(*p) for p in cases if p[0]==v] for v in VIN}
    failed={v:[rail(*p,diode=False) for p in cases if p[0]==v] for v in VIN}
    assert all(not x[3] for x in normal[13.8]),"No Zener at 13.8 in idealized nominal network"
    assert all(x[3] for x in normal[36.])
    assert all(x[1]>.0004 for group in normal.values() for x in group),"Assumed TL431 bias meets 0.4mA"
    assert all(x[0]<36 for x in failed[48.]),"This *specific* healthy-TL431 open-D806 envelope"
    assert any(x[0]>36 for p in cases if p[0]==48. for x in
        [(p[0]-p[1]-p[2]*p[5])]),"Dual fault TL431 reference OPEN can expose U801"
    native=None if args.math_only else check_netlist(args.native_netlist)
    def rng(rows,index,factor=1.):
        return [round(min(x[index] for x in rows)*factor,3),
                round(max(x[index] for x in rows)*factor,3)]
    result={
      "gate":"PASS_IDEAL_LOAD_AWARE_RAIL_BIAS_DIAGNOSTIC_ONLY",
      "native_nets":native,"cases":len(cases),
      "at_11p5_v_rail_V":rng(normal[11.5],0),
      "at_13p8_v_rail_V":rng(normal[13.8],0),
      "at_13p8_tl431_cathode_mA":rng(normal[13.8],1,1000),
      "at_48_ideal_d806_zener_mA":rng(normal[48.],2,1000),
      "at_48_d806_open_tl431_healthy_rail_V":rng(failed[48.],0),
      "at_48_d806_and_tl431_open_ideal_rail_max_V":round(max(
          p[0]-p[1]-p[2]*p[5] for p in cases if p[0]==48.),3),
      "tl431_0p4mA_is_25C_datasheet_condition_not_thermal_guarantee":True,
      "LM393_voltage_and_input_common_mode_qualified":False,
      "actual_U801_supply_current_qualified":False,
      "diode_knee_and_startup_qualified":False,
      "PVT_vendor_SPICE":False,
      "NO_FAB":True,"NO_TX":True}
    print(json.dumps(result,sort_keys=True))

if __name__=="__main__":
    main()
