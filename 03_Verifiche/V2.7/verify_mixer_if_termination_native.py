#!/usr/bin/env python3
"""Native KiCad9 port contract + ngspice mixer IF termination sensitivity.

Does NOT model actual SBL-1+ nonlinear IF output impedance or qualify 50 ohms
over its output harmonic spectrum. No PCB, no TX, no fabrication.
"""
from pathlib import Path
import math
import tempfile
from verify_interboard_audio_contract_native import exported_nets, require
from verify_if455_two_port_source_impedance_native import (
    TANK, spicedeck, run_spice, FSTART, FSTOP, N
)

ROOT=Path(__file__).resolve().parents[2]
MIXER=ROOT/"04_KiCad/V2.7_DRAFT/MIXER_SBL1_CANDIDATE/MIXER_SBL1_BENCH_THT_V2_7_DRAFT.kicad_sch"
SOURCE_R=(50,1000,10000)
TERMINATIONS=(None,50,100)
REFERENCE_50_NO_TERM=0.835055562
F_IF=455000

def main():
    with tempfile.TemporaryDirectory(prefix="tht_mixer_if_termination_") as temp:
        folder=Path(temp)
        mixer=exported_nets(MIXER,folder/"mixer.net")
        tank=exported_nets(TANK,folder/"tank.net")
        require(mixer,"IF455_MIXER_IF",("MX1701","3"),("MX1701","4"),("J1703","1"))
        require(mixer,"IF_BENCH_GND",("MX1701","2"),("MX1701","5"),
                ("MX1701","6"),("MX1701","7"),("J1703","2"))
        require(tank,"IF455_SOURCE",("J1601","1"),("C1601","1"))
        require(tank,"IF_BENCH_GND",("J1601","2"),("J1602","2"))
        # The existing native standalone mixer has *no* termination element.
        # Preserve that fact until an intentional KiCad revision is qualified.
        assert mixer["IF455_MIXER_IF"]=={
            ("MX1701","3"),("MX1701","4"),("J1703","1")}
        assert not any(ref.startswith("R") for ref,pin in mixer["IF455_MIXER_IF"])
        assert tank["IF455_SOURCE"]=={("J1601","1"),("C1601","1")}
        idx=round((F_IF-FSTART)*(N-1)/(FSTOP-FSTART))
        assert abs(FSTART+idx*(FSTOP-FSTART)/(N-1)-F_IF)<1
        cases={}
        for rs in SOURCE_R:
            for termination in TERMINATIONS:
                name="none" if termination is None else str(termination)
                dest=folder/f"rs{rs}_rt{name}"
                dest.mkdir()
                deck=spicedeck(rs,"","transfer")
                assert deck.count("C1601 gen tank 10p")==1
                if termination is not None:
                    # Resistor at SOURCE PORT after the assumed source Rs,
                    # in parallel with the existing IF455 filter input.
                    # Only a temporary SPICE deck: no actual mixer model.
                    deck=deck.replace("C1601 gen tank 10p",
                                      f"R_IF_TERM gen 0 {termination}\nC1601 gen tank 10p")
                fn=dest/"transfer.cir"
                fn.write_text(deck,encoding="utf-8")
                data=run_spice(fn,dest,"transfer")
                assert abs(data[idx][0]-F_IF)<1
                port=data[idx][1].real
                output=data[idx][1].imag
                assert math.isfinite(port) and math.isfinite(output)
                assert port>0 and output>0
                record=dict(source_R_ohm_hypothetical=rs,
                            shunt_IF_port_R_ohm=termination,
                            V_IF_port_over_V_source_at_455=round(port,9),
                            V_filter_out_over_V_source_at_455=round(output,9))
                cases[rs,termination]=record
                print("IF455_MIXER_TERMINATION_NATIVE_SPICE",record,flush=True)
        assert len(cases)==9
        for rs in SOURCE_R:
            unterm=cases[rs,None]["V_filter_out_over_V_source_at_455"]
            term100=cases[rs,100]["V_filter_out_over_V_source_at_455"]
            term50=cases[rs,50]["V_filter_out_over_V_source_at_455"]
            assert unterm>term100>term50>0,(rs,unterm,term100,term50)
            assert cases[rs,None]["V_IF_port_over_V_source_at_455"]>(
                cases[rs,50]["V_IF_port_over_V_source_at_455"])
        assert abs(cases[50,None]["V_filter_out_over_V_source_at_455"]-
                   REFERENCE_50_NO_TERM)<1e-6
        print("MIXER_IF_NOMINAL_HAS_NO_NATIVE_50OHM_SHUNT_OR_DIPLEXER",flush=True)
        print("MIXER_IF_50OHM_BENCH_TERMINATION_NOT_VENDOR_SOURCE_Z_MODEL",flush=True)
        print("PASS_NATIVE_KICAD9_MIXER_IF_PORT_AND_9_NGSPICE_TERMINATION_CASES_NO_OEM_LOAD_QUALIFICATION_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
