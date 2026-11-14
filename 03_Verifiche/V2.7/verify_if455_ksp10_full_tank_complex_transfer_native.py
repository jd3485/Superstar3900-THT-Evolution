#!/usr/bin/env python3
"""Complex three-node IF455 tank/KSP10 transfer under GENERIC BJT corners.

72 actual ngspice AC solves on the SAME source, tank, and 6V KSP10 bench.
Not OEM BJT, mixer, filter, noise, selectivity or hardware qualification.
"""
import cmath
import math
from pathlib import Path
import subprocess
import tempfile

from verify_interboard_audio_contract_native import exported_nets, require
from verify_if455_two_port_source_impedance_native import TANK
from verify_if455_ksp10_generic_bjt_bias_ac import SCH as KSP10_SCH, BETAS
from verify_if455_j113_ksp10_shared_tank_native import circuit

FREQUENCIES=(445000,455000,465000)
CAPS_PF=(10,100,1000,10000)
LOADS=(1500,2000)
EXPECTED=len(FREQUENCIES)*len(CAPS_PF)*len(LOADS)*len(BETAS)

def solve(folder,beta,load,frequency,cap_pf):
    deck=circuit("KSP10",beta,load,cap_pf)
    old="ac lin 2 455000 455001"
    assert deck.count(old)==1
    deck=deck.replace(old,f"ac lin 2 {frequency} {frequency+1}")
    old="wrdata transfer.dat vm(out) vm(bufferout) vm(input)"
    assert deck.count(old)==1
    deck=deck.replace(old,"wrdata transfer.dat v(tank) v(out) v(bufferout)")
    source=folder/"study.cir"
    source.write_text(deck,encoding="utf-8")
    proc=subprocess.run(["ngspice","-b","-o",str(folder/"spice.log"),str(source)],
                        cwd=folder,capture_output=True,text=True)
    proc.check_returncode()
    log=(folder/"spice.log").read_text(encoding="utf-8",errors="replace")
    assert "Error:" not in log and "fatal" not in log.lower(),log[-1500:]
    rows=[tuple(map(float,line.split())) for line in
          (folder/"transfer.dat").read_text().splitlines() if line.strip()]
    assert 1<=len(rows)<=2 and all(len(row)==7 and all(math.isfinite(v) for v in row) for row in rows),rows
    f,tr,ti,orr,oi,br,bi=rows[0]
    assert abs(f-frequency)<1
    tank,port,buffer=complex(tr,ti),complex(orr,oi),complex(br,bi)
    assert abs(tank)>1e-12 and abs(port)>1e-12 and abs(buffer)>1e-12
    return tank,port,buffer

def main():
    sch=KSP10_SCH.read_text(encoding="utf-8")
    assert "ONSEMI_KSP10BU_TO92_CANDIDATE" in sch
    assert "2k2_EMITTER_SET_DRAFT" in sch
    results={}
    with tempfile.TemporaryDirectory(prefix="if455_complex_transfer_") as tmp:
        root=Path(tmp)
        knets=exported_nets(KSP10_SCH,root/"ksp10.net")
        tnets=exported_nets(TANK,root/"tank.net")
        require(knets,"IFBUF_BASE_BIAS",("Q1701","1"),("C1701","2"))
        require(knets,"IFBUF_EMITTER",("Q1701","2"),("R1703","1"))
        require(tnets,"IF455_SOURCE",("J1601","1"),("C1601","1"))
        require(tnets,"IF455_TANK",("C1601","2"),("L1601","1"))
        for beta in BETAS:
            for load in LOADS:
                for cap in CAPS_PF:
                    for freq in FREQUENCIES:
                        folder=root/f"b{beta}_l{load}_c{cap}_f{freq}"
                        folder.mkdir()
                        tank,port,buffer=solve(folder,beta,load,freq,cap)
                        ratio=buffer/tank
                        assert all(math.isfinite(x) for x in (ratio.real,ratio.imag,abs(ratio)))
                        results[(beta,load,cap,freq)]=(tank,port,buffer)
                        print("IF455_KSP10_COMPLEX_TANK_TO_BUFFER_NATIVE",{
                            "generic_beta":beta,"resistive_dummy_ohm":load,
                            "cap_pF":cap,"frequency_Hz":freq,
                            "tank_abs_VperV":round(abs(tank),9),
                            "port_abs_VperV":round(abs(port),9),
                            "buffer_abs_VperV":round(abs(buffer),9),
                            "buffer_over_tank_abs":round(abs(ratio),9),
                            "buffer_over_tank_phase_deg":round(math.degrees(cmath.phase(ratio)),6),
                            "OEM_or_noise_or_filter_qualified":False},flush=True)
        assert len(results)==EXPECTED,(len(results),EXPECTED)
        # Same source and resonant tank, so coupling effects must be
        # evaluated simultaneously at the tank and at the output.
        for beta in BETAS:
            for load in LOADS:
                a=results[beta,load,10,455000]
                b=results[beta,load,10000,455000]
                tank_ratio=abs(b[0]/a[0])
                output_ratio=abs(b[2]/a[2])
                assert math.isfinite(tank_ratio) and math.isfinite(output_ratio)
                assert abs(tank_ratio-1)>0.01,(beta,load,tank_ratio)
                print("IF455_KSP10_10NF_VS_10PF_COMPLEX_TRANSFER",{
                    "generic_beta":beta,"dummy_load_ohm":load,
                    "tank_voltage_ratio_10n_over_10p":round(tank_ratio,8),
                    "buffer_voltage_ratio_10n_over_10p":round(output_ratio,8),
                    "bandwidth_or_sensitivity_qualified":False},flush=True)
    print("PASS_NATIVE_KICAD9_KSP10_72_FULL_TANK_COMPLEX_TRANSFER_NGSPICE_NO_OEM_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
