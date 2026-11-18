#!/usr/bin/env python3
"""Nonqualifying 64-state topology screen anchored to actual KiCad9 FRONT hierarchy.
Models conductive contact reachability, NOT coil PVT or voltage attenuation.
"""
from pathlib import Path
import itertools
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets
from verify_front_g5v1_six_terminal_oem_pin_map_native import OEM_TO_EXISTING_NET
CAND=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_CONTROL_PARTIAL_G5V1_SIXPIN_CANDIDATE.kicad_sch"
PIN_TO_NET={str(pin):net for pin,net in OEM_TO_EXISTING_NET.items()}

def connected(edges,a,b):
    adjacency={}
    for x,y in edges:
        adjacency.setdefault(x,set()).add(y)
        adjacency.setdefault(y,set()).add(x)
    seen={a}
    queue=[a]
    while queue:
        current=queue.pop()
        if current==b:return True
        for nextnode in adjacency.get(current,()):
            if nextnode not in seen:
                seen.add(nextnode)
                queue.append(nextnode)
    return False

def main():
    with tempfile.TemporaryDirectory(prefix="g5v1_faultgraph_") as td:
        nets=exported_nets(CAND,Path(td)/"front.net")
    member_net={}
    for net,members in nets.items():
        for member in members:
            assert member not in member_net,(member,net)
            member_net[member]=net.rsplit("/",1)[-1]
    pins={p:member_net[("K1901",p)] for p in PIN_TO_NET}
    assert pins==PIN_TO_NET,(pins,PIN_TO_NET)
    assert member_net[("J1902","1")]=="AMP_INPUT_MUTED"
    assert member_net[("R1902","1")]=="RELAY_COM_AUDIO"
    assert member_net[("R1902","2")]=="AMP_INPUT_MUTED"
    assert member_net[("J1901","1")]=="VOL_WIPER_TO_AMP"
    assert member_net[("J1902","2")]=="AF_GND"
    assert member_net[("K1901","5")]==member_net[("K1901","6")]
    flags=("coil_on","nc_stuck_open","no_welded","com5_open","com6_open","ground_open")
    cases=0
    dangerous_source_while_coil_off=0
    lost_nc_ground_while_coil_off=0
    samples=[]
    for bits in itertools.product((False,True),repeat=len(flags)):
        x=dict(zip(flags,bits))
        edges=[("AMP_INPUT_MUTED","RELAY_COM_AUDIO")] # Native R1902 series resistor: topology only
        if not x["com5_open"]:
            edges.append(("RELAY_COM_AUDIO","OEM_INTERNAL_COM"))
        if not x["com6_open"]:
            edges.append(("RELAY_COM_AUDIO","OEM_INTERNAL_COM"))
        if (not x["coil_on"]) and (not x["nc_stuck_open"]):
            edges.append(("OEM_INTERNAL_COM","NC1"))
        if x["coil_on"] or x["no_welded"]:
            edges.append(("OEM_INTERNAL_COM","NO10"))
        if not x["ground_open"]:
            edges.append(("NC1","AF_GND"))
        edges.append(("NO10","VOL_WIPER_TO_AMP"))
        grounded=connected(edges,"AMP_INPUT_MUTED","AF_GND")
        source=connected(edges,"AMP_INPUT_MUTED","VOL_WIPER_TO_AMP")
        commons_ok=not (x["com5_open"] and x["com6_open"])
        oracle_ground=(not x["coil_on"] and not x["nc_stuck_open"] and
                       not x["ground_open"] and commons_ok)
        oracle_source=((x["coil_on"] or x["no_welded"]) and commons_ok)
        assert grounded==oracle_ground,(x,grounded,oracle_ground)
        assert source==oracle_source,(x,source,oracle_source)
        if not x["coil_on"] and source:
            dangerous_source_while_coil_off+=1
            if len(samples)<2:samples.append(x)
        if not x["coil_on"] and not grounded:
            lost_nc_ground_while_coil_off+=1
        cases+=1
    assert cases==64
    assert dangerous_source_while_coil_off>0
    assert lost_nc_ground_while_coil_off>0
    print("PASS_FRONT_G5V1_SIXPIN_NATIVE_64_FAULT_TOPOLOGY_SCREEN",{
      "cases":cases,
      "coil_off_source_continuity_cases":dangerous_source_while_coil_off,
      "coil_off_lost_NC_ground_cases":lost_nc_ground_while_coil_off,
      "hazard_examples":samples,
      "no_analog_voltage_or_contact_resistance_modeled":True,
      "coil_driver_PVT_qualified":False,
      "fail_safe_qualified":False,
      "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True},flush=True)
if __name__=="__main__":
    main()
