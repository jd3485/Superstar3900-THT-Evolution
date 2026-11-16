#!/usr/bin/env python3
"""S-meter FRONT THT passive fault-power budget, native pin-net anchored.

Finite idealized cases only: real meter/pot OEM, thermal rating, source,
open returns and cable transients remain unknown. NO FAB / NO TX.
"""
from itertools import product
from math import isclose,isfinite
from verify_smeter_passive_source_loading_native import (
    reduction,native,POT,LIMIT,V_OPEN,SOURCE_R,COIL,SHORTS,WIPER)

def dissipations(v,rs,rc,shorts,w):
    terminal,isource,imeter,ilow=reduction(v,rs,rc,shorts,w)
    rh=POT*(1-w)
    rl=POT*w
    vw=imeter*((2-shorts)*LIMIT+rc)
    # Upper-track flow equals current drawn from source terminal.
    iupper=isource
    powers={
      "driver_source_ohm":isource*isource*rs,
      "pot_track_upper":iupper*iupper*rh,
      "pot_track_lower":ilow*ilow*rl,
      "series_100k_intact_total":imeter*imeter*((2-shorts)*LIMIT),
      "meter_coil_hypothetical":imeter*imeter*rc}
    assert all(isfinite(p) and p>=0 for p in powers.values())
    assert isclose(isource,imeter+ilow,rel_tol=1e-10,abs_tol=1e-12)
    assert isclose(v*isource,sum(powers.values()),rel_tol=1e-10,abs_tol=1e-10),(
        v,rs,rc,shorts,w,powers,v*isource)
    assert isclose(terminal*isource,sum(p for k,p in powers.items()
                                      if k!="driver_source_ohm"),rel_tol=1e-10,abs_tol=1e-10)
    if shorts==0:
        assert isclose(powers["series_100k_intact_total"],2*LIMIT*imeter*imeter)
    if shorts==2:
        assert powers["series_100k_intact_total"]==0
    return powers

def main():
    native()
    cases=0
    peak={k:{"watts":-1., "scenario":None} for k in
          ("driver_source_ohm","pot_track_upper","pot_track_lower",
           "series_100k_intact_total","meter_coil_hypothetical")}
    for case in product(V_OPEN,SOURCE_R,COIL,SHORTS,WIPER):
        p=dissipations(*case)
        for k,x in p.items():
            if x>peak[k]["watts"]:
                peak[k]={"watts":x,"scenario":case}
        cases+=1
    assert cases==675
    # No resistive guard short: sample 11V, 20k coil, trim all high.
    nominal=dissipations(11.,0.,20000.,0,1.)
    assert isclose(nominal["pot_track_lower"],.0121)
    assert isclose(nominal["series_100k_intact_total"],.0005)
    assert isclose(nominal["meter_coil_hypothetical"],.00005)
    assert isclose(sum(nominal.values()),.01265)
    # A 20V source with two shorted protection resistors and 1k movement
    # is a materially higher fault power, not a qualified meter rating.
    fault=dissipations(20.,0.,1000.,2,1.)
    assert isclose(fault["meter_coil_hypothetical"],.4)
    assert isclose(fault["pot_track_lower"],.04)
    print("FRONT_SMETER_NATIVE_675_FAULT_POWER_CONSERVATION",{
      "cases":cases,
      "peak_power_watts_and_scenarios":peak,
      "11V_healthy_20kcoil_power_W":nominal,
      "20V_two_short_1kcoil_fault_power_W":fault,
      "real_R1801_R1802_MPN_derating_qualified":False,
      "real_RV1801_pot_power_rating_qualified":False,
      "real_meter_coil_thermal_limit_qualified":False,
      "real_MAIN_drive_voltage_bound_known":False,
      "NO_FAB_NO_TX":True},flush=True)
    print("PASS_NATIVE_KICAD9_FRONT_SMETER_675_POWER_CONSERVATION_FAULT_SCREEN_NONFAB",flush=True)

if __name__=="__main__":main()
