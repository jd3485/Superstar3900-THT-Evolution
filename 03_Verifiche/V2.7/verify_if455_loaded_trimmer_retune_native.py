#!/usr/bin/env python3
"""Native ngspice 455 kHz trimmer retune study with realistic explicit
passive downstream port loads, not a receiver or OEM RF qualification.

36 independent AC simulations: 4 loads x 9 EW candidate settings 10..50pF.
Measure true fpeak and attenuation at exact 455kHz; never infer SNR/THD.
"""
from pathlib import Path
import math
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[2]
PRIOR=ROOT/"03_Verifiche/V2.7/RAPPORTO_IF455_PORT_Z_COMPLESSA_BANDA_AC_DRAFT.md"
TANK=ROOT/"04_KiCad/V2.7_DRAFT/IF455_TANK/IF455_TANK_THT_V2_7_DRAFT.kicad_sch"
TRIMS=(10,15,20,25,30,35,40,45,50)
CASES=(
    ("100k_reference",""),
    ("shunt_10k","R_ADD out 0 10k"),
    ("shunt_1k","R_ADD out 0 1k"),
    ("JFET_PASSIVE_GATE_SURROGATE","C_GATE_IN out gate 10p\nR_GATE_DC gate 0 1Meg\nC_GATE_PAR gate 0 7p"),
)
N=1001
FSTART=350000
FSTOP=550000
OLD_PEAK={"100k_reference":454750,"shunt_10k":440250,
          "shunt_1k":439000,"JFET_PASSIVE_GATE_SURROGATE":450250}
OLD_455={"100k_reference":0.835055562,"shunt_10k":0.180771862,
         "shunt_1k":0.022073671,"JFET_PASSIVE_GATE_SURROGATE":0.665186786}

def actual_ac(folder,case,trim,load):
    folder.mkdir()
    circuit=f"""* Real native ngspice IF455 passive load-dependent trimmer retune.
* Lcoil 1mH; Rloss 16.5ohm AC ASSUMPTION (NOT vendor guaranteed).
.title IF455 tank trimmer sensitivity generic no OEM RF signoff
VSOURCE src 0 DC 0 AC 1
RGEN src gen 50
C1601 gen tank 10p
L1601 tank coil_tail 1m
RCOIL coil_tail 0 16.5
C1602 tank 0 82p
CTRIM tank 0 {trim}p
R1601 tank 0 47k
C1604 tank out 10p
R1602 out 0 100k
{load}
.control
set wr_singlescale
ac lin {N} {FSTART} {FSTOP}
wrdata transfer.dat vm(out)
quit
.endc
.end
"""
    path=folder/"actual.cir"
    logpath=folder/"native.log"
    path.write_text(circuit,encoding="utf-8")
    run=subprocess.run(["ngspice","-b","-o",str(logpath),str(path)],
                       cwd=folder,capture_output=True,text=True)
    log=logpath.read_text(encoding="utf-8",errors="replace") if logpath.exists() else ""
    run.check_returncode()
    assert "Error:" not in log and "fatal" not in log.lower(),log[-1200:]
    data=folder/"transfer.dat"
    assert data.is_file(),log[-1200:]
    rows=[]
    for line in data.read_text(encoding="utf-8").splitlines():
        try: row=tuple(float(x) for x in line.split())
        except ValueError:continue
        if row:
            assert len(row)==2 and all(math.isfinite(v) for v in row),row
            rows.append(row)
    assert len(rows)==N,(case,trim,len(rows))
    idx455=round((455000-FSTART)*(N-1)/(FSTOP-FSTART))
    assert abs(rows[idx455][0]-455000)<1
    idxpeak=max(range(N),key=lambda i:rows[i][1])
    return rows[idxpeak][0],rows[idxpeak][1],rows[idx455][1]

def main():
    schema=TANK.read_text(encoding="utf-8")
    report=PRIOR.read_text(encoding="utf-8")
    assert "EW_GKG50015_10to50pF_THT_CANDIDATE_TRIM" in schema
    assert "16,5Ω" in report and "100k" in report
    assert set(OLD_PEAK)=={name for name,_ in CASES}
    results=[]
    with tempfile.TemporaryDirectory(prefix="tht_if455_load_retune_") as td:
        root=Path(td)
        for case,load in CASES:
            samples=[]
            for trim in TRIMS:
                peak_freq,peak_transfer,at455=actual_ac(
                    root/(case+"_"+str(trim)+"pF"),case,trim,load)
                row={"load_case":case,"trimmer_pF":trim,
                     "peak_frequency_Hz":round(peak_freq,1),
                     "peak_transfer_per_1V":round(peak_transfer,9),
                     "transfer_at_455k_per_1V":round(at455,9)}
                samples.append(row)
                print("IF455_NATIVE_LOAD_TRIM_AC_CASE",row,flush=True)
                assert 0<at455 and 0<peak_transfer
                assert peak_transfer>=at455
                if trim==30:
                    assert abs(peak_freq-OLD_PEAK[case])<=350,(case,peak_freq)
                    assert abs(at455-OLD_455[case])/OLD_455[case]<0.01,(
                        "PR110 AC load baseline drift",case,at455)
            assert len(samples)==len(TRIMS)
            assert samples[0]["peak_frequency_Hz"]>samples[-1]["peak_frequency_Hz"],(
                "Trimmer tuning direction physically unexpected",case)
            strongest=max(samples,key=lambda r:r["transfer_at_455k_per_1V"])
            closest=min(samples,key=lambda r:abs(r["peak_frequency_Hz"]-455000))
            original=next(r for r in samples if r["trimmer_pF"]==30)
            print("IF455_NATIVE_LOAD_TRIM_AC_OPTIMUM",{
                "load_case":case,
                "best_455k_transfer_trim_pF":strongest["trimmer_pF"],
                "best_455k_transfer":strongest["transfer_at_455k_per_1V"],
                "gain_vs_30p_at_455k":round(strongest["transfer_at_455k_per_1V"]/
                                           original["transfer_at_455k_per_1V"],6),
                "closest_peak_455k_trim_pF":closest["trimmer_pF"],
                "closest_peak_Hz":closest["peak_frequency_Hz"],
                "reference_30p_peak_Hz":original["peak_frequency_Hz"],
                "OEM_Q_ESR_AND_PCB_NOT_QUALIFIED":True},flush=True)
            results+=samples
    assert len(results)==36
    print("PASS_NGSPICE_IF455_36_REAL_TRIM_LOAD_AC_CASES_UNQUALIFIED_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
