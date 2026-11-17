#!/usr/bin/env python3
"""KiCad9 FRONT G5V-1 5V coil drive headroom, hypothetical PVT fault screening.

No OEM BC337 VCE(sat) curve, no thermal or true contact reliability guarantee.
Tests actual two series NPN collector/emitter net topology from FRONT parent.
"""
from itertools import product
from pathlib import Path
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets, require
from verify_front_partial_hierarchy_native import SCH as FRONT
from verify_front_g5v1_six_terminal_oem_pin_map_native import OEM_TO_EXISTING_NET

RAILS=(4.50,4.75,5.,5.25)     # hypothetical regulated 5V source corner
SAT=(0.1,0.3,0.6)            # assumed per-BJT VCE saturated drops [V]
RCOIL=(167*.90,167.,167*1.10) # 23C OEM 167Ω ±10%
V_OPERATE_MAX_23C=4.0       # standard G5V-1 5V must-operate <=80%, 23C

def main():
    with tempfile.TemporaryDirectory(prefix="tht_front_relay_headroom_") as td:
        nets=exported_nets(FRONT,Path(td)/"front.net")
    # FRONT hierarchy native KiCad9 exports '/' page-path in some net names.
    def pins(name):
        matches=[v for k,v in nets.items() if k.rsplit("/",1)[-1]==name]
        assert len(matches)==1,(name,sorted(nets))
        return matches[0]
    require({"COIL_PLUS_LAB":pins("COIL_PLUS_LAB")},"COIL_PLUS_LAB",
            ("K1901","4"),("J1911","1"),("J1914","1"))
    require({"COIL_MINUS_LAB":pins("COIL_MINUS_LAB")},"COIL_MINUS_LAB",
            ("K1901","5"),("Q1911","1"),("D1911","2"))
    require({"SERIES_MID":pins("SERIES_MID")},"SERIES_MID",
            ("Q1911","3"),("Q1912","1"))
    require({"DRIVER_GND":pins("DRIVER_GND")},"DRIVER_GND",
            ("Q1912","3"),("J1911","2"))
    assert pins("COIL_PLUS_LAB").isdisjoint(pins("COIL_MINUS_LAB"))
    assert pins("SERIES_MID").isdisjoint(pins("DRIVER_GND"))
    assert {OEM_TO_EXISTING_NET["2"],OEM_TO_EXISTING_NET["9"]}=={
      "COIL_PLUS_LAB","COIL_MINUS_LAB"}
    n=above=below=0;minv=100.;maxv=-100.;imin=100.;imax=-100.
    byrail={}
    for rail,a,b,r in product(RAILS,SAT,SAT,RCOIL):
        # Hypothetical closed dual series switch, no base/gain/load checks.
        vcoil=max(0.,rail-a-b)
        i=vcoil/r
        assert 0 <= vcoil <= rail and i >=0
        minv=min(minv,vcoil);maxv=max(maxv,vcoil)
        imin=min(imin,i);imax=max(imax,i)
        if vcoil>=V_OPERATE_MAX_23C:
            above+=1
        else:
            below+=1
        byrail.setdefault(rail,[0,0])
        byrail[rail][int(vcoil<V_OPERATE_MAX_23C)]+=1
        n+=1
    assert (n,above,below)==(108,78,30)
    assert abs(minv-3.3)<1e-9 and abs(maxv-5.05)<1e-9
    assert abs(imin-3.3/(167*1.1))<1e-10
    assert abs(imax-5.05/(167*.9))<1e-10
    assert sum(sum(v) for v in byrail.values())==108
    # No independent base-current/saturation justification, no output relay.
    # Passing nominal 4V is NOT proof of G5V-1 reliable pull-in across temp.
    print("FRONT_G5V1_COIL_HEADROOM_NATIVE_NONQUALIFYING",{
      "native_series_sink":"Q1911 E pin3 -> Q1912 C pin1, Q1912 E pin3 -> DRIVER_GND",
      "hypothetical_scenarios":n,
      "coil_voltage_ge_4V_23C_scenario_count":above,
      "coil_voltage_lt_4V_23C_scenario_count":below,
      "coil_voltage_range_V":[round(minv,4),round(maxv,4)],
      "coil_current_range_mA":[round(imin*1000,3),round(imax*1000,3)],
      "per_rail_pass_fail":byrail,
      "oem_BC337_VCEsat_and_base_drive_verified":False,
      "ambient_temperature_qualification":False,
      "coil_contact_actuation_guaranteed":False,
      "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True
    },flush=True)
    print("PASS_NATIVE_FRONT_G5V1_DUAL_NPN_COIL_HEADROOM_108_NONFAB",flush=True)

if __name__=="__main__":main()
