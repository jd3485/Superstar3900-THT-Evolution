#!/usr/bin/env python3
"""Independent 30-run native ngspice IF455 R-damp/R-output noise-load tradeoff.
6 parameter configurations x (signal + 4 resistor-noise AC transfer probes).
No OEM RF loss/Q, active IF amplifier noise, diode or antenna sensitivity claim.
"""
from pathlib import Path
import math
import tempfile

import verify_if455_passive_resistor_noise_budget_native as base

ROOT=Path(__file__).resolve().parents[2]
RDAMP_VALUES=(47000,100000,220000)
RLOAD_VALUES=(100000,220000)
ANCHOR_DAMP="R1601 tank damping_r 47k"
ANCHOR_LOAD="R1602 out load_r 100k"
PR113_REF_SOURCE_NOISE=2.775511e-08
PR113_REF_H455=0.835055562

def document(bias,rdamp,rload,excitation):
    deck=base.deck_text(bias,excitation)
    assert deck.count(ANCHOR_DAMP)==1 and deck.count(ANCHOR_LOAD)==1
    deck=deck.replace(ANCHOR_DAMP,f"R1601 tank damping_r {rdamp}")
    deck=deck.replace(ANCHOR_LOAD,f"R1602 out load_r {rload}")
    return deck

def main():
    sch=(ROOT/"04_KiCad/V2.7_DRAFT/IF455_TANK/IF455_TANK_THT_V2_7_DRAFT.kicad_sch").read_text(encoding="utf-8")
    assert "EW_GKG50015_10to50pF_THT_CANDIDATE_TRIM" in sch
    rows=[]
    with tempfile.TemporaryDirectory(prefix="tht_if455_thermal_R_tradeoffs_") as tmp:
        for rdamp in RDAMP_VALUES:
            for rload in RLOAD_VALUES:
                label=f"RDAMP_{rdamp}_RLOAD_{rload}"
                load={"extra":"","resistors":{"RGEN":50.0,"RCOIL":16.5,
                       "RDAMP":float(rdamp),"RLOAD":float(rload)}}
                folder=Path(tmp)/label
                sig=base.spectrum(document(load,rdamp,rload,"SIGNAL"),
                                  folder/"signal")
                h455=abs(sig[base.COUNT//2])
                assert h455>0
                contributions=[]
                densities=[0.0]*base.COUNT
                for part,ohms in load["resistors"].items():
                    gain=base.spectrum(document(load,rdamp,rload,part),
                                       folder/part)
                    if part=="RGEN":
                        assert abs(abs(gain[base.COUNT//2])-h455)/h455<0.001,(
                            "Independent source series transfer contract broken",
                            label,h455,gain[base.COUNT//2])
                    noisepsd=[4*base.K_B*base.TEMP_K*ohms*abs(h)**2
                              for h in gain]
                    densities=[a+b for a,b in zip(densities,noisepsd)]
                    contributions.append({"resistor":part,"ohms":ohms,
                        "RF_noise_455_nV_per_sqrtHz":
                            round(1e9*math.sqrt(noisepsd[base.COUNT//2]),5)})
                spectral=math.sqrt(densities[base.COUNT//2])
                integrated=math.sqrt(sum(
                    0.5*(densities[i]+densities[i+1])*base.FREQ_STEP
                    for i in range(base.COUNT-1)))
                source_ref=spectral/h455
                assert source_ref>0 and integrated>0 and math.isfinite(source_ref)
                if (rdamp,rload)==(47000,100000):
                    assert abs(source_ref-PR113_REF_SOURCE_NOISE)/PR113_REF_SOURCE_NOISE<0.01
                    assert abs(h455-PR113_REF_H455)/PR113_REF_H455<0.01
                row={"damping_R_ohms":rdamp,"output_R_ohms":rload,
                    "transfer_at_455_V_per_1V_generator":round(h455,9),
                    "output_noise_455_nV_per_sqrtHz":round(1e9*spectral,5),
                    "output_noise_451_459k_uVrms":round(1e6*integrated,6),
                    "generator_referred_noise_455_nV_per_sqrtHz":round(1e9*source_ref,5),
                    "contributions":contributions}
                rows.append(row)
                print("IF455_NATIVE_PASSIVE_RESISTOR_NOISE_LOAD_TRADEOFF",row,flush=True)
    assert len(rows)==len(RDAMP_VALUES)*len(RLOAD_VALUES)
    rank=sorted(rows,key=lambda x:x["generator_referred_noise_455_nV_per_sqrtHz"])
    print("IF455_PASSIVE_RF_NOISE_MINIMUM_INPUT_REFERRED_GENERIC",{
        "lowest_nominal_model":rank[0],
        "highest_nominal_model":rank[-1],
        "warning":"Selection cannot use single-frequency noise; check 3dB BW, AC loss, OEM PVT, AM IF architecture"},flush=True)
    print("PASS_NGSPICE_IF455_R_DAMP_R_LOAD_30_NATIVE_NOISE_AND_TRANSFER_PROBES_NOT_RECEIVER_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":main()
