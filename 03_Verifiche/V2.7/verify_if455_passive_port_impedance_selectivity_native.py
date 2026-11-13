#!/usr/bin/env python3
"""Native ngspice output-port Z and frequency-response characterization of
isolated KiCad9 IF455 tank, with explicit passive load surrogates.

No transfer to antenna input, active J113 model, diode OEM, receiver selectivity,
IF gain, noise figure or hardware performance is justified by this bench.
"""
from pathlib import Path
import math
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[2]
SCH=ROOT/"04_KiCad/V2.7_DRAFT/IF455_TANK/IF455_TANK_THT_V2_7_DRAFT.kicad_sch"
REFERENCE_DECK=ROOT/"03_Verifiche/V2.7/spice/if455_downstream_input_load_ac.cir"
FSTART,FSTOP,N=300000,650000,1401
CASES=(
    ("original_100k_only", ""),
    ("shunt_10k", "R_EXTRA out 0 10k"),
    ("shunt_1k", "R_EXTRA out 0 1k"),
    ("JFET_GATE_GENERIC_PASSIVE", "C_GIN out gate 10p\nR_GLEAK gate 0 1Meg\nC_GPAR gate 0 7p"),
)
# These are not gain and impedance of a real J113; just static RF port load.
CONTRACT=(
    "C1601 gen tank 10p", "L1601 tank ltail 1m",
    "RL_COIL ltail 0 16.5", "C1602 tank 0 82p",
    "CTRIM tank 0 30p", "R1601 tank 0 47k",
    "C1604 tank out 10p", "R1602 out 0 100k",
    "RGEN src gen 50",
)

def run_spice(path,folder,label):
    logpath=folder/(label+".log")
    cmd=subprocess.run(["ngspice","-b","-o",str(logpath),str(path)],
                       cwd=folder,capture_output=True,text=True)
    log=logpath.read_text(encoding="utf-8",errors="replace") if logpath.exists() else ""
    cmd.check_returncode()
    assert "Error:" not in log and "fatal" not in log.lower(),log[-1600:]
    data=folder/(label+".dat")
    assert data.exists(),("Native ngspice output missing",label,log[-1000:])
    out=[]
    for line in data.read_text(encoding="utf-8").splitlines():
        try:
            row=tuple(float(x) for x in line.split())
        except ValueError:
            continue
        if row:
            assert len(row)==3,(label,row)
            assert all(math.isfinite(x) for x in row),(label,row)
            out.append((row[0],complex(row[1],row[2])))
    assert len(out)==N,(label,len(out))
    assert abs(out[0][0]-FSTART)<1 and abs(out[-1][0]-FSTOP)<1
    for i,(freq,_) in enumerate(out):
        assert abs(freq-(FSTART+(FSTOP-FSTART)*i/(N-1)))<2,(label,i,freq)
    return out

def crossing(left,right,limit):
    f1,z1=left;f2,z2=right
    a1=abs(z1);a2=abs(z2)
    if a2==a1:return f1
    return f1+(limit-a1)*(f2-f1)/(a2-a1)

def bandwidth(rows):
    magnitudes=[abs(v) for _,v in rows]
    index=max(range(len(rows)),key=lambda i:magnitudes[i])
    peak=magnitudes[index]
    threshold=peak/math.sqrt(2)
    below=[i for i in range(index-1,-1,-1) if magnitudes[i]<threshold]
    above=[i for i in range(index+1,len(rows)) if magnitudes[i]<threshold]
    assert below and above,("Cannot bracket -3dB bandwidth",rows[index],peak)
    lo=below[0];hi=above[0]
    left=crossing(rows[lo],rows[lo+1],threshold)
    right=crossing(rows[hi-1],rows[hi],threshold)
    return rows[index][0],peak,left,right,right-left

def main():
    schematic=SCH.read_text(encoding="utf-8")
    legacy=REFERENCE_DECK.read_text(encoding="utf-8")
    assert "82pF_C0G_THT" in schematic and "EW_GKG50015" in schematic
    for token in ("C1601_UNLOADED gen_UNLOADED tank_UNLOADED 10p",
                  "L1601_UNLOADED tank_UNLOADED ltail_UNLOADED 1m",
                  "RL_UNLOADED ltail_UNLOADED 0 16.5",
                  "CTRIM_UNLOADED tank_UNLOADED 0 30p",
                  "R1602_UNLOADED out_UNLOADED 0 100k"):
        assert token in legacy,("Model reference changed",token)
    table=[]
    with tempfile.TemporaryDirectory(prefix="tht_if455_port_z_") as t:
        base=Path(t)
        for case,extra in CASES:
            folder=base/case
            folder.mkdir()
            results=[]
            for mode in ("transfer","port_z"):
                source=("VSOURCE src 0 DC 0 AC 1\n" if mode=="transfer"
                        else "VSOURCE src 0 DC 0 AC 0\nIPROBE 0 out DC 0 AC 1\n")
                circuit="\n".join((
                    "* IF455 passive tank AC + output test port (not full RF receiver)",
                    "* 1mH DCR16.5 ohm AS RF loss, no measured Q or OEM model.",
                    ".title IF455 output impedance and selectivity bench surrogate",
                    source,*CONTRACT,extra,".control","set wr_singlescale",
                    f"ac lin {N} {FSTART} {FSTOP}",
                    f"wrdata {mode}.dat vr(out) vi(out)",
                    "quit",".endc",".end",""))
                deck=folder/(mode+".cir")
                deck.write_text(circuit,encoding="utf-8")
                results.append(run_spice(deck,folder,mode))
            transfer,zout=results
            freq_peak,mag_peak,lower,upper,bw=bandwidth(transfer)
            peak_q=freq_peak/bw
            idx=round((455000-FSTART)*(N-1)/(FSTOP-FSTART))
            f455,m455=transfer[idx]
            zfreq,z455=zout[idx]
            assert abs(f455-455000)<1 and abs(zfreq-455000)<1
            assert bw>0 and peak_q>0 and mag_peak>0
            assert abs(z455)>0 and math.isfinite(abs(z455))
            r={"case":case,"load_model":extra or "100k output reference only",
               "peak_frequency_Hz":round(freq_peak,1),
               "peak_transfer_Vout_per_Vsource":round(mag_peak,9),
               "minus3dB_lower_Hz":round(lower,1),
               "minus3dB_upper_Hz":round(upper,1),
               "minus3dB_bandwidth_Hz":round(bw,1),
               "loaded_Q_from_peak_over_BW":round(peak_q,3),
               "transfer_at_455k_Vout_per_Vsource":round(abs(m455),9),
               "output_Z_at_455k_real_ohms":round(z455.real,3),
               "output_Z_at_455k_imag_ohms":round(z455.imag,3),
               "output_Z_at_455k_abs_ohms":round(abs(z455),3)}
            table.append(r)
            print("IF455_NATIVE_PASSIVE_AC_PORT_AND_SELECTIVITY",r,flush=True)
        assert len(table)==len(CASES)
        original=table[0]
        byname={r["case"]:r for r in table}
        # A physical shunt must reduce the port impedance magnitude.
        assert byname["shunt_1k"]["output_Z_at_455k_abs_ohms"] < (
            byname["shunt_10k"]["output_Z_at_455k_abs_ohms"])
        assert byname["shunt_10k"]["output_Z_at_455k_abs_ohms"] < (
            original["output_Z_at_455k_abs_ohms"])
        assert byname["shunt_1k"]["transfer_at_455k_Vout_per_Vsource"] < (
            byname["shunt_10k"]["transfer_at_455k_Vout_per_Vsource"])
        assert byname["shunt_10k"]["transfer_at_455k_Vout_per_Vsource"] < (
            original["transfer_at_455k_Vout_per_Vsource"])
        # Linear network: output impedance excludes nonlinear diode operating point.
        assert original["output_Z_at_455k_abs_ohms"]>0
    print("PASS_NGSPICE_IF455_PASSIVE_4_LOADS_AC_COMPLEX_Z_BANDWIDTH_NOT_RECEIVER_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":main()
