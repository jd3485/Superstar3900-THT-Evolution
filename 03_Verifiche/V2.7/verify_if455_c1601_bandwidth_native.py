#!/usr/bin/env python3
"""Native ngspice 15-case IF455 C1601 source-impedance vs passband check.

All variations are temporary SPICE decks. Neither actual mixer IF source
impedance nor a qualified production filter is represented. NO FAB / NO TX.
"""
from pathlib import Path
import math
import tempfile
from verify_if455_two_port_source_impedance_native import (
    TANK, spicedeck, run_spice, bandwidth, FSTART, FSTOP, N
)
CAPS_PF=(10,47,100,470,1000)
RS_OHM=(50,1000,10000)
BASELINE_455={(50):0.835055562,(1000):0.815223437,(10000):0.652547922}
F_IF=455000.0

def main():
    schematic=TANK.read_text(encoding="utf-8")
    assert '(property "Reference" "C1601"' in schematic
    assert '(property "Value" "10pF_C0G_INPUT_COUPLING"' in schematic
    index=round((F_IF-FSTART)*(N-1)/(FSTOP-FSTART))
    results=[]
    with tempfile.TemporaryDirectory(prefix="tht_if455_cap_bandwidth_") as tmp:
        for cap in CAPS_PF:
            for rs in RS_OHM:
                folder=Path(tmp)/f"c{cap}_rs{rs}"
                folder.mkdir()
                circuit=spicedeck(rs,"","transfer")
                assert circuit.count("C1601 gen tank 10p")==1
                circuit=circuit.replace("C1601 gen tank 10p",f"C1601 gen tank {cap}p")
                deck=folder/"transfer.cir"
                deck.write_text(circuit,encoding="utf-8")
                ac=run_spice(deck,folder,"transfer")
                f455,m455=ac[index]
                assert abs(f455-F_IF)<1
                output_curve=[(f,complex(z.imag,0)) for f,z in ac]
                peak,mag,lower,upper,bw=bandwidth(output_curve)
                v455=m455.imag
                assert all(math.isfinite(v) for v in (peak,mag,lower,upper,bw,v455))
                assert lower<peak<upper and 0<bw<FSTOP-FSTART
                assert 0<v455<=mag*(1+1e-6),(cap,rs,v455,mag)
                if cap==10:
                    assert abs(v455-BASELINE_455[rs])<1e-6,("baseline drift",rs,v455)
                item=dict(C1601_pF=cap,hypothetical_Rs_ohm=rs,
                          peak_frequency_Hz=round(peak,1),
                          minus3dB_lower_Hz=round(lower,1),
                          minus3dB_upper_Hz=round(upper,1),
                          minus3dB_bandwidth_Hz=round(bw,1),
                          apparent_peak_over_BW=round(peak/bw,3),
                          transfer_455_Vout_over_Vsource=round(v455,9),
                          transfer_455_over_peak=round(v455/mag,6))
                results.append(item)
                print("IF455_C1601_NATIVE_BANDWIDTH",item,flush=True)
    assert len(results)==15
    for rs in RS_OHM:
        group=[x for x in results if x["hypothetical_Rs_ohm"]==rs]
        assert {x["C1601_pF"] for x in group}==set(CAPS_PF)
    print("PASS_NGSPICE_IF455_C1601_15_NATIVE_PASSBAND_CASES_NO_VENDOR_MIXER_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
