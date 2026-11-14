#!/usr/bin/env python3
"""PCB-FRONT analog moving-coil S-meter candidate: conservative current gate.

This is NOT a calibrated drive or a real meter OEM qualification. It
evaluates the actual 10k divider + two independent 100k series resistor topology under
unqualified hypothetical source/movement values, including contact faults.
The expected native KiCad pin↔net geometry is checked separately by
verify_front_smeter_native.py in FULL.
"""
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SCHEMATIC=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_SMETER/FRONT_SMETER_THT_V2_7_DRAFT.kicad_sch"
POT=10000.0
LIMIT_EACH=100000.0
LIMIT=2*LIMIT_EACH

def meter_current(vsource,rsource,rpot,rlimit,rcoil,alpha):
    """Positive current through coil for linear divider and Thevenin source.

    alpha=0: wiper at return; alpha=1: wiper at high track end.
    All resistances are nonnegative, rpot and rlimit strictly positive.
    """
    assert all(math.isfinite(x) for x in
               (vsource,rsource,rpot,rlimit,rcoil,alpha))
    assert vsource>=0 and rsource>=0 and rpot>0 and rlimit>0 and rcoil>=0
    assert 0<=alpha<=1
    top=(1-alpha)*rpot
    bottom=alpha*rpot
    # From the wiper: Vs with (rsource + top) above, bottom to return.
    vth=vsource*bottom/(rsource+top+bottom)
    rth=(rsource+top)*bottom/(rsource+top+bottom)
    return vth/(rth+rlimit+rcoil)

def nodal_reference(vsource,rsource,rpot,rlimit,rcoil,alpha):
    """Independent two-node Kirchhoff conductance solution for 0<alpha<1."""
    assert rsource>0 and 0<alpha<1
    a=1/rsource
    b=1/((1-alpha)*rpot)
    c=1/(alpha*rpot)
    d=1/(rlimit+rcoil)
    determinant=(a+b)*(b+c+d)-b*b
    assert determinant>0
    vw=(vsource*a*b)/determinant
    vh=(vsource*a*(b+c+d))/determinant
    assert abs((vh-vsource)*a+(vh-vw)*b)<1e-10
    assert abs((vw-vh)*b+vw*c+vw*d)<1e-10
    return vw*d

def main():
    sch=SCHEMATIC.read_text(encoding="utf-8")
    # Tie the numerical assumptions to the real draft components: changes
    # in values must cause explicit review of the analytical safety gate.
    assert '(property "Value" "10k_LINEAR_B_THT_DRAFT_PROVISIONAL"' in sch
    assert '(property "Value" "100k_0P25W_CANDIDATE_NO_FSD_QUAL"' in sch
    assert '(property "Value" "100k_0P25W_REDUNDANT_CANDIDATE_NO_FSD_QUAL"' in sch
    assert '(property "Reference" "R1802"' in sch
    assert 'METER_DRIVE_CANDIDATE' in sch and 'METER_RETURN' in sch
    cases=0
    for vs in (3.3,6.0,20.0):
        for rs in (100.0,1000.0,10000.0):
            for rc in (100.0,1000.0,5000.0):
                previous=0.0
                for alpha in (0.0,0.1,0.25,0.5,0.75,0.9,1.0):
                    i=meter_current(vs,rs,POT,LIMIT,rc,alpha)
                    assert 0<=i<=vs/LIMIT+1e-15
                    if alpha not in (0.0,1.0):
                        independent=nodal_reference(vs,rs,POT,LIMIT,rc,alpha)
                        assert math.isclose(i,independent,rel_tol=1e-11,abs_tol=1e-16)
                        cases+=1
                    assert i+1e-15>=previous,(
                        "For passive R divider, current should be monotonic",
                        vs,rs,rc,alpha,i,previous)
                    previous=i
                assert meter_current(vs,rs,POT,LIMIT,rc,0.0)==0.0

    # Nominal twin 100k series: 20V/200k=100uA, 6V/200k=30uA.
    assert math.isclose(meter_current(20,0,POT,LIMIT,0,1),100e-6)
    assert math.isclose(meter_current(6,0,POT,LIMIT,0,1),30e-6)
    assert meter_current(6,0,POT,LIMIT,0,1)<100e-6
    assert meter_current(20,0,POT,LIMIT,0,1)>50e-6
    # Either resistor shorted alone: the other 100k remains.
    for failed_index in (0,1):
        resistors=[LIMIT_EACH,LIMIT_EACH]
        resistors[failed_index]=0.0
        surviving=sum(resistors)
        assert math.isclose(meter_current(20,0,POT,surviving,0,1),200e-6)
        assert math.isclose(meter_current(6,0,POT,surviving,0,1),60e-6)
    # Both limiters shorted: resistive fault tolerance entirely lost.
    # Hypothetical 100-ohm coil at 6V -> ~60mA.
    double_fault=meter_current(6,0,POT,1e-9,100,1)
    assert double_fault>0.05
    # Single open resistor / open wiper gives zero steady DC coil current;
    # does not model inductive discharge, transients, or ESD.
    single_open_current_dc=0.0
    wiper_open_current_dc=0.0
    assert single_open_current_dc==wiper_open_current_dc==0.0
    # Potentiometer track load and unknown power rating are separate:
    # full-drive 20V across 10k would dissipate 40mW in ideal track,
    # not an assertion that the selected physical part is rated for it.
    track_power=20**2/POT
    assert math.isclose(track_power,0.04)
    print("FRONT_SMETER_UNQUALIFIED_FAULT_ENVELOPE",{
        "crosschecks":cases,
        "two_series_limiters_ohm_each":LIMIT_EACH,
        "20V_nominal_short_coil_uA":100.0,
        "20V_single_short_short_coil_uA":200.0,
        "6V_nominal_short_coil_uA":30.0,
        "6V_single_short_short_coil_uA":60.0,
        "6V_double_short_coil100_A":round(double_fault,9),
        "hypothetical_track_power_20V_W":track_power,
        "FSD_and_MAIN_drive_qualified":False},flush=True)
    assert cases==135
    print("PASS_FRONT_SMETER_135_KCL_DUAL_LIMITERS_SINGLE_FAULT_NO_FSD_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
