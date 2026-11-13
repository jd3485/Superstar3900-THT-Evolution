#!/usr/bin/env python3
"""Native IF455 source-port loading contract: upstream Rs 50/1k/10k, downstream
100k baseline or passive JFET-gate RC surrogate, plus complex Zin probes.

No mixer or upstream amplifier model is asserted; Rs are hypothetical
Thevenin resistances. Signal port is KiCad J1601 pin1 IF455_SOURCE relative
to J1601 pin2 IF_BENCH_GND. J1602 output remains a separate two-pin port.
"""
from pathlib import Path
import math
import tempfile
from verify_if455_passive_port_impedance_selectivity_native import (
    run_spice,bandwidth,FSTART,FSTOP,N
)

ROOT=Path(__file__).resolve().parents[2]
TANK=ROOT/"04_KiCad/V2.7_DRAFT/IF455_TANK/IF455_TANK_THT_V2_7_DRAFT.kicad_sch"
PREV=ROOT/"03_Verifiche/V2.7/verify_if455_passive_port_impedance_selectivity_native.py"
RS=(50,1000,10000)
LOADS=(
    ("R100k_BENCH_REFERENCE",""),
    ("GATE_RC_SURROGATE","C_GATE out gate 10p\nR_GATE gate 0 1Meg\nC_PAR gate 0 7p"),
)
H455_AT_50={"R100k_BENCH_REFERENCE":0.835055562,
            "GATE_RC_SURROGATE":0.665186786}
ZPORT="input"
def spicedeck(rs,load,mode):
    if mode=="transfer":
        drive=f"VSIGNAL src 0 DC 0 AC 1\nRGEN src gen {rs}"
        output="vm(gen) vm(out)"
    elif mode=="port_z":
        # Generator disconnected. Pure filter input port impedance, not
        # source impedance with the upstream Thevenin resistance in circuit.
        drive="IPROBE 0 gen DC 0 AC 1"
        output="vr(gen) vi(gen)"
    else:
        raise ValueError(mode)
    return "\n".join([
        "* Passive IF455 SOURCE boundary stress test only, no real mixer.",
        "* Nominal Rcoil RF 16.5 Ohms is an unqualified DCR proxy.",
        ".title IF455 source impedance and downstream detector port cross loading",
        drive,
        "C1601 gen tank 10p",
        "L1601 tank ltail 1m",
        "RLOSS ltail 0 16.5",
        "C1602 tank 0 82p",
        "C1603 tank 0 30p",
        "R1601 tank 0 47k",
        "C1604 tank out 10p",
        "R1602 out 0 100k",
        load,
        ".control","set wr_singlescale",
        f"ac lin {N} {FSTART} {FSTOP}",
        f"wrdata {mode}.dat {output}",
        "quit",".endc",".end","",
    ])

def main():
    sch=TANK.read_text(encoding="utf-8")
    legacy=PREV.read_text(encoding="utf-8")
    for key in ('label "IF455_SOURCE"','label "IF_BENCH_GND"',
                'label "IF455_FILTER_OUT"',
                'property "Reference" "J1601"','property "Reference" "J1602"'):
        assert key in sch,("KiCad IF455 two-port contract moved",key)
    assert 'H455' in legacy and "RGEN src gen 50" in legacy
    results=[]
    with tempfile.TemporaryDirectory(prefix="tht_if455_source_port_") as t:
        for loadname,load in LOADS:
            for rs in RS:
                folder=Path(t)/(loadname+"_"+str(rs))
                folder.mkdir()
                deck=folder/"transfer.cir"
                deck.write_text(spicedeck(rs,load,"transfer"),encoding="utf-8")
                # Native vm(gen), vm(out) only (not complex voltage data).
                # Existing native reader expects 3 floats and returns complex
                # vm(gen)+j*vm(out), allowing us to extract both columns.
                data=run_spice(deck,folder,"transfer")
                idx=round((455000-FSTART)*(N-1)/(FSTOP-FSTART))
                assert abs(data[idx][0]-455000)<1
                drive_at_455=data[idx][1].real
                out_at_455=data[idx][1].imag
                assert drive_at_455>0 and out_at_455>0
                output_curve=[(freq,complex(value.imag,0)) for freq,value in data]
                peak,amp,left,right,bw=bandwidth(output_curve)
                assert left<peak<right and bw>0
                if rs==50:
                    exp=H455_AT_50[loadname]
                    assert abs(out_at_455-exp)/exp<0.01,(
                        "PR110 baseline drift with Rs50",loadname,out_at_455,exp)
                row={"load_case":loadname,"hypothetical_source_R_ohms":rs,
                     "IF_source_port_signal_at_455_per_Vsource":round(drive_at_455,9),
                     "IF_detector_port_signal_at_455_per_Vsource":round(out_at_455,9),
                     "IF_output_over_post_Rs_input_at_455":round(out_at_455/drive_at_455,9),
                     "peak_frequency_Hz":round(peak,1),
                     "minus3dB_band_Hz":round(bw,1)}
                results.append(row)
                print("IF455_NATIVE_TWO_PORT_RS_TO_LOAD",row,flush=True)
            # Intrinsic port Zin of passive tank with downstream load.
            folder=Path(t)/(loadname+"_zin")
            folder.mkdir()
            deck=folder/"port_z.cir"
            deck.write_text(spicedeck(None,load,"port_z"),encoding="utf-8")
            zin=run_spice(deck,folder,"port_z")
            idx=round((455000-FSTART)*(N-1)/(FSTOP-FSTART))
            assert abs(zin[idx][0]-455000)<1
            z=zin[idx][1] # 1 A test injection into J1601 input port
            assert z.real>0 and math.isfinite(abs(z)) and abs(z)>0
            print("IF455_NATIVE_INTRINSIC_SOURCE_PORT_Z_AT_455",{
                "load_case":loadname,"Zin_ohm_real":round(z.real,6),
                "Zin_ohm_imag":round(z.imag,6),
                "Zin_ohm_abs":round(abs(z),6),
                "source_resistance_excluded":True},flush=True)
    assert len(results)==6
    by={(r["load_case"],r["hypothetical_source_R_ohms"]):r for r in results}
    for name,_ in LOADS:
        assert by[name,10000]["IF_detector_port_signal_at_455_per_Vsource"]<(
            by[name,1000]["IF_detector_port_signal_at_455_per_Vsource"])
        assert by[name,1000]["IF_detector_port_signal_at_455_per_Vsource"]<(
            by[name,50]["IF_detector_port_signal_at_455_per_Vsource"])
    print("PASS_NGSPICE_IF455_6_SOURCE_PORT_AC_PLUS_2_COMPLEX_ZIN_NO_MIXER_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":main()
