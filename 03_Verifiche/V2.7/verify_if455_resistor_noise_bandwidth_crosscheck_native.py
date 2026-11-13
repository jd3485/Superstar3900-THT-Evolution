#!/usr/bin/env python3
"""6 independent native ngspice IF455 R-damp/R-load bandwidth checks matching
the prior 30 real RF resistor Johnson-noise/signal transfer experiments.
No full receiver mask, AM/FM/SSB or OEM part approval.
"""
from pathlib import Path
import math
import tempfile
from verify_if455_passive_port_impedance_selectivity_native import (
    FSTART,FSTOP,N,run_spice,bandwidth,
)

ROOT=Path(__file__).resolve().parents[2]
PRIOR=ROOT/"03_Verifiche/V2.7/verify_if455_passive_resistor_noise_load_tradeoff_native.py"
RDAMP=(47000,100000,220000)
RLOAD=(100000,220000)
# Values directly checked by native PR114, not free targets chosen by this test.
PR114_H455={(47000,100000):0.835055562,
             (47000,220000):1.016659064,
             (100000,100000):1.280373951,
             (100000,220000):1.711591500,
             (220000,100000):1.723341159,
             (220000,220000):2.556852878}

def deck(damping,output):
    return f"""* IF455 passive-only 6-case native selectivity bandwidth comparison.
* RCOIL 16.5 Ohms assumes DCR = RF loss (not qualified by OEM).
.title IF455 IF-stage passive noise tradeoff and AC -3dB BW no fab
VSIGNAL src 0 DC 0 AC 1
RGEN src gen 50
C1601 gen tank 10p
L1601 tank ltail 1m
RCOIL ltail 0 16.5
C1602 tank 0 82p
C1603 tank 0 30p
R1601 tank 0 {damping}
C1604 tank out 10p
R1602 out 0 {output}
.control
set wr_singlescale
ac lin {N} {FSTART} {FSTOP}
wrdata transfer.dat vr(out) vi(out)
quit
.endc
.end
"""

def main():
    script=PRIOR.read_text(encoding="utf-8")
    for anchor in ('RDAMP_VALUES=(47000,100000,220000)',
                   'RLOAD_VALUES=(100000,220000)',
                   'PR113_REF_H455=0.835055562'):
        assert anchor in script,("PR114 screening changed",anchor)
    results=[]
    with tempfile.TemporaryDirectory(prefix="tht_if455_resistor_bw_") as td:
        for rdamp in RDAMP:
            for rload in RLOAD:
                case=f"rd{rdamp}_rl{rload}"
                folder=Path(td)/case
                folder.mkdir()
                cir=folder/"bandwidth.cir"
                cir.write_text(deck(rdamp,rload),encoding="utf-8")
                rows=run_spice(cir,folder,"transfer")
                peak,peak_gain,lower,upper,bw=bandwidth(rows)
                idx=round((455000-FSTART)*(N-1)/(FSTOP-FSTART))
                assert abs(rows[idx][0]-455000)<1
                transfer=abs(rows[idx][1])
                assert abs(transfer-PR114_H455[(rdamp,rload)])/(
                    PR114_H455[(rdamp,rload)])<0.01,(
                        "PR114 AC transfer drift",rdamp,rload,transfer)
                assert 0<bw<100000 and lower<peak<upper and peak_gain>=transfer
                record={"damping_ohm":rdamp,"output_resistance_ohm":rload,
                    "transfer_at_455_V_per_V_source":round(transfer,9),
                    "peak_freq_Hz":round(peak,1),
                    "lower_minus3dB_Hz":round(lower,1),
                    "upper_minus3dB_Hz":round(upper,1),
                    "AC_minus3dB_BW_Hz":round(bw,1),
                    "transfer_peak_over_BW_indicator":round(peak/bw,4),
                    "ratio_transfer_455_to_peak":round(transfer/peak_gain,6)}
                print("IF455_NATIVE_6_R_DAMP_RLOAD_SELECTIVITY_TRADEOFF",record,flush=True)
                results.append(record)
    assert len(results)==6
    original=next(x for x in results if x["damping_ohm"]==47000
                  and x["output_resistance_ohm"]==100000)
    assert abs(original["peak_freq_Hz"]-454750)<250
    assert abs(original["AC_minus3dB_BW_Hz"]-42556.7)/42556.7<0.015
    print("IF455_NATIVE_6_R_DAMP_RLOAD_BW_REFERENCE",{
        "PR110_original_BW_Hz":original["AC_minus3dB_BW_Hz"],
        "caveat":"single resonator AC transfer, not receiver IF selectivity mask"},flush=True)
    print("PASS_NGSPICE_IF455_6_NOISE_TRADEOFF_AC_BANDWIDTH_NATIVE_NOT_RECEIVER_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":main()
