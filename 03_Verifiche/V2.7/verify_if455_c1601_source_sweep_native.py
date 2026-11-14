#!/usr/bin/env python3
"""Native ngspice sensitivity of the *candidate* IF455 source coupling capacitor.

C1601=10p in actual KiCad tank; alternatives are sandbox-only substitutions
in the SPICE deck. Rs is hypothetical: NO SBL-1+ IF Zout/vendor characterization.
NO FAB / NO TX / NO BATTERY / NO VEHICLE.
"""
from pathlib import Path
import math
import tempfile
from verify_if455_two_port_source_impedance_native import (
    TANK, spicedeck, run_spice, FSTART, FSTOP, N
)

CAPS_PF=(10, 47, 100, 470, 1000)
RS_OHM=(50, 1000, 10000)
IF_HZ=455000
BASELINE_50=0.835055562

def main():
    sch=TANK.read_text(encoding="utf-8")
    assert '(property "Reference" "C1601"' in sch
    assert '(property "Value" "10pF_C0G_INPUT_COUPLING"' in sch
    idx=round((IF_HZ-FSTART)*(N-1)/(FSTOP-FSTART))
    assert abs(FSTART+idx*(FSTOP-FSTART)/(N-1)-IF_HZ)<1
    results=[]
    with tempfile.TemporaryDirectory(prefix="tht_if455_c1601_sweep_") as temp:
        for cap in CAPS_PF:
            for rs in RS_OHM:
                folder=Path(temp)/f"c{cap}_rs{rs}"
                folder.mkdir()
                # Same native ngspice tank as previously regression-tested.
                # Only the *bench deck*, never KiCad, gets a trial C value.
                deck_text=spicedeck(rs,"","transfer")
                marker="C1601 gen tank 10p"
                assert deck_text.count(marker)==1
                deck_text=deck_text.replace(marker,f"C1601 gen tank {cap}p")
                deck=folder/"transfer.cir"
                deck.write_text(deck_text,encoding="utf-8")
                data=run_spice(deck,folder,"transfer")
                assert abs(data[idx][0]-IF_HZ)<1
                vin=data[idx][1].real
                vout=data[idx][1].imag
                assert all(math.isfinite(x) for x in (vin,vout))
                assert vin>0 and vout>0,(cap,rs,vin,vout)
                xc=1/(2*math.pi*IF_HZ*cap*1e-12)
                row=dict(cap_pF=cap,hypothetical_Rs_ohm=rs,
                         C_reactance_ohm=round(xc,3),
                         Vout_over_Vsource_at_455=round(vout,9),
                         Vout_over_post_Rs_input_at_455=round(vout/vin,9))
                print("IF455_C1601_NATIVE_PARAMETRIC",row,flush=True)
                results.append((cap,rs,vout))
    assert len(results)==len(CAPS_PF)*len(RS_OHM)
    baseline=next(v for c,r,v in results if c==10 and r==50)
    assert abs(baseline-BASELINE_50)/BASELINE_50<0.01,(baseline,BASELINE_50)
    assert 34900<1/(2*math.pi*IF_HZ*10e-12)<35100
    # Avoid assuming larger coupling automatically optimizes bandwidth,
    # mixer loading, LO isolation or noise: these require real measurements.
    print("PASS_NGSPICE_IF455_C1601_15_CANDIDATE_SOURCE_CASES_NO_MIXER_MODEL_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
