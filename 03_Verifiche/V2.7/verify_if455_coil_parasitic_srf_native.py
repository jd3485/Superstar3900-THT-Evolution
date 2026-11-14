#!/usr/bin/env python3
"""Native IF455 coil parasitic capacitance sensitivity, NOT a part qualification.

The 1mH L1601 is modeled with hypothetical shunt Cp across the WHOLE lossy
coil branch (16.5-ohm DCR proxy). Native ngspice port Z is cross-checked
against independently derived complex nodal admittance at 3 frequencies.
No OEM SRF/Q, real 30MHz performance, mixer source, PCB or fabrication.
"""
from pathlib import Path
import cmath
import math
import subprocess
import tempfile

from verify_interboard_audio_contract_native import exported_nets, require

ROOT=Path(__file__).resolve().parents[2]
IF455=ROOT/"04_KiCad/V2.7_DRAFT/IF455_TANK/IF455_TANK_THT_V2_7_DRAFT.kicad_sch"
FREQ=(455000,1000000,30000000)
C_PAR_PF=(0.0,0.1,1.0,10.0)
L_H=1e-3
R_COIL=16.5

def native_spice(freq,cp_pf,folder):
    # All values are sandbox-only, mirroring the existing 10pF-coupled
    # IF455 tank 82pF+30pF, 47k damping and 10pF+100k output load.
    lines=[
        "* 1-A passive port admittance probe; no real mixer model",
        "IPROBE 0 port DC 0 AC 1",
        "C1601 port tank 10p",
        "L1601 tank ltail 1m",
        "RCOIL ltail 0 16.5",
        "C1602 tank 0 82p",
        "C1603 tank 0 30p",
        "R1601 tank 0 47k",
        "C1604 tank out 10p",
        "R1602 out 0 100k",
    ]
    if cp_pf:
        # Across tank-to-ground, in parallel with *series* L+R coil branch.
        lines.append(f"CP_COIL tank 0 {cp_pf}p")
    lines += [
        ".control", "set wr_singlescale",
        f"ac lin 2 {freq} {freq+1}",
        "wrdata portz.dat vr(port) vi(port)",
        "quit", ".endc", ".end", ""
    ]
    src=folder/"portz.cir"
    src.write_text("\n".join(lines),encoding="utf-8")
    log=folder/"ngspice.log"
    proc=subprocess.run(["ngspice","-b","-o",str(log),str(src)],
                        cwd=folder,capture_output=True,text=True)
    proc.check_returncode()
    report=log.read_text(encoding="utf-8",errors="replace")
    assert "Error:" not in report and "fatal" not in report.lower(),report[-1800:]
    path=folder/"portz.dat"
    assert path.is_file(),("No native SPICE output",freq,cp_pf)
    rows=[tuple(map(float,row.split())) for row in path.read_text().splitlines() if row.strip()]
    assert 1<=len(rows)<=2,(freq,cp_pf,rows)
    assert all(len(row)==3 and all(math.isfinite(v) for v in row) for row in rows)
    f,vreal,vimag=rows[0]
    assert abs(f-freq)<1,(freq,cp_pf,f)
    return complex(vreal,vimag)

def analytic_port(freq,cp_pf):
    w=2*math.pi*freq
    coil_z=R_COIL+1j*w*L_H
    out_z=100000+1/(1j*w*10e-12)
    y_tank=(1/coil_z + 1j*w*(112+cp_pf)*1e-12
            + 1/47000 + 1/out_z)
    return 1/(1j*w*10e-12) + 1/y_tank

def main():
    with tempfile.TemporaryDirectory(prefix="if455_coil_srf_") as tmp:
        root=Path(tmp)
        net=exported_nets(IF455,root/"if455.net")
        require(net,"IF455_SOURCE",("J1601","1"),("C1601","1"))
        require(net,"IF455_TANK",("C1601","2"),("L1601","1"),
                ("C1602","1"),("R1601","1"))
        require(net,"IF_BENCH_GND",("J1601","2"),("L1601","2"))
        sch=IF455.read_text(encoding="utf-8")
        assert '(property "Value" "1mH' in sch, "Tank inductor value changed; requalify model"
        results={}
        for cp in C_PAR_PF:
            # Self-resonance of isolated ideal L||Cp, not assembled tank passband.
            srf=None if cp==0 else 1/(2*math.pi*math.sqrt(L_H*cp*1e-12))
            if srf:
                assert srf>0
            print("IF455_COIL_IDEALIZED_ISOLATED_SRF",{
                "hypothetical_shunt_Cp_pF":cp,
                "idealized_isolated_L_par_Cp_SRF_Hz":None if srf is None else round(srf,1),
                "NOT_A_MEASURED_OEM_SRF":True},flush=True)
            for freq in FREQ:
                folder=root/f"cp{cp}_f{freq}"
                folder.mkdir()
                observed=native_spice(freq,cp,folder)
                expected=analytic_port(freq,cp)
                rel=abs(observed-expected)/abs(expected)
                assert rel<2e-5,(cp,freq,observed,expected,rel)
                assert math.isfinite(abs(observed)) and abs(observed)>0
                results[cp,freq]=observed
                print("IF455_COIL_PARASITIC_NATIVE_COMPLEX_Z",{
                    "hypothetical_Cp_pF":cp,"frequency_Hz":freq,
                    "port_Z_real_ohm":round(observed.real,6),
                    "port_Z_imag_ohm":round(observed.imag,6),
                    "port_Z_magnitude_ohm":round(abs(observed),6),
                    "independent_nodal_relative_error":round(rel,9)},flush=True)
    assert len(results)==12
    base455=results[0.0,455000]
    assert abs(base455-complex(18530.810505,-19747.334868))/abs(base455)<1e-5
    # Show that Cp is material at 30MHz; no 'ideal 1mH RF extrapolation' pass.
    assert abs(results[10.0,30000000]-results[0.0,30000000])>1
    print("PASS_NATIVE_KICAD9_IF455_COIL_12_PARASITIC_AC_COMPLEX_Z_CROSSCHECK_SRF_UNQUALIFIED_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
