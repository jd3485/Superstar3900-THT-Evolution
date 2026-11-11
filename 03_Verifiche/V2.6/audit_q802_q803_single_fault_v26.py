#!/usr/bin/env python3
"""V2.6 Q802/Q803 single-device C-E fault matrix and native-net topology audit.
Binary conducting-channel abstraction, NOT transistor SPICE or hardware safety.
"""
from itertools import product
from pathlib import Path
import argparse,json,runpy

def sink(ovp_permit,uvlo_permit,fault):
    # Q802 above Q803; a C-E short bypasses that transistor's veto.
    # C-E open leaves the series path nonconducting.
    a=ovp_permit
    b=uvlo_permit
    if fault=="Q802_CE_SHORT":a=True
    if fault=="Q803_CE_SHORT":b=True
    if fault=="Q802_CE_OPEN":a=False
    if fault=="Q803_CE_OPEN":b=False
    return a and b

def check_native(filename):
    h=runpy.run_path(str(Path(__file__).resolve().parents[2]/
                  "03_Verifiche/V1.0/verify_kicad_netlist_v10.py"))
    nets=h["read_nets"](Path(filename))
    assert len(nets)==76,(len(nets),"Unexpected native V2.6 net count")
    def net(p):
        matches=[name for name,members in nets.items() if p in members]
        assert len(matches)==1,(p,matches)
        return matches[0]
    def same(a,b):
        assert net(a)==net(b),(a,b,net(a),net(b))
    same(("Q802","3"),("R1009","2")) # GATE_SINK, upper C
    same(("Q802","1"),("Q803","3"))  # SERIES_MID, upper E/lower C
    same(("Q803","1"),("U801","4")) # ground
    same(("Q802","2"),("R1007","2")) # CMP_OUT -> Q_BASE drive
    same(("Q803","2"),("R1016","2"))# UVLO_OC -> UVLO_BASE drive
    same(("R1009","1"),("D803","2"))# PFET gate
    same(("D803","1"),("Q801","3"))# PFET source
    assert len({net(("Q802","3")),net(("Q802","1")),net(("Q803","1"))})==3
    return len(nets)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("native_netlist",nargs="?")
    p.add_argument("--math-only",action="store_true")
    a=p.parse_args()
    assert a.math_only==(a.native_netlist is None)
    states=list(product((False,True),repeat=2))
    fault_names=("HEALTHY","Q802_CE_SHORT","Q803_CE_SHORT","Q802_CE_OPEN","Q803_CE_OPEN")
    rows=[{"fault":fault,"ovp_permit":ovp,"uvlo_permit":uvlo,
           "gate_sink":sink(ovp,uvlo,fault),
           "violation":sink(ovp,uvlo,fault) and not (ovp and uvlo)}
          for fault in fault_names for ovp,uvlo in states]
    assert len(rows)==20
    assert all(r["gate_sink"]==(r["ovp_permit"] and r["uvlo_permit"]) for r in rows if r["fault"]=="HEALTHY")
    bad=[r for r in rows if r["violation"]]
    assert {(r["fault"],r["ovp_permit"],r["uvlo_permit"]) for r in bad}=={
        ("Q802_CE_SHORT",False,True),("Q803_CE_SHORT",True,False)}
    assert all(not r["gate_sink"] for r in rows if r["fault"].endswith("_OPEN"))
    native=None if a.math_only else check_native(a.native_netlist)
    print(json.dumps({
      "gate":"PASS_RISK_DETECTED_DUAL_NPN_SINGLE_SHORT_BYPASS_NO_SAFETY_APPROVAL",
      "native_v26_net_groups":native,
      "logical_states_tested":len(rows),
      "single_ce_short_bypass":bad,
      "open_ce_blocks_sink_ideal_only":True,
      "series_npn_single_short_fail_closed":False,
      "transistor_storage_leakage_bvceo_qualified":False,
      "mosfet_gate_voltage_qualified":False,
      "independent_powergood_mute_present":False,
      "NO_FAB":True,"NO_TX":True,
    },sort_keys=True))
if __name__=="__main__":
    main()
