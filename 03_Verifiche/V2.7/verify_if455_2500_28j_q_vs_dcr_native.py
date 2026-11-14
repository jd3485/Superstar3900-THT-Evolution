#!/usr/bin/env python3
"""Guard against treating Delevan 2500-28J max DC resistance as AC series loss.

Q=60 at 790kHz gives an *illustrative* 82.73-ohm effective series
resistance at THAT frequency if L=1mH, not an OEM value at 455kHz.
Every sweep alters only a temporary ngspice deck, not physical KiCad.
"""
from pathlib import Path
import math
import tempfile
from verify_interboard_audio_contract_native import exported_nets, require
from verify_if455_two_port_source_impedance_native import (
    TANK, spicedeck, run_spice, bandwidth, FSTART, FSTOP, N
)

F_Q=790000.0
F_IF=455000.0
L_H=0.001
Q_790=60.0
DCR_MAX=16.5
R_EQ_AT_790=2*math.pi*F_Q*L_H/Q_790
# NOT a 455kHz manufacturer's model: controlled sensitivity hypotheses.
LOSS_CASES=(("DCR_MAX_AS_RF_LOSS_PROXY",DCR_MAX),
            ("HALF_R_EQ_790_AS_455_TRIAL",R_EQ_AT_790/2),
            ("R_EQ_790_AS_455_TRIAL",R_EQ_AT_790),
            ("TWICE_R_EQ_790_AS_455_TRIAL",2*R_EQ_AT_790))
LOADS=(("100K_BASELINE",""),("GATE_RC_PASSIVE",
        "C_GATE out gate 10p\nR_GATE gate 0 1Meg\nC_PAR gate 0 7p"))

def main():
    sch=TANK.read_text(encoding="utf-8")
    assert '(property "Reference" "L1601"' in sch
    assert '(property "Value" "1mH_DELEVAN_2500-28J_CANDIDATE_NOT_QUALIFIED"' in sch
    assert 82<R_EQ_AT_790<84
    idx=round((F_IF-FSTART)*(N-1)/(FSTOP-FSTART))
    all_rows=[]
    with tempfile.TemporaryDirectory(prefix="tht_if455_q_dcr_") as t:
        root=Path(t)
        nets=exported_nets(TANK,root/"if455.net")
        require(nets,"IF455_SOURCE",("J1601","1"),("C1601","1"))
        require(nets,"IF455_TANK",("C1601","2"),("L1601","1"))
        require(nets,"IF_BENCH_GND",("L1601","2"),("J1601","2"))
        for label,load in LOADS:
            for case,r_loss in LOSS_CASES:
                folder=root/f"{label}_{case}"
                folder.mkdir()
                deck=spicedeck(50,load,"transfer")
                old="RLOSS ltail 0 16.5"
                assert deck.count(old)==1
                deck=deck.replace(old,f"RLOSS ltail 0 {r_loss:.12g}")
                file=folder/"transfer.cir"
                file.write_text(deck,encoding="utf-8")
                data=run_spice(file,folder,"transfer")
                assert abs(data[idx][0]-F_IF)<1
                output=[(freq,complex(z.imag,0)) for freq,z in data]
                peak,amplitude,left,right,bw=bandwidth(output)
                v455=data[idx][1].imag
                assert all(math.isfinite(v) for v in (peak,amplitude,left,right,bw,v455))
                assert left<peak<right and 0<v455 and 0<bw<FSTOP-FSTART
                item={"passive_load_case":label,"loss_hypothesis":case,
                      "AC_series_R_trial_ohm":round(r_loss,6),
                      "peak_Hz":round(peak,1),"minus3dB_BW_Hz":round(bw,1),
                      "Vout_per_Vsource_at_455":round(v455,9)}
                print("IF455_2500_28J_Q_VS_DCR_NATIVE_AC",item,flush=True)
                all_rows.append(item)
    assert len(all_rows)==len(LOSS_CASES)*len(LOADS)==8
    base=next(row for row in all_rows if row["passive_load_case"]=="100K_BASELINE"
              and row["loss_hypothesis"]=="DCR_MAX_AS_RF_LOSS_PROXY")
    assert abs(base["Vout_per_Vsource_at_455"]-0.835055562)<1e-6
    assert abs(base["minus3dB_BW_Hz"]-42556.7)<2
    print("DELEVAN_2500_28J_Q60_AT_790K_IMPLIES_IDEAL_SERIES_R_OHM",
          round(R_EQ_AT_790,6),"NOT_455KHZ_OEM_RF_R",flush=True)
    print("PASS_NATIVE_KICAD9_NGSPICE_IF455_8_AC_LOSS_TRIALS_NO_Q455_INFERENCE_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
