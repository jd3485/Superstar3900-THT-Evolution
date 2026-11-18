#!/usr/bin/env python3
"""Native KiCad9 topology proof for two independent two-wire MAIN/FRONT audio links.

A shared FRONT AF_GND joins two previously disjoint MAIN return nets when
both cables are installed. This is a return bridge, NOT by itself a closed
ground loop; a loop needs another independently conductive path. All ties
here are passive ideal-net assumptions, not measured cable/RF impedances.
No real PCB, chassis, shield or grounds may be shorted based on this test.
"""
from pathlib import Path
import subprocess
import tempfile
from verify_interboard_audio_contract_native import exported_nets
from verify_main_front_dual_af_harness_native import (MAIN, FRONT, HARNESS,
                                                       EXPECTED, unique_net)

ROOT=Path(__file__).resolve().parents[2]
RETURNS={
    "MAIN_DEMOD_RETURN":("MAIN","J1502","2"),
    "FRONT_AF_GND":("FRONT","J1301","2"),
    "MAIN_LM386_RETURN":("MAIN","J1202","2"),
}
CABLE_RETURN_EDGES={
    "A_DEMOD":("MAIN_DEMOD_RETURN","FRONT_AF_GND"),
    "B_POSTMUTE":("FRONT_AF_GND","MAIN_LM386_RETURN"),
}
AUXILIARY_MAIN_TIE=("MAIN_DEMOD_RETURN","MAIN_LM386_RETURN")

def connectivity(edges):
    """Independent undirected graph calculation: components, cyclomatic rank."""
    nodes=set(RETURNS)
    parent={x:x for x in nodes}
    def root(x):
        while parent[x]!=x:
            x=parent[x]
        return x
    cycles=0
    for a,b in edges:
        ra,rb=root(a),root(b)
        if ra==rb:
            cycles+=1
        else:
            parent[ra]=rb
    components=len({root(x) for x in nodes})
    assert cycles==len(edges)-len(nodes)+components
    return components,cycles,root("MAIN_DEMOD_RETURN")==root("MAIN_LM386_RETURN")

def main():
    with tempfile.TemporaryDirectory(prefix="tht_af_return_graph_") as td:
        d=Path(td)
        nets={}
        for key,sch in (("MAIN",MAIN),("FRONT",FRONT),("HARNESS",HARNESS)):
            result=d/(key+".net")
            nets[key]=exported_nets(sch,result)
    assert nets["HARNESS"]==EXPECTED
    for name,(board,ref,pin) in RETURNS.items():
        assert len([n for n,m in nets[board].items() if (ref,pin) in m])==1,name
    main_if=unique_net(nets["MAIN"],("J1502","2"))
    main_lm=unique_net(nets["MAIN"],("J1202","2"))
    front_a=unique_net(nets["FRONT"],("J1301","2"))
    front_b=unique_net(nets["FRONT"],("J1902","2"))
    assert main_if.isdisjoint(main_lm),("MAIN returns unexpectedly joined on PCB",main_if&main_lm)
    assert front_a==front_b,("FRONT AF returns must be shared",front_a,front_b)
    assert ("J1501","2") in main_if and ("U1201","4") in main_lm
    assert ("RV1301","3") in front_a and ("J1902","2") in front_a

    # Verify actual cable mapping, not merely a manually invented graph.
    assert nets["HARNESS"]["AM455_TO_FRONT_VOLUME_RETURN"]=={
        ("J2701","2"),("J2702","2")}
    assert nets["HARNESS"]["FRONT_POSTMUTE_TO_MAIN_LM386_RETURN"]=={
        ("J2703","2"),("J2704","2")}
    # Do not allow a direct audio signal-to-return short or missing mute.
    for signal,ret in (
        ("AM455_TO_FRONT_VOLUME_AF","AM455_TO_FRONT_VOLUME_RETURN"),
        ("FRONT_POSTMUTE_TO_MAIN_LM386_AF",
         "FRONT_POSTMUTE_TO_MAIN_LM386_RETURN")):
        assert nets["HARNESS"][signal].isdisjoint(nets["HARNESS"][ret])
    assert unique_net(nets["FRONT"],("J1902","1")).isdisjoint(
        unique_net(nets["FRONT"],("J1302","1")))

    # Six deterministic scenarios: unplugged, each cable alone, both cables,
    # independent MAIN reference bridge alone, and both cables + that bridge.
    expected={
        (False,False,False):(3,0,False),
        (True,False,False):(2,0,False),
        (False,True,False):(2,0,False),
        (True,True,False):(1,0,True),
        (False,False,True):(2,0,True),
        (True,True,True):(1,1,True),
    }
    for (a,b,external),answer in expected.items():
        edges=[]
        if a:edges.append(CABLE_RETURN_EDGES["A_DEMOD"])
        if b:edges.append(CABLE_RETURN_EDGES["B_POSTMUTE"])
        if external:edges.append(AUXILIARY_MAIN_TIE)
        got=connectivity(edges)
        assert got==answer,(a,b,external,got,answer)
    # A single main chassis/shield return can be an additional path.
    # Whether such a path actually exists is NOT established by native CAD.
    assert connectivity(list(CABLE_RETURN_EDGES.values()))==(1,0,True)
    assert connectivity(list(CABLE_RETURN_EDGES.values())+
                        [AUXILIARY_MAIN_TIE])==(1,1,True)
    print("PASS_KICAD9_DUAL_AF_RETURN_GRAPH_6_SCENARIOS_CABLES_BRIDGE_MAIN_RETURNS_NO_INHERENT_CYCLE",{
        "actual_MAIN_return_net_partitions":2,
        "actual_FRONT_AF_ground_partition":1,
        "both_cable_returns_installed_connect_MAIN_returns":True,
        "both_cables_alone_form_closed_topological_loop":False,
        "additional_independent_MAIN_ground_bridge_would_form_cycle":True,
        "physical_shield_chassis_RFI_second_path_unknown":True,
        "connector_polarity_ground_impedance_load_EMC_unqualified":True,
        "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True},flush=True)

if __name__=="__main__":
    main()
