#!/usr/bin/env python3
"""KiCad9 native verification for isolated FRONT LED illumination bench.

Bench only; J2201 5V laboratory supply is NOT a qualified MAIN/FRONT
interface. RED 5mm LED Vf, intensity, ESD, panel fit, EMC and current are
unqualified. No production board exists; no PCB DRC claim.
"""
from pathlib import Path
import subprocess
import tempfile
from verify_interboard_audio_contract_native import exported_nets,require
from verify_front_illum_lab_pcb_native import main as verify_bench_pcb_drc

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_ILLUM_BENCH"
SCH=BASE/"FRONT_ILLUM_BENCH_V2_7_DRAFT.kicad_sch"
EXPECTED={
    "ILLUM_5V_LAB":{("J2201","1"),("R2201","1"),("R2202","1")},
    "ILLUM_RETURN_LAB":{("J2201","2"),("D2201","1"),("D2202","1")},
    "ILLUM_LED1_A":{("R2201","2"),("D2201","2")},
    "ILLUM_LED2_A":{("R2202","2"),("D2202","2")},
}


def main():
    s=SCH.read_text(encoding="utf-8")
    lib=(BASE/"TH_FRONT_ILLUM.kicad_sym").read_text(encoding="utf-8")
    assert (BASE/"sym-lib-table").is_file()
    assert (BASE/"FRONT_ILLUM_BENCH_V2_7_DRAFT.kicad_pro").is_file()
    assert "TH_FRONT_ILLUM.kicad_sym" in (BASE/"sym-lib-table").read_text(encoding="utf-8")
    assert s.count('(symbol (lib_id "TH_FRONT_ILLUM:')==5
    assert s.count("(wire (pts")==10 and s.count('(label "')==10
    assert "NO FAB / NO TX" in s
    for ref in ("J2201","R2201","R2202","D2201","D2202"):
        assert s.count('(property "Reference" "'+ref+'"')==1,ref
    for fp,n in (
        ("TH_FRONT_ILLUM_LAB:LAB_HEADER_2P54",2),
        ("TH_FRONT_ILLUM_LAB:LAB_RESISTOR_7P62",3),
        ("TH_FRONT_ILLUM_LAB:LAB_LED_2P54",3)):
        # one embedded symbol default plus one footprint per placement
        assert s.count(fp)==n,(fp,s.count(fp),n)
        assert fp in lib
    assert (BASE/"fp-lib-table").is_file()
    assert (BASE/"TH_FRONT_ILLUM_LAB.pretty/LAB_HEADER_2P54.kicad_mod").is_file()
    assert (BASE/"TH_FRONT_ILLUM_LAB.pretty/LAB_RESISTOR_7P62.kicad_mod").is_file()
    assert (BASE/"TH_FRONT_ILLUM_LAB.pretty/LAB_LED_2P54.kicad_mod").is_file()
    assert '(symbol "LED"' in lib
    assert '(name "A" (effects (font (size 1 1)))) (number "2"' in lib
    assert '(name "K" (effects (font (size 1 1)))) (number "1"' in lib
    assert s.count("680R_0P25W_THT_CANDIDATE")==2
    # Illustrative nominal current only: NEVER use as OEM LED requirement.
    # At VDD5 and assumed red LED Vf=2V (no pulsing/dimming), I=4.41mA.
    # Resistance 680R candidate at VDD=5.5V and Vfmin=1.6V -> 5.74mA
    # per LED; dissipation <0.023W ideal, not a thermal qualification.
    nominal=(5.0-2.0)/680.0
    stress=(5.5-1.6)/680.0
    assert 0.004 < nominal < 0.005
    assert 0.005 < stress < 0.006
    assert (stress**2)*680 < 0.025
    with tempfile.TemporaryDirectory(prefix="tht_front_illum_") as temp:
        report=Path(temp)/"erc.rpt"
        cp=subprocess.run(["kicad-cli","sch","erc","--exit-code-violations",
                           "-o",str(report),str(SCH)],cwd=ROOT,
                          capture_output=True,text=True,timeout=120)
        print("FRONT_ILLUM_ERC_STDOUT",cp.stdout,cp.stderr,flush=True)
        if report.exists():
            print("FRONT_ILLUM_ERC_REPORT",report.read_text(encoding="utf-8"),flush=True)
        cp.check_returncode()
        nets=exported_nets(SCH,Path(temp)/"illum.net")
    assert set(nets)==set(EXPECTED),(set(nets),set(EXPECTED))
    for n,members in EXPECTED.items():
        require(nets,n,*sorted(members))
        assert set(nets[n])==members,(n,nets[n],members)
    assert sum(map(len,nets.values()))==10
    print("FRONT_ILLUM_KICAD9_BENCH",{"refs":5,"nets":4,"pin_endpoints":10,
         "two_independent_LED_current_resistors":True,
         "estimated_current_nominal_mA":round(nominal*1000,3),
         "estimated_5p5V_Vf1p6_mA":round(stress*1000,3),
         "LED_OEM_mechanics_qualified":False,
         "power_source_5V_and_interboard_qualified":False,
         "FRONT_product_PCB_created":False,
         "NO_FAB_NO_TX":True},flush=True)
    print("PASS_KICAD9_FRONT_LED_ILLUM_THT5_NETS4_PINS10_ERC0_LAB_ONLY_NO_FAB_NO_TX",flush=True)
    verify_bench_pcb_drc()


if __name__=="__main__":
    main()
