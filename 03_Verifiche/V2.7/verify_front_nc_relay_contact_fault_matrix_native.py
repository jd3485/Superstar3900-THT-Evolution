#!/usr/bin/env python3
"""Relay contact state-space fault screen, NOT physical relay or safe mute proof.

Compare two independently represented SPDT contact connectivity algorithms
against actual six KiCad9 exported nets (including R1902 series path).
Model 2 commands x 2 coil continuities x 4 mechanical contact conditions x
2 independent ground continuities x 2 volume-wiper continuities = 64 cases.
No OEM physical weld/open probability, debounce, minimum dry current, arc or
release time; front/MAIN product CAD untouched. NO FAB/NO TX.
"""
from __future__ import annotations
from itertools import product
from pathlib import Path
import tempfile
from verify_interboard_audio_contract_native import exported_nets, require

ROOT=Path(__file__).resolve().parents[2]
SCH=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_MUTE_NC_RELAY/FRONT_NC_MUTE_CONTACT_THT_V2_7_DRAFT.kicad_sch"
CONTACT_FAULTS=("free","welded_NO","welded_NC","open_contact")

def topology_edges(command:bool,coil_ok:bool,fault:str,gnd_ok:bool,volume_ok:bool):
    # Source wiper and external AF_GND are separate endpoints; actual relay
    # only connects COM to NC or COM to NO or disconnects COM.
    actual=("NO" if (command and coil_ok) else "NC") if fault=="free" else {
        "welded_NO":"NO","welded_NC":"NC","open_contact":"OPEN"}[fault]
    edges=set()
    if actual=="NC": edges.add(("COM","NC"))
    if actual=="NO": edges.add(("COM","NO"))
    if gnd_ok:edges.add(("NC","GROUND"))
    if volume_ok:edges.add(("NO","WIPER"))
    return edges

def paths_via_graph(edges):
    nodes=("COM","NC","NO","GROUND","WIPER")
    adjacency={v:set() for v in nodes}
    for a,b in edges:
        adjacency[a].add(b); adjacency[b].add(a)
    reached={"COM"}
    frontier=["COM"]
    while frontier:
        here=frontier.pop()
        for nxt in adjacency[here]-reached:
            reached.add(nxt);frontier.append(nxt)
    return ("GROUND" in reached,"WIPER" in reached)

def independent_contact_logic(command,coil_ok,fault,gnd_ok,volume_ok):
    # Algebraic boolean form, independent of graph-edge construction.
    can_nc=(not (command and coil_ok)) if fault=="free" else fault=="welded_NC"
    can_no=(command and coil_ok) if fault=="free" else fault=="welded_NO"
    return (can_nc and gnd_ok,can_no and volume_ok)

def main():
    with tempfile.TemporaryDirectory(prefix="tht_contact_fault_matrix_") as directory:
        nets=exported_nets(SCH,Path(directory)/"mute.net")
    # R1902/1 is on relay COM; its other pin joins LM386-side R1901/1.
    require(nets,"RELAY_COM_AUDIO",("K1901","1"),("R1902","1"))
    require(nets,"AMP_INPUT_MUTED",("R1902","2"),("J1902","1"),("R1901","1"))
    require(nets,"AF_GND",("K1901","2"),("J1902","2"),("J1901","2"),("R1901","2"))
    require(nets,"VOL_WIPER_TO_AMP",("K1901","3"),("J1901","1"))
    require(nets,"COIL_PLUS_LAB",("K1901","4"),("J1903","1"))
    require(nets,"COIL_MINUS_LAB",("K1901","5"),("J1903","2"))
    checked=0
    unexpected_mute_bypass=[]
    regular_muted=regular_audio=0
    for command,coil_ok,fault,gnd_ok,volume_ok in product(
        (False,True),(False,True),CONTACT_FAULTS,(False,True),(False,True)):
        edges=topology_edges(command,coil_ok,fault,gnd_ok,volume_ok)
        ground,audio=paths_via_graph(edges)
        assert (ground,audio)==independent_contact_logic(
            command,coil_ok,fault,gnd_ok,volume_ok)
        assert not(ground and audio),(command,coil_ok,fault,gnd_ok,volume_ok)
        if not command and audio:
            unexpected_mute_bypass.append((coil_ok,fault,gnd_ok,volume_ok))
        if fault=="free" and gnd_ok and volume_ok:
            if not command or not coil_ok:
                assert ground and not audio
                regular_muted+=1
            else:
                assert audio and not ground
                regular_audio+=1
        checked+=1
    assert len(nets)==6, sorted(nets)\n    assert checked==64 and regular_muted==3 and regular_audio==1
    assert len(unexpected_mute_bypass)==4
    assert all(fault=="welded_NO" and volume_ok
               for coil_ok,fault,gnd_ok,volume_ok in unexpected_mute_bypass)
    assert paths_via_graph(topology_edges(False,False,"free",True,True))==(True,False)
    assert paths_via_graph(topology_edges(False,False,"free",False,True))==(False,False)
    print("FRONT_NC_RELAY_FAULT_MATRIX",{
        "cases":checked,"normal_grounded_mute_cases":regular_muted,
        "normal_audio_enabled_cases":regular_audio,
        "command_mute_bypass_due_welded_NO":len(unexpected_mute_bypass),
        "single_fault_AF_GND_open_leaves_input_without_ground_bleed":True,
        "relay_open_contact_leaves_input_with_100k_bleed_if_ground_intact":True,
        "mechanical_NO_weld_bypasses_mute_during_off":True,
        "coil_stuck_energized_not_prevented_by_contact_only":True,
        "mechanical_contact_position_verified_by_OEM":False,
        "independent_failsafe_demonstrated":False,
        "NO_FAB_NO_TX":True},flush=True)
    print("PASS_KICAD9_FRONT_NC_RELAY_64_FAULT_STATE_GRAPH_BOOLEAN_NO_FAILSAFE_RELEASE",flush=True)

if __name__=="__main__":main()
