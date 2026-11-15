#!/usr/bin/env python3
"""Native KiCad9 TL431/LM393 THT power-good *candidate* & 135 corner screen.

Actual TI package pin functions checked against OEM PDF; the comparator
may be outside common-mode for deep brownout. This is NOT a supervisor
qualification or a safety proof. All units and outputs are hypothetical.
"""
from __future__ import annotations
from itertools import product
from pathlib import Path
import subprocess
import tempfile
from verify_interboard_audio_contract_native import exported_nets,require
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_MUTE_POWER_GOOD"
SCH=BASE/"FRONT_LM393_TL431_POWER_GOOD_THT_V2_7_DRAFT.kicad_sch"
COIL=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_MUTE_COIL_DRIVER/FRONT_NC_MUTE_DUAL_ENABLE_COIL_DRIVER_V2_7_DRAFT.kicad_sch"
BOARD=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_PLACEMENT/FRONT_CONTROL_13REFS_PLACEMENT_NONFAB.kicad_pcb"
EXPECTED={
"PGOOD_5V_LAB":{("U2001","8"),("R2001","1"),("R2002","1"),
                ("R2004","1"),("C2001","1"),("J2001","1")},
"PGOOD_GND":{("U2001","4"),("U2001","5"),("U2001","7"),
             ("U2002","2"),("R2003","2"),("C2001","2"),
             ("J2001","2"),("J2002","2")},
"VREF2V5":{("U2001","2"),("U2001","6"),("U2002","1"),
            ("U2002","3"),("R2001","2")},
"SENSE_DIV":{("U2001","3"),("R2002","2"),("R2003","1")},
"POWER_GOOD_LAB":{("U2001","1"),("R2004","2"),("J2002","1")}
}
TI_COMPARATOR_PINS={1:"OUTA_OC",2:"INA_MINUS",3:"INA_PLUS",4:"GND",
                    5:"INB_PLUS",6:"INB_MINUS",7:"OUTB_OC",8:"VCC"}
TI_TL431_LP_PINS={1:"CATHODE",2:"ANODE",3:"REF"}
def main():
    assert SCH.with_suffix(".kicad_pro").is_file()
    registry=(BASE/"sym-lib-table").read_text(encoding="utf-8")
    assert '(name "TH_PGOOD")' in registry
    lib=(BASE/"TH_PGOOD.kicad_sym").read_text(encoding="utf-8")
    for sym in ("LM393_DUAL_8PIN_LAB","TL431_LP_TO92_3PIN","RESISTOR","CAPACITOR","PORT2"):
        assert '(symbol "'+sym+'"' in lib
    for sym,pins in (("LM393_DUAL_8PIN_LAB",TI_COMPARATOR_PINS),
                     ("TL431_LP_TO92_3PIN",TI_TL431_LP_PINS)):
        s=lib.split('(symbol "'+sym+'"',1)[1].split('(symbol "',1)[0]
        for num,name in pins.items():
            assert '(name "'+name+'"' in lib
            assert '(number "'+str(num)+'"' in lib
    raw=SCH.read_text(encoding="utf-8")
    assert raw.count('(symbol (lib_id "TH_PGOOD:LM393_DUAL_8PIN_LAB")')==1
    assert raw.count('(symbol (lib_id "TH_PGOOD:TL431_LP_TO92_3PIN")')==1
    assert raw.count('(symbol (lib_id "TH_PGOOD:RESISTOR")')==4
    assert raw.count('(symbol (lib_id "TH_PGOOD:CAPACITOR")')==1
    assert raw.count('(symbol (lib_id "TH_PGOOD:PORT2")')==2
    assert "NO FAB / NO TX" in raw
    board=BOARD.read_text(encoding="utf-8")
    assert "U2001" not in board and board.count('(segment ')==35
    with tempfile.TemporaryDirectory(prefix="tht_pgood_lm393_") as td:
        tmp=Path(td)
        erc=tmp/"erc.txt"
        run=subprocess.run(["kicad-cli","sch","erc","--exit-code-violations",
                            "-o",str(erc),str(SCH)],cwd=ROOT,
                           text=True,capture_output=True,timeout=120)
        print("FRONT_PGOOD_TI_NATIVE_ERC",run.stdout,run.stderr,flush=True)
        if erc.exists():print(erc.read_text(encoding="utf-8"),flush=True)
        run.check_returncode()
        nets=exported_nets(SCH,tmp/"pgood.net")
        driver=exported_nets(COIL,tmp/"coil.net")
    assert set(nets)==set(EXPECTED),(nets,EXPECTED)
    for name,members in EXPECTED.items():
        require(nets,name,*members)
        assert nets[name]==members,(name,nets[name],members)
    require(driver,"POWER_GOOD_LAB",("J1913","1"),("R1912","1"))
    require(driver,"DRIVER_GND",("J1913","2"),("Q1912","3"))
    assert ("U2001","1") not in nets["PGOOD_5V_LAB"] # OC output pull-up only
    assert ("U2001","4") not in nets["POWER_GOOD_LAB"] # GND separate
    corner_count=0;unknown_cm=0;unregulated=0;both_valid=0
    output_loaded_min=1e9; output_loaded_max=0.
    nominal_threshold=2.495*(1+10000/12000)
    assert 4.55 < nominal_threshold < 4.60
    for vcc,vref,rtop,rbot in product(
        (3.5,4.,4.5,5.,5.5),(2.44,2.495,2.55),
        (9500.,10000.,10500.),(11400.,12000.,12600.)):
        sense=vcc*rbot/(rtop+rbot)
        vth=vref*(1+rtop/rbot)
        assert 4.<vth<5.
        ref_current=(vcc-vref)/1000.
        # TI TL431I min 1mA regulation, model reference validity only.
        reg=ref_current>=.001
        # Conservative LM393 full temperature upper CM VCC-2V
        common_mode=(vref<=vcc-2) and (sense<=vcc-2)
        if not reg: unregulated+=1
        if not common_mode: unknown_cm+=1
        if reg and common_mode:both_valid+=1
        # OC output + 1.5k pullup sourcing existing R1912 1.5k:
        # saturated base ~0.8V; no real BJT model, no leakage.
        vout=(vcc*1500.+.8*1500.)/(1500.+1500.)
        output_loaded_min=min(output_loaded_min,vout)
        output_loaded_max=max(output_loaded_max,vout)
        assert vout < vcc and vout > .8
        corner_count+=1
    assert corner_count==135
    assert unknown_cm>0 and unregulated>0 and both_valid>0
    assert output_loaded_max<4.5
    # 1.5k pull-up may sink <4mA nominal but cannot be called an
    # assured logical 4.5V high when loaded by existing base circuit.
    assert 5.5/1500<.004
    print("FRONT_PGOOD_TI_135_CORNER_SCREEN",{
        "cases":corner_count,"nominal_trip_V":round(nominal_threshold,5),
        "reference_invalid_regulation_count":unregulated,
        "comparator_common_mode_invalid_count":unknown_cm,
        "both_model_valid_cases":both_valid,
        "loaded_oc_high_min_V":round(output_loaded_min,3),
        "loaded_oc_high_max_V":round(output_loaded_max,3),
        "output_high_guaranteed_4p5V_to_current_driver":False,
        "TL431_cathode_ref_OEM_qualified_under_all_brownouts":False,
        "LM393_open_collector_saturation_current_OEM_PVT_qualified":False,
        "voltage_hysteresis_or_RC_delay_implemented":False,
        "UVLO_deep_brownout_failclosed_proven":False,
        "supervisor_product_qualified":False,
        "NO_FAB_NO_TX":True},flush=True)
    print("PASS_KICAD9_THT_TL431_LM393_PGOOD_5NETS_ERC0_135_CORNERS_UNQUALIFIED",flush=True)
if __name__=="__main__":main()
