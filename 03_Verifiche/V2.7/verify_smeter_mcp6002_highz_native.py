#!/usr/bin/env python3
"""Native KiCad9 MCP6002 PDIP8 bench-only high-Z AM-envelope follower.

An actual MAIN RX/AGC source, reverse/overvoltage input protection, full
output stress qualification and moving-coil driver are NOT implemented.
"""
import math
import subprocess
import tempfile
from pathlib import Path
from verify_interboard_audio_contract_native import exported_nets,require

ROOT=Path(__file__).resolve().parents[2]
SCHEMATIC=ROOT/"04_KiCad/V2.7_DRAFT/SMETER_MCP6002_HIGHZ_BENCH/SMETER_MCP6002_HIGHZ_BENCH_V2_7_DRAFT.kicad_sch"
REFS={"U1901","J1901","J1902","J1903","R1901","R1902","R1903","C1901"}
EXPECTED={
 "AM_ENV_DC_BENCH":{("J1901","1"),("R1903","1")},
 "AM_ENV_AFTER_R1903":{("R1903","2"),("U1901","3"),("R1901","1")},
 "SMBUF_BENCH_GND":{("J1901","2"),("J1902","2"),("J1903","2"),("U1901","4"),("U1901","5"),("R1901","2"),("C1901","2")},
 "VLAB5_BUFFER":{("J1903","1"),("U1901","8"),("C1901","1")},
 "SMBUF_A_FB":{("U1901","1"),("U1901","2"),("R1902","1")},
 "SMBUF_B_FB":{("U1901","6"),("U1901","7")},
 "SMBUF_VOUT_BENCH":{("R1902","2"),("J1902","1")},
}

def main():
    s=SCHEMATIC.read_text(encoding="utf-8")
    # KiCad9 CLI recognizes project-local symbol tables only when the
    # same-basename .kicad_pro exists beside the standalone schematic.
    project=SCHEMATIC.with_suffix(".kicad_pro")
    assert project.is_file(),("Missing KiCad9 project for local symbols",project)
    table=(SCHEMATIC.parent/"sym-lib-table").read_text(encoding="utf-8")
    library=(SCHEMATIC.parent/"TH_SMETERBUF.kicad_sym").read_text(encoding="utf-8")
    assert '(name "TH_SMETERBUF")' in table
    assert 'KIPRJMOD}/TH_SMETERBUF.kicad_sym' in table
    for k in ("J","R","C","U"):
        assert '(symbol "'+k+'"' in library
    assert s.count("(symbol (lib_id ")==len(REFS)
    assert s.count('(property "Footprint" "Package_DIP:DIP-8_W7.62mm"')>=1
    assert s.count('(property "Footprint" "Resistor_THT:')>=3
    assert '(property "Value" "100k_1PCT_0P25W_INPUT_FAULT_LIMIT_CANDIDATE"' in s
    assert s.count('(property "Footprint" "Capacitor_THT:')>=1
    assert s.count('(property "Footprint" "Connector_PinHeader_2.54mm:')>=3
    assert 'MICROCHIP_MCP6002_I_P_PDIP8_CANDIDATE' in s
    assert '(property "Value" "22MEG_1PCT_BIAS_TO_GND_THT"' in s
    assert 'NO MAIN AGC/FSD' in s
    with tempfile.TemporaryDirectory(prefix="tht_mcp6002_highz_") as d:
        temp=Path(d)
        erc=temp/"erc.rpt"
        cp=subprocess.run(
            ["kicad-cli","sch","erc","--exit-code-violations","-o",str(erc),str(SCHEMATIC)],
            cwd=ROOT,capture_output=True,text=True)
        print("MCP6002_HIGHZ_ERC_STDOUT",cp.stdout,cp.stderr,flush=True)
        if erc.exists():
            print("MCP6002_HIGHZ_ERC_REPORT",erc.read_text(encoding="utf-8"),flush=True)
        cp.check_returncode()
        nets=exported_nets(SCHEMATIC,temp/"highz.net")
    assert set(nets)==set(EXPECTED),("Wrong native nets",nets.keys())
    for name,members in EXPECTED.items():
        require(nets,name,*sorted(members))
        assert set(nets[name])==members,("Unexpected pin-net assignment",name,nets[name])
    assert sum(len(members) for members in nets.values())==22
    # 22M passive shunt in parallel with idealized 47k detector: only
    # predicts nominal static DC loading, NOT opamp input leakage or PVT.
    rdet=47000
    rbias=22000000
    rseries=100000
    # The 100k series resistance lies upstream of the 22M input-bias
    # return; this is an ideal DC loading estimate, NOT ESD clamp testing.
    loss=rdet/(rdet+rbias+rseries)
    assert loss<0.003
    for v in (0.1,0.5,1,3,4):
        node=v*rbias/(rdet+rbias+rseries)
        assert math.isclose(node,v*(1-loss),rel_tol=1e-12)
    # If an IC clamp holds its input at the assumed rail+/-0.3V,
    # R1903 can LIMIT steady fault current; it does not prove safe
    # unpowered rail backfeed or protect against transients/ESD.
    hypothetical_faults=((20.0,5.0,0.3),(-20.0,0.0,-0.3),(20.0,0.0,0.3))
    for v_in,vdd,edge in hypothetical_faults:
        v_clamp=vdd+edge if v_in>vdd else edge
        i=abs(v_in-v_clamp)/rseries
        assert i<0.002,(v_in,vdd,i)
    print("MCP6002_HIGHZ_NATIVE",{"components":len(REFS),"nets":len(nets),
          "pins":22,"R_BIAS":rbias,"R_SERIES":rseries,"theoretical_R47k_load_loss_fraction":round(loss,7),
          "vendor_pinout_MCP6002_PDIP8":"1=OUTA 2=-A 3=+A 4=VSS 5=+B 6=-B 7=OUTB 8=VDD",
          "unqualified_input_ESD_OVP":True,
          "actual_RX_AGC_or_meter_driver":False},flush=True)
    print("PASS_KICAD9_MCP6002_PDIP8_THT_HIGHZ_BUFFER_ERC0_PINS22_LAB_ONLY_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
