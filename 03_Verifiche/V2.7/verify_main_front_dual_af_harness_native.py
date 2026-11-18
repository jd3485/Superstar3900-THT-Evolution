#!/usr/bin/env python3
"""Fail-closed physical-pin contract for TWO independent KiCad9 audio cable pairs.

MAIN J1502 -> FRONT J1301; FRONT J1902 (POST MUTE) -> MAIN J1202.
The native harness is an isolated cable drawing, NOT a product interboard
PCB or an authorization to bridge MAIN/FRONT GND. Shared FRONT AF_GND
can create a GROUND LOOP between two distinct MAIN returns when mated;
this risk remains open pending physical topology/EMC/ESD qualification.
"""
from pathlib import Path
import subprocess
import tempfile
from verify_interboard_audio_contract_native import exported_nets

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "04_KiCad/V2.7_DRAFT"
MAIN = BASE / "MAIN_RADIO_PARTIAL_V2_7_DRAFT.kicad_sch"
FRONT = BASE / "FRONT_CONTROL_PARTIAL_G5V1_SIXPIN_CANDIDATE.kicad_sch"
HARNESS = BASE / "MAIN_FRONT_DUAL_AF_HARNESS_V2_7_DRAFT.kicad_sch"

EXPECTED = {
    "AM455_TO_FRONT_VOLUME_AF": {("J2701","1"),("J2702","1")},
    "AM455_TO_FRONT_VOLUME_RETURN": {("J2701","2"),("J2702","2")},
    "FRONT_POSTMUTE_TO_MAIN_LM386_AF": {("J2703","1"),("J2704","1")},
    "FRONT_POSTMUTE_TO_MAIN_LM386_RETURN": {("J2703","2"),("J2704","2")},
}
LINKS = {
    ("J2701","1"):("MAIN","J1502","1"),
    ("J2701","2"):("MAIN","J1502","2"),
    ("J2702","1"):("FRONT","J1301","1"),
    ("J2702","2"):("FRONT","J1301","2"),
    ("J2703","1"):("FRONT","J1902","1"),
    ("J2703","2"):("FRONT","J1902","2"),
    ("J2704","1"):("MAIN","J1202","1"),
    ("J2704","2"):("MAIN","J1202","2"),
}

def unique_net(nets, endpoint):
    selected = [(name,pins) for name,pins in nets.items() if endpoint in pins]
    assert len(selected)==1,(endpoint,selected)
    return selected[0][1]

def main():
    text = HARNESS.read_text(encoding="utf8")
    assert HARNESS.with_suffix(".kicad_pro").exists()
    assert text.count('(symbol (lib_id "TH_FRONT:AUDIO_2PIN")')==4
    assert text.count('(wire (pts ')==4
    assert not any(tag in text for tag in ("(global_label", "(power "))
    assert "NO FAB / NO TX / NO BATTERIA / NO VEICOLO" in text
    assert "NO BYPASS J1302 TO J1202" in text
    for ref in ("J2701","J2702","J2703","J2704"):
        assert text.count('(property "Reference" "'+ref+'"')==1
    assert len(LINKS)==8 and len(set(LINKS.values()))==8
    assert {(v[0],v[1]) for v in LINKS.values()}=={
        ("MAIN","J1502"),("FRONT","J1301"),
        ("FRONT","J1902"),("MAIN","J1202")}
    for k,p in LINKS.items():
        assert k[1]==p[2],(k,p)  # no signal/return inversion
    with tempfile.TemporaryDirectory(prefix="tht_main_front_2af_") as temp:
        d=Path(temp)
        for design in (HARNESS,MAIN,FRONT):
            report=d/(design.stem+".erc")
            cp=subprocess.run(["kicad-cli","sch","erc","--exit-code-violations",
                "-o",str(report),str(design)],cwd=ROOT,capture_output=True,text=True,timeout=180)
            print("DUAL_AF_ERC",design.name,cp.stdout,cp.stderr,flush=True)
            if report.exists(): print("DUAL_AF_ERC_REPORT",design.name,
                report.read_text(encoding="utf8"),flush=True)
            cp.check_returncode()
        hn=exported_nets(HARNESS,d/"harness.net")
        mn=exported_nets(MAIN,d/"main.net")
        fn=exported_nets(FRONT,d/"front.net")
    assert hn==EXPECTED,(hn,EXPECTED)
    assert len(set.union(*hn.values()))==8
    for cable_pin,(board,ref,pin) in LINKS.items():
        n=mn if board=="MAIN" else fn
        assert unique_net(n,(ref,pin)),(cable_pin,board,ref,pin)
        assert any(cable_pin in members for members in hn.values())
    # Physical nets: AM detector output, separate return, FRONT volume
    # input, post-mute output and MAIN LM386 J1202/C1201 input.
    main_af=unique_net(mn,("J1502","1"))
    main_if_return=unique_net(mn,("J1502","2"))
    main_lm_af=unique_net(mn,("J1202","1"))
    main_lm_return=unique_net(mn,("J1202","2"))
    front_in=unique_net(fn,("J1301","1"))
    front_in_return=unique_net(fn,("J1301","2"))
    front_out=unique_net(fn,("J1902","1"))
    front_out_return=unique_net(fn,("J1902","2"))
    assert ("C1502","2") in main_af
    assert ("J1501","2") in main_if_return
    assert ("RV1301","1") in front_in
    assert ("R1901","1") in front_out and ("R1902","2") in front_out
    assert ("C1201","1") in main_lm_af
    assert ("U1201","4") in main_lm_return
    assert ("J1302","1") not in front_out  # no mute bypass
    assert main_af.isdisjoint(main_if_return)
    assert main_af.isdisjoint(main_lm_af)
    assert main_if_return.isdisjoint(main_lm_return)
    assert main_lm_af.isdisjoint(main_lm_return)
    assert front_in.isdisjoint(front_out)
    assert front_in_return==front_out_return  # shared FRONT AF_GND!
    assert ("J1302","2") in front_in_return
    # The two cable returns remain separate on the isolated cable drawing,
    # despite being joined on FRONT. Do not claim a physical star ground.
    assert hn["AM455_TO_FRONT_VOLUME_RETURN"].isdisjoint(
        hn["FRONT_POSTMUTE_TO_MAIN_LM386_RETURN"])
    print("PASS_KICAD9_MAIN_FRONT_TWO_AUDIO_PAIRS_4_NETS_8_PINS_3X_ERC0_NO_MUTE_BYPASS_NO_FAB",{
        "harness_four_separate_nets":True,
        "original_both_MAIN_returns_not_joined":True,
        "FRONT_AF_GND_SHARED_BETWEEN_TWO_CABLES":True,
        "physical_ground_loop_risk":True,
        "connector_mating_polarization_ESD_EMC_unqualified":True,
        "PCB_or_cable_manufacturable":False,
        "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True},flush=True)

if __name__=="__main__":
    main()
