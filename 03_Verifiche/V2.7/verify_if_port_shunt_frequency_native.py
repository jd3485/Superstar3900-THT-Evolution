#!/usr/bin/env python3
"""Native AC small-signal IF-port Z check for test-only shunt / RC branches.

The mixer is NOT modeled: a 1 A AC probe finds the passive load impedance.
Theoretical parallel-admittance superposition is independently checked against
ngspice at 455 kHz, 1 MHz, and 30 MHz. Ideal components at 30 MHz are NOT
validated RF parasitics or an OEM constant-impedance diplexer.
NO FAB / NO TX / NO BATTERY / NO VEHICLE.
"""
from pathlib import Path
import cmath
import math
import subprocess
import tempfile
from verify_interboard_audio_contract_native import exported_nets, require

ROOT=Path(__file__).resolve().parents[2]
MIXER=ROOT/"04_KiCad/V2.7_DRAFT/MIXER_SBL1_CANDIDATE/MIXER_SBL1_BENCH_THT_V2_7_DRAFT.kicad_sch"
TANK=ROOT/"04_KiCad/V2.7_DRAFT/IF455_TANK/IF455_TANK_THT_V2_7_DRAFT.kicad_sch"
FREQ_HZ=(455000,1000000,30000000)
CASES={"NONE":None,"R50":0,"R50_C100P":100e-12,"R50_C1N":1e-9}
PROBE_AC_A=1.0

def deck(freq,case):
    # Mirrors the nominal V2.7 IF455 passive trial; no measured coil RF Q,
    # no nonlinear mixer, and no high-frequency component parasitic models.
    lines=[
        "* Test-only IF455 input admittance; current probe is not mixer power",
        "IPROBE 0 port DC 0 AC 1",
        "C1601 port tank 10p",
        "L1601 tank ltail 1m",
        "RLOSS ltail 0 16.5",
        "C1602 tank 0 82p",
        "C1603 tank 0 30p",
        "R1601 tank 0 47k",
        "C1604 tank out 10p",
        "R1602 out 0 100k",
    ]
    if case=="R50":
        lines.append("RTERM port 0 50")
    elif case in ("R50_C100P","R50_C1N"):
        cap="100p" if case=="R50_C100P" else "1n"
        lines+=["RTERM port term 50",f"CTERM term 0 {cap}"]
    else:
        assert case=="NONE"
    lines += [
        ".control","set wr_singlescale",
        f"ac lin 2 {freq} {freq+1}",
        "wrdata zin.dat vr(port) vi(port)",
        "quit",".endc",".end",""
    ]
    return "\n".join(lines)

def get_z(folder,freq,case):
    file=folder/"load.cir"
    file.write_text(deck(freq,case),encoding="utf-8")
    out=subprocess.run(["ngspice","-b","-o",str(folder/"ngspice.log"),str(file)],
                       cwd=folder,capture_output=True,text=True)
    out.check_returncode()
    log=(folder/"ngspice.log").read_text(encoding="utf-8",errors="replace")
    assert "Error:" not in log and "fatal" not in log.lower(),log[-1800:]
    data=folder/"zin.dat"
    assert data.is_file(),("missing native AC data",freq,case)
    rows=[list(map(float,line.split())) for line in data.read_text().splitlines() if line.strip()]
    assert len(rows)==2,(freq,case,rows)
    for row in rows:
        assert len(row)==3 and all(math.isfinite(x) for x in row),(freq,case,row)
    assert abs(rows[0][0]-freq)<1,(freq,case,rows[0])
    z=complex(rows[0][1],rows[0][2])/PROBE_AC_A
    assert abs(z)>0 and math.isfinite(abs(z))
    return z

def branch_admittance(freq,case):
    if case=="NONE":return 0j
    if case=="R50":return 1/complex(50)
    cap=CASES[case]
    return 1/(50 + 1/(1j*2*math.pi*freq*cap))

def main():
    with tempfile.TemporaryDirectory(prefix="tht_if_diplexer_native_") as tmp:
        folder=Path(tmp)
        mx=exported_nets(MIXER,folder/"mixer.net")
        tank=exported_nets(TANK,folder/"tank.net")
        require(mx,"IF455_MIXER_IF",("MX1701","3"),("MX1701","4"),("J1703","1"))
        require(mx,"IF_BENCH_GND",("J1703","2"),("MX1701","2"))
        require(tank,"IF455_SOURCE",("J1601","1"),("C1601","1"))
        require(tank,"IF_BENCH_GND",("J1601","2"),("J1602","2"))
        assert mx["IF455_MIXER_IF"]=={
            ("MX1701","3"),("MX1701","4"),("J1703","1")}
        results={}
        for freq in FREQ_HZ:
            for case in CASES:
                job=folder/f"{freq}_{case}"
                job.mkdir()
                z=get_z(job,freq,case)
                results[freq,case]=z
                print("IF_PORT_TEST_ONLY_NATIVE_Z",{
                    "frequency_Hz":freq,"case":case,
                    "real_ohm":round(z.real,6),"imag_ohm":round(z.imag,6),
                    "abs_ohm":round(abs(z),6)},flush=True)
        assert len(results)==len(FREQ_HZ)*len(CASES)==12
        for freq in FREQ_HZ:
            z0=results[freq,"NONE"]
            for case in CASES:
                measured=1/results[freq,case]-1/z0
                theoretical=branch_admittance(freq,case)
                # Complex current/voltage AC (not a magnitude-only check).
                err=abs(measured-theoretical)
                assert err<max(5e-8,abs(theoretical)*1e-4),(
                    "native admittance disagrees with independent branch calculation",
                    freq,case,measured,theoretical,err)
                print("IF_PORT_PARALLEL_ADMITTANCE_INDEPENDENT_CHECK",{
                    "frequency_Hz":freq,"case":case,
                    "branch_real_S":round(measured.real,9),
                    "branch_imag_S":round(measured.imag,9),
                    "absolute_error_S":round(err,12)},flush=True)
        # A series 100pF + 50ohm branch cannot be a flat 50-ohm termination
        # at 455kHz; at 30MHz it still has a reactive part.
        y455=branch_admittance(455000,"R50_C100P")
        y30m=branch_admittance(30000000,"R50_C100P")
        assert abs(y455)<abs(y30m)
        assert abs(1/y455)>1000
        assert abs(1/y30m)>50
    print("PASS_NATIVE_KICAD9_IF_PORT_12_NGSPICE_COMPLEX_ADMITTANCE_CASES_NO_REAL_DIPLEXER_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
