#!/usr/bin/env python3
"""S-meter passive network source compliance / FSD envelope, schematic-anchored.

The two series 100k resistors and 10k potentiometer are FRONT candidates.
No OEM meter full-scale current, coil resistance or MAIN driver is known.
"""
from itertools import product
from math import isclose, isfinite
from pathlib import Path
import tempfile
from verify_interboard_audio_contract_native import exported_nets, require

ROOT=Path(__file__).resolve().parents[2]
SCHEMATIC=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_SMETER/FRONT_SMETER_THT_V2_7_DRAFT.kicad_sch"
R_NOM=100_000.
R_TOL=.05
POT=10_000.
COIL_OHM=(0.,1000.,20000.)
SOURCE_V=(5.,9.,12.,15.,20.)
FSD_A=(25e-6,50e-6,100e-6)
SHORTS=(0,1,2)
WIPER=(0.,.1,.5,.9,1.)

def coil_current(v,coil,resistors_shorted,wiper_fraction,series_resistor_scale=1.):
    """Ideal divider pot with loaded wiper. 0=low side, 1=high side."""
    if not all(isfinite(vv) for vv in (v,coil,wiper_fraction,series_resistor_scale)):
        raise ValueError("nonfinite")
    if coil<0 or resistors_shorted not in SHORTS or not 0<=wiper_fraction<=1 or series_resistor_scale<=0:
        raise ValueError("invalid")
    rh=POT*(1-wiper_fraction)
    rl=POT*wiper_fraction
    rload=(2-resistors_shorted)*R_NOM*series_resistor_scale+coil
    # Exact endpoints; zero-ohm load short is not a valid current-limited
    # circuit and must report unbounded current rather than fake 0A.
    if rload==0:
        return float("inf") if v and wiper_fraction else 0.
    if rh==0:
        return abs(v)/rload
    if rl==0:
        return 0.
    rparallel=rl*rload/(rl+rload)
    vw=abs(v)*rparallel/(rh+rparallel)
    return vw/rload

def source_required(fsd,coil,resistors_shorted,scale=1.,wiper_fraction=1.):
    """Best-case source requirement at a selected pot setting."""
    if not isfinite(fsd) or fsd<=0:raise ValueError("invalid FSD")
    per_volt=coil_current(1.,coil,resistors_shorted,wiper_fraction,scale)
    if per_volt==0:return float("inf")
    return fsd/per_volt

def native():
    with tempfile.TemporaryDirectory(prefix="tht_meter_compliance_") as td:
        nets=exported_nets(SCHEMATIC,Path(td)/"smeter.net")
    expected={
      "METER_DRIVE_CANDIDATE":{("J1801","1"),("RV1801","1")},
      "METER_RETURN":{("J1801","2"),("RV1801","3"),("J1802","2")},
      "METER_TRIM_OUTPUT":{("RV1801","2"),("R1801","1")},
      "METER_LIMIT_STAGE1":{("R1801","2"),("R1802","1")},
      "METER_POS_LIMITED":{("R1802","2"),("J1802","1")}
    }
    assert set(nets)==set(expected)
    for name,pins in expected.items():
        require(nets,name,*pins)
        assert nets[name]==pins,(name,nets[name],pins)
    data=SCHEMATIC.read_text(encoding="utf-8")
    for val in ("10k_LINEAR_B_THT_DRAFT_PROVISIONAL",
                "100k_0P25W_CANDIDATE_NO_FSD_QUAL",
                "100k_0P25W_REDUNDANT_CANDIDATE_NO_FSD_QUAL"):
        assert data.count(val)==1,val

def main():
    native()
    count=0
    unbounded=0
    for v,coil,shorts,wiper in product(SOURCE_V,COIL_OHM,SHORTS,WIPER):
        curr=coil_current(v,coil,shorts,wiper)
        assert curr>=0 and (isfinite(curr) or curr==float("inf"))
        assert curr<=coil_current(v,coil,shorts,1.)+1e-16
        if shorts==2 and coil==0 and wiper>0:
            assert curr==float("inf")
        for fsd in FSD_A:
            required=source_required(fsd,coil,shorts,wiper)
            assert ((curr>=fsd) == (v+1e-10>=required)),(v,coil,shorts,wiper,fsd,curr,required)
            count+=1
            if curr==float("inf"):unbounded+=1
    assert count==675 and unbounded==60
    assert isclose(coil_current(5.,20000.,0,1.),5/220000)
    assert isclose(coil_current(5.,0.,0,1.),25e-6)
    assert isclose(coil_current(5.,20000.,1,1.),5/120000)
    assert isclose(coil_current(5.,20000.,2,1.),250e-6)
    assert isclose(source_required(50e-6,20000.,0),11.)
    assert isclose(source_required(50e-6,20000.,0,.95),10.5)
    assert isclose(source_required(50e-6,20000.,1,.95),5.75)
    assert isclose(source_required(50e-6,20000.,2),1.)
    assert source_required(50e-6,20000.,0,wiper_fraction=0.)==float("inf")
    assert coil_current(5.,20000.,0,.9)<coil_current(5.,20000.,0,1.)
    # FSD at 5 V with both resistors intact is impossible for hypothetical
    # 50uA + 20kohm coil even at -5% resistor tolerance.
    assert coil_current(5.,20000.,0,1.,.95)<50e-6
    # Do not silently report finite current with two dead series
    # limiters and hypothetical zero coil ohms.
    assert coil_current(5.,0.,2,1.)==float("inf")
    for v in (float("nan"),float("inf")):
        try:coil_current(v,20000.,0,1.)
        except ValueError:pass
        else:raise AssertionError("nonfinite source accepted")
    print("SMETER_PASSIVE_5V_FSD_COMPLIANCE_SCREEN",{
       "cases_checked":count,"unbounded_zero_ohm_two_short_cases":unbounded,
       "SOURCE_V_scenarios":SOURCE_V,
       "R1801_R1802_nominal_each_ohm":R_NOM,
       "R_tolerance_hypothetical":R_TOL,
       "Rcoil_hypothetical_ohm":COIL_OHM,
       "FSD_hypothetical_microampere":tuple(1e6*x for x in FSD_A),
       "5V_20kcoil_two_good_amps":coil_current(5.,20000.,0,1.),
       "50uA_20kcoil_nominal_two_good_min_source_V":11.,
       "50uA_20kcoil_low_tolerance_two_good_min_source_V":10.5,
       "5V_active_sink_connected_to_2x100k":False,
       "actual_MAIN_driver_exists":False,
       "actual_meter_coil_FSD_qualified":False,
       "hardware_bench_qualified":False,"NO_FAB_NO_TX":True},flush=True)
    print("PASS_NATIVE_KICAD9_SMETER_675_PASSIVE_FSD_SOURCE_COMPLIANCE_CASES_NONFAB",flush=True)

if __name__=="__main__":main()
