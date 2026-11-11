#!/usr/bin/env python3
"""V2.7 pre-CAD fault contract for INDEPENDENT series power-good path.
Models logic only: NO transistor behavior, no component qualification, no PCB.
Tests actual KiCad V2.6 native netlist of still-unprotected primary path.
"""
import argparse,json,runpy
from itertools import product
from pathlib import Path

SINGLE_FAULTS=(
 "HEALTHY","Q802_CE_SHORT","Q803_CE_SHORT","Q801_DS_SHORT",
 "Q804_DS_SHORT","PRIMARY_OVP_STUCK_ALLOW","PRIMARY_UVLO_STUCK_ALLOW",
 "SECONDARY_OVP_STUCK_ALLOW","SECONDARY_UVLO_STUCK_ALLOW",
 "SECONDARY_DRIVER_STUCK_ALLOW","PRIMARY_REF_STUCK_ALLOW",
 "SECONDARY_REF_STUCK_ALLOW",
)

def decision(ovp_ok,uvlo_ok,fault):
    # Both supervisors must be independent in the REAL circuit.
    p_ovp=ovp_ok or fault in ("Q802_CE_SHORT","PRIMARY_OVP_STUCK_ALLOW")
    p_uvlo=uvlo_ok or fault in ("Q803_CE_SHORT","PRIMARY_UVLO_STUCK_ALLOW")
    s_ovp=ovp_ok or fault=="SECONDARY_OVP_STUCK_ALLOW"
    s_uvlo=uvlo_ok or fault=="SECONDARY_UVLO_STUCK_ALLOW"
    primary=p_ovp and p_uvlo
    second=s_ovp and s_uvlo
    if fault in ("Q801_DS_SHORT","PRIMARY_REF_STUCK_ALLOW"):
        primary=True
    if fault in ("Q804_DS_SHORT","SECONDARY_DRIVER_STUCK_ALLOW",
                 "SECONDARY_REF_STUCK_ALLOW"):
        second=True
    return primary,second,primary and second

def check_native(filename):
    ns=runpy.run_path(str(Path(__file__).resolve().parents[2]/
                   "03_Verifiche/V1.0/verify_kicad_netlist_v10.py"))["read_nets"](Path(filename))
    assert len(ns)==76,len(ns)
    def net(part):
        items=[name for name,pins in ns.items() if part in pins]
        assert len(items)==1,(part,items)
        return items[0]
    assert net(("Q802","3"))==net(("R1009","2"))
    assert net(("Q802","1"))==net(("Q803","3"))
    assert net(("Q803","1"))==net(("U801","4"))
    assert net(("R1009","1"))==net(("D803","2"))
    # This deliberately describes the *current* incomplete circuit:
    # second series switch Q804 is NOT in actual V2.6 CAD yet.
    assert not any(("Q804",str(i)) in pins for pins in ns.values() for i in range(1,5))
    return len(ns)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("native_netlist",nargs="?")
    p.add_argument("--math-only",action="store_true")
    args=p.parse_args()
    assert args.math_only==(args.native_netlist is None)
    rows=[]
    for ov,uv,f in product((False,True),(False,True),SINGLE_FAULTS):
        primary,secondary,both=decision(ov,uv,f)
        unsafe=not(ov and uv)
        rows.append((ov,uv,f,primary,secondary,both,unsafe))
    assert len(rows)==48
    assert all(row[5]==(row[0] and row[1]) for row in rows if row[2]=="HEALTHY")
    primary_bypass=[row for row in rows if row[3] and row[6]]
    both_bypass=[row for row in rows if row[5] and row[6]]
    assert len(primary_bypass)>0,primary_bypass
    assert both_bypass==[],both_bypass
    assert any(row[2]=="Q802_CE_SHORT" and row[3] and row[6] for row in primary_bypass)
    assert any(row[2]=="Q803_CE_SHORT" and row[3] and row[6] for row in primary_bypass)
    # Explicitly model one UNMITIGATED common-cause dual fault.
    common_cause_bypass=sum(
        (not(ov and uv)) and True and True
        for ov,uv in product((False,True),repeat=2))
    assert common_cause_bypass==3
    native=None if args.math_only else check_native(args.native_netlist)
    print(json.dumps({
      "gate":"PASS_PRE_CAD_INDEPENDENT_SECOND_SWITCH_LOGIC_CONTRACT_NOT_HARDWARE_APPROVAL",
      "single_fault_cases":len(rows),"native_v26_net_groups":native,
      "existing_primary_unsafe_bypass_rows":len(primary_bypass),
      "proposed_two_independent_series_paths_unsafe_bypass_rows":len(both_bypass),
      "common_cause_stuck_allow_bypass_rows":common_cause_bypass,
      "secondary_powergood_actuator_physically_present":False,
      "second_supervisor_independence_verified":False,
      "no_new_component_MPN_selected":True,
      "not_a_v27_kicad_revision":True,
      "NO_FAB":True,"NO_TX":True
    },sort_keys=True))
if __name__=="__main__":
    main()
