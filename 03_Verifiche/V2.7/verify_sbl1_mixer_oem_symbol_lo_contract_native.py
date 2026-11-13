#!/usr/bin/env python3
"""Native KiCad9 symbol export plus OEM-derived SBL-1+ candidate pin/LO screening.

DO NOT assign any generic DIP8 footprint: A06 package's mechanical dimensions
are different. This is a LIBRARY component, not mixer-to-IF integrated circuit.
"""
from pathlib import Path
import math
import re
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[2]
LIB=ROOT/"04_KiCad/V2.7_DRAFT/MIXER_SBL1_CANDIDATE/SBL1_MIXER_OEM_PINOUT.kicad_sym"
TABLE=LIB.parent/"sym-lib-table"
IF455=ROOT/"04_KiCad/V2.7_DRAFT/IF455_TANK/IF455_TANK_THT_V2_7_DRAFT.kicad_sch"

# Mini-Circuits OEM SBL-1+ A06 pin function table.
PIN_MAP={"1":"RF","2":"GROUND","3":"IF_A","4":"IF_B",
         "5":"GROUND","6":"GROUND","7":"GROUND","8":"LO"}
LO_DBM=7.0 # Data sheet nominal level-7 LO drive. No LO budget margin assumed.
ZREF=50.0  # The 50 ohm power calculation is an external load assumption.
TYP_CONVERSION_LOSS_DB=5.6 # Nominal OEM only, not guaranteed at 27 MHz / 455 kHz IF.
MAX_CONVERSION_LOSS_DB=8.0 # Total range in OEM electrical table, setup-dependent.

def pin_extraction(source):
    pattern=(r'\(pin passive line \(at [-.\d]+ [-.\d]+ (?:0|90|180|270)\) '
             r'\(length [\d.]+\) \(name "([A-Z_]+)" '
             r'\(effects \(font \(size 1 1\)\)\)\) '
             r'\(number "(\d+)"')
    parsed=re.findall(pattern,source)
    return {num:name for name,num in parsed}

def main():
    s=LIB.read_text(encoding="utf-8")
    table=TABLE.read_text(encoding="utf-8")
    if455=IF455.read_text(encoding="utf-8")
    assert '(kicad_symbol_lib (version 20231120)' in s
    assert '(symbol "SBL-1_PLUS"' in s
    assert '(property "Value" "SBL-1+"' in s
    assert '(property "Footprint" ""' in s,("Unapproved A06 footprint accidentally assigned",LIB)
    assert "Connector" not in s and 'DIP-' not in s
    assert "MCL_SBL1_CANDIDATE" in table and LIB.name in table
    assert pin_extraction(s)==PIN_MAP,(pin_extraction(s),PIN_MAP)
    assert sum(1 for v in PIN_MAP.values() if v=="GROUND")==4
    # IEC double-balanced passive mixer has two physically separate IF pads.
    assert PIN_MAP["3"]=="IF_A" and PIN_MAP["4"]=="IF_B"
    assert 'IF pins 3+4 MUST be externally tied' in s
    assert 'label "IF455_SOURCE"' in if455 and 'label "IF_BENCH_GND"' in if455
    # +7 dBm in 50 ohms is 5.012 mW, Vrms 0.5006V and 1.416Vpp sine.
    p_w=1e-3*10**(LO_DBM/10)
    v_rms=math.sqrt(p_w*ZREF)
    v_pp=2*math.sqrt(2)*v_rms
    i_rms=v_rms/ZREF
    assert 0.0050<p_w<0.0051 and 0.50<v_rms<0.51
    assert 1.41<v_pp<1.43 and 0.0100<i_rms<0.0102
    # Conversion loss is specified as a POWER ratio under matched test
    # conditions; do not multiply a voltage at J1601 by this quantity.
    power_ratio_typ=10**(-TYP_CONVERSION_LOSS_DB/10)
    power_ratio_worst=10**(-MAX_CONVERSION_LOSS_DB/10)
    assert 0<power_ratio_worst<power_ratio_typ<1
    with tempfile.TemporaryDirectory(prefix="tht_sbl1_native_symbol_") as tmp:
        cmd=subprocess.run(["kicad-cli","sym","export","svg",
                            "--output",tmp,str(LIB)],
                           capture_output=True,text=True)
        assert cmd.returncode==0,("KiCad9 native symbol parser failed",cmd.stderr,cmd.stdout)
        svgs=list(Path(tmp).rglob("*.svg"))
        assert len(svgs)==1,("KiCad9 symbol export missing or unexpected",svgs,cmd.stdout)
        assert svgs[0].stat().st_size>500,("Invalid SVG export",svgs[0])
        print("SBL1_NATIVE_KICAD9_SYMBOL_EXPORT_PASS",svgs[0].name,
              "bytes",svgs[0].stat().st_size,flush=True)
    print("SBL1_OEM_PINOUT_CANDIDATE",PIN_MAP,flush=True)
    print("SBL1_LO_7DBM_50OHM_SOURCE_BUDGET_ASSUMED",{
        "LO_nominal_dBm":LO_DBM,"power_mW":round(p_w*1000,6),
        "load_ohms_ASSUMED":ZREF,
        "sine_Vrms":round(v_rms,6),"sine_Vpp":round(v_pp,6),
        "sine_Irms_mA":round(i_rms*1000,6),
        "LO_matching_and_available_drive_NOT_verified":True,
    },flush=True)
    print("SBL1_VENDOR_CONVERSION_LOSS_POWER_ONLY",{
        "typical_dB":TYP_CONVERSION_LOSS_DB,
        "max_total_range_dB":MAX_CONVERSION_LOSS_DB,
        "typical_matched_power_ratio":round(power_ratio_typ,6),
        "max_loss_matched_power_ratio":round(power_ratio_worst,6),
        "NOT_applicable_as_IF455_voltage_gain_without_actual_termination":True
    },flush=True)
    print("PASS_KICAD9_SBL1_OEM_8_PIN_A06_SYMBOL_LO_POWER_CONTRACT_NO_FOOTPRINT_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":main()
