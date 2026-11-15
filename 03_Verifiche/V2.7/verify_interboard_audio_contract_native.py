#!/usr/bin/env python3
"""Verify the MAIN-audio ↔ FRONT-volume pin contract using *native* KiCad9 netlists.

These two DRAFT schematics are still isolated. The check documents the intended
two-wire harness; it does not assert that any cable, PCB, mating header or
mechanical integration exists. No FAB, TX, battery or vehicle approval.
"""
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
MAIN = ROOT / "04_KiCad/V2.7_DRAFT/AUDIO_RX_MONO_LM386_V2_7_DRAFT.kicad_sch"
FRONT = ROOT / "04_KiCad/V2.7_DRAFT/FRONT_VOLUME/FRONT_VOLUME_THT_V2_7_DRAFT.kicad_sch"
HARNESS = ROOT / "04_KiCad/V2.7_DRAFT/INTERBOARD_AUDIO_HARNESS_V2_7_DRAFT.kicad_sch"


def exported_nets(schematic, destination):
    subprocess.run(
        ["kicad-cli", "sch", "export", "netlist",
         "-o", str(destination), str(schematic)], cwd=ROOT, check=True)
    result = destination.read_text(encoding="utf-8")
    assert "(nets" in result, f"No netlist nets: {schematic}"
    tail = result.rsplit("(nets", 1)[1]
    # One KiCad (net (code ...) (name ...) block, followed by (node (ref ...) (pin ...)).
    headers = list(re.finditer(
        r'\(net\s+\(code\s+"?\d+"?\)\s+\(name\s+"([^"]+)"\)', tail))
    assert headers, ("No native named nets", schematic)
    nets = {}
    for i, match in enumerate(headers):
        segment = tail[match.end():headers[i + 1].start() if i + 1 < len(headers) else len(tail)]
        name = match.group(1).lstrip("/")
        members = set(re.findall(
            r'\(node\s+\(ref\s+"([^"]+)"\)\s+\(pin\s+"([^"]+)"\)', segment))
        assert name not in nets, ("Repeated net name", name)
        nets[name] = members
    return nets


def require(nets, name, *members):
    assert name in nets, ("Missing native net", name, sorted(nets))
    absent = set(members) - nets[name]
    assert not absent, ("Missing native connections", name, absent, sorted(nets[name]))


def main():
    with tempfile.TemporaryDirectory(prefix="tht_interboard_af_") as tmp:
        tmp = Path(tmp)
        front = exported_nets(FRONT, tmp / "front.net")
        main_nets = exported_nets(MAIN, tmp / "main.net")

    # FRONT: potentiometer terminal 1 receives detector audio;
    # terminal 2 is the wiper sent to the amplifier, terminal 3 is AF return.
    require(front, "DEMOD_AUDIO", ("J1301", "1"), ("RV1301", "1"))
    require(front, "VOL_WIPER_TO_AMP", ("RV1301", "2"), ("J1302", "1"))
    require(front, "AF_GND", ("J1301", "2"), ("RV1301", "3"), ("J1302", "2"))

    # MAIN audio: two-pin input J1202 takes the front-panel signal;
    # no power supply is carried over this cable.
    require(main_nets, "AUDIO_IN", ("J1202", "1"), ("C1201", "1"))
    require(main_nets, "GND", ("J1202", "2"), ("U1201", "4"))
    require(main_nets, "AUDIO_6V_LAB", ("J1201", "1"), ("U1201", "6"))
    assert ("J1302", "1") not in main_nets.get("AUDIO_6V_LAB", set())

    # The cable assignment is explicit and directional; connectors currently
    # use generic *male* THT pin headers, so mating/cable details are unqualified.
    harness = {
        ("J1302", "1"): ("J1202", "1"),
        ("J1302", "2"): ("J1202", "2"),
    }
    assert len(harness) == 2 and len(set(harness.values())) == 2
    print("FRONT_NETLIST:", {name: sorted(front[name])
                             for name in ("DEMOD_AUDIO", "VOL_WIPER_TO_AMP", "AF_GND")}, flush=True)
    print("MAIN_AUDIO_INPUT:", {name: sorted(main_nets[name])
                                for name in ("AUDIO_IN", "GND", "AUDIO_6V_LAB")}, flush=True)
    # A REAL KiCad9 standalone two-conductor drawing now records the
    # explicit pins in a single electrical netlist. It is a cable/electrical
    # abstraction, NOT a shield/polarization/contact manufacturing drawing.
    assert HARNESS.with_suffix(".kicad_pro").is_file()
    design=HARNESS.read_text(encoding="utf-8")
    assert design.count('(symbol (lib_id "TH_FRONT:AUDIO_2PIN")')==2
    for ref in ("J2401","J2402"):
        assert design.count('(property "Reference" "'+ref+'"')==1
    assert design.count("(wire (pts")==2
    assert "(global_label" not in design and "(power" not in design
    assert "NO FAB / NO TX" in design
    with tempfile.TemporaryDirectory(prefix="tht_audio_harness_") as td:
        d=Path(td)
        erc=d/"harness_erc.rpt"
        run=subprocess.run(["kicad-cli","sch","erc",
            "--exit-code-violations","-o",str(erc),str(HARNESS)],
            cwd=ROOT,capture_output=True,text=True,timeout=120)
        print("AUDIO_HARNESS_ERC_STDOUT",run.stdout,run.stderr,flush=True)
        if erc.exists():
            print("AUDIO_HARNESS_ERC_REPORT",erc.read_text(encoding="utf-8"),flush=True)
        run.check_returncode()
        h_nets=exported_nets(HARNESS,d/"harness.net")
    expected_harness={
        "AF_WIPER_LINK":{("J2401","1"),("J2402","1")},
        "AF_RETURN_LINK":{("J2401","2"),("J2402","2")},
    }
    assert set(h_nets)==set(expected_harness),(h_nets,expected_harness)
    for net,pins in expected_harness.items():
        assert h_nets[net]==pins,(net,h_nets[net],pins)
    assert set.union(*h_nets.values())=={
        ("J2401","1"),("J2401","2"),("J2402","1"),("J2402","2")}
    assert harness=={
        ("J1302","1"):("J1202","1"),
        ("J1302","2"):("J1202","2"),
    }
    print("PASS_KICAD9_RX_MAIN_FRONT_HARNESS_2CONDUCTOR_2NETS_4PINS_ERC0_NO_POWER_NO_FAB",flush=True)
    print("HARNESS_DRAFT_PIN_MAP:", harness, flush=True)
    print("PASS_KICAD9_NATIVE_MAIN_FRONT_AUDIO_PIN_CONTRACT_2_WIRE_DRAFT_NO_FAB", flush=True)


if __name__ == "__main__":
    main()
