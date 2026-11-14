#!/usr/bin/env python3
"""Native KiCad9 source-port contract + 12 ngspice Rg/R1/Rin bench checks.

No ceramic-filter transfer function, real mixer impedance, output filtering,
source available-power/NF claim, footprint assignment or PCB approval.
The 1.5k/2k resistors are *test-only input proxies* at 455 kHz.
"""
from pathlib import Path
import math
import subprocess
import tempfile
from verify_interboard_audio_contract_native import exported_nets,require
from verify_if455_two_port_source_impedance_native import TANK

ROOT=Path(__file__).resolve().parents[2]
MIXER=ROOT/"04_KiCad/V2.7_DRAFT/MIXER_SBL1_CANDIDATE/MIXER_SBL1_BENCH_THT_V2_7_DRAFT.kicad_sch"
F_IF=455000.0
RS_HYPOTHETICAL=(50.0,500.0,1500.0)
Z_FILTER_NOMINAL=(1500.0,2000.0)
MODES=("DIRECT_NO_R1","OEM_RG_PLUS_R1_EQUALS_NOMINAL")
def deck(source_r,target_z,series_r):
    lines=[
        "* IF455 matching measurement resistor-only reference; NOT ceramic model",
        "VSIGNAL src 0 DC 0 AC 1",
        f"RGEN src upstream {source_r:.12g}",
    ]
    if series_r>0:
        lines.append(f"R1 upstream pin1 {series_r:.12g}")
    else:
        # A native SPICE 0-ohm resistor is not used; direct net instead.
        lines[-1]=f"RGEN src pin1 {source_r:.12g}"
    lines += [
        f"R_FILTER_INPUT_PROXY pin1 0 {target_z:.12g}",
        ".control","set wr_singlescale",
        "ac lin 2 455000 455001",
        "wrdata input.dat vr(pin1) vi(pin1)",
        "quit",".endc",".end",""
    ]
    return "\n".join(lines)
def native_at_455(folder,source_r,target_z,series_r):
    file=folder/"bench.cir"
    file.write_text(deck(source_r,target_z,series_r),encoding="utf-8")
    proc=subprocess.run(["ngspice","-b","-o",str(folder/"ngspice.log"),str(file)],
                       cwd=folder,capture_output=True,text=True)
    proc.check_returncode()
    log=(folder/"ngspice.log").read_text(encoding="utf-8",errors="replace")
    assert "Error:" not in log and "fatal" not in log.lower(),log[-1500:]
    out=folder/"input.dat"
    assert out.is_file()
    rows=[list(map(float,s.split())) for s in out.read_text().splitlines() if s.strip()]
    assert 1<=len(rows)<=2,rows
    assert all(len(x)==3 and all(math.isfinite(y) for y in x) for x in rows)
    freq,vreal,vimag=rows[0]
    assert abs(freq-F_IF)<1 and abs(vimag)<1e-7,(freq,vreal,vimag)
    return vreal

def main():
    with tempfile.TemporaryDirectory(prefix="if455_fb455_termination_") as temp:
        tmp=Path(temp)
        m=exported_nets(MIXER,tmp/"mixer.net")
        tank=exported_nets(TANK,tmp/"tank.net")
        require(m,"IF455_MIXER_IF",("MX1701","3"),("MX1701","4"),("J1703","1"))
        require(m,"IF_BENCH_GND",("J1703","2"),("MX1701","2"))
        require(tank,"IF455_SOURCE",("J1601","1"),("C1601","1"))
        require(tank,"IF_BENCH_GND",("J1601","2"),("J1602","2"))
        # No OEM matching parts have been assigned to the actual candidate.
        assert m["IF455_MIXER_IF"]=={("MX1701","3"),("MX1701","4"),("J1703","1")}
        assert tank["IF455_SOURCE"]=={("J1601","1"),("C1601","1")}
        results={}
        for target in Z_FILTER_NOMINAL:
            for source in RS_HYPOTHETICAL:
                for mode in MODES:
                    r1=0.0 if mode=="DIRECT_NO_R1" else target-source
                    assert r1>=0
                    folder=tmp/f"z{int(target)}_rs{int(source)}_{mode}"
                    folder.mkdir()
                    observed=native_at_455(folder,source,target,r1)
                    # Independent exact Ohm's-law check with source=1V AC.
                    expected=target/(source+r1+target)
                    assert abs(observed-expected)<1e-7,(target,source,r1,observed,expected)
                    # Caution: power is for the resistive *dummy* only.
                    series_vs_dummy_db=20*math.log10(observed)
                    target_fraction=target/(source+r1+target)
                    assert abs(target_fraction-observed)<1e-7
                    if mode=="OEM_RG_PLUS_R1_EQUALS_NOMINAL":
                        assert abs(source+r1-target)<1e-9
                        assert abs(observed-0.5)<1e-7
                    record={"nominal_filter_port_ohm":target,
                            "hypothetical_mixer_Thevenin_R_ohm":source,
                            "bench_mode":mode,"test_only_R1_series_ohm":round(r1,6),
                            "dummy_filter_input_V_over_Vsource":round(observed,9),
                            "dummy_input_level_dBV_for_1V_source":round(series_vs_dummy_db,6),
                            "nominal_filter_output_load_ohm_NOT_MODELED":target,
                            "actual_ceramic_filter_frequency_response_modeled":False}
                    print("IF455_FB455_RESISTIVE_TERMINATION_NATIVE",record,flush=True)
                    results[(target,source,mode)]=observed
        assert len(results)==12
        for target in Z_FILTER_NOMINAL:
            for source in RS_HYPOTHETICAL:
                assert results[(target,source,"DIRECT_NO_R1")]>=(
                    results[(target,source,"OEM_RG_PLUS_R1_EQUALS_NOMINAL")])
        assert abs(results[(2000.,50.,"DIRECT_NO_R1")]-2000/2050)<1e-7
        assert abs(results[(2000.,50.,"OEM_RG_PLUS_R1_EQUALS_NOMINAL")]-0.5)<1e-7
        assert abs(results[(1500.,50.,"OEM_RG_PLUS_R1_EQUALS_NOMINAL")]-0.5)<1e-7
    print("PASS_NATIVE_KICAD9_IF455_12_NGSPICE_FB455_1500_2000_RG_R1_TEST_DUMMY_NO_VENDOR_TRANSFER_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
