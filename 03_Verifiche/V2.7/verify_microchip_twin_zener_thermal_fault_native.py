#!/usr/bin/env python3
"""KiCad9 netlist anchored Microchip twin low-current Zener mismatch/stress screen.

OEM data points are applied ONLY at their published measurement conditions.
All extrapolated knee/current-sharing relationships are labelled SYNTHETIC.
No safety qualification, production, power-up, vehicle, or TX is implied.
"""
from pathlib import Path
import itertools
import math
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets, require
from verify_q806_dual_zener_clamp_native import N as EXPECTED

SCH=ROOT/"04_KiCad/V2.7_DRAFT/MAIN_SECONDARY_OVP_Q804_Q805_Q806_LOW_CURRENT_ZENER/MAIN_SECONDARY_OVP_Q804_Q805_Q806_LOW_CURRENT_ZENER_LAB_V2_7_DRAFT.kicad_sch"
# Microsemi/Microchip OEM 1N4106-1 (datasheet 1N4099-1..1N4135-1):
# VZ nominal = 12V at IZT=250 uA (+/-5% commercial), 200 ohm MAX
# ZZT @ IZT only, IZM 32mA, 500mW at 25C and thermal
# derating to zero @ 175C. These do not define its full I-V function.
OEM_IZT_A=.000250
OEM_VZ_NOM=12.
OEM_ZZT_MAX_OHM=200.
OEM_IZM_A=.032
OEM_P_RATED_W=.5
OEM_DERATE_START_C=25.
OEM_DERATE_END_C=175.
OEM_TEMP_COEFF_MAX_FRACTION_PER_C=.0008

def synthetic_node(vsource,rgs,rseries,branch_states,vspec,rz):
    """Floating common source treated as imposed ideal Vsource.

    branch_states: 1 active synthetic Zener, 0 open, -1 short circuit.
    Piecewise linear Zener I=max(0, (Vgs-Vspec)/rz), with no OEM validity
    except its approximate shape; diode short means Vgs=0 model only.
    """
    if -1 in branch_states:
        return 0.
    def kcl(v):
        iz=sum(max(0.,(v-vz)/r) for state,vz,r in zip(branch_states,vspec,rz) if state==1)
        return (vsource-v)/rseries - v/rgs-iz
    low,high=0.,vsource
    for _ in range(75):
        mid=(low+high)/2.
        if kcl(mid)>0.:low=mid
        else:high=mid
    v=(low+high)/2.
    assert abs(kcl(v))<1e-10
    return v

def derated_max_w(temp_c):
    # OEM datasheet footnote: ambient power derates linearly 25->175C
    return OEM_P_RATED_W*max(0.,min(1.,(OEM_DERATE_END_C-temp_c)/(OEM_DERATE_END_C-OEM_DERATE_START_C)))

def main():
    s=SCH.read_text(encoding="utf8")
    for token in ("KSP42BU_NPN_CANDIDATE","1N4106-1_MICROCHIP_250UA_CANDIDATE",
                  "1N4106-1_SECOND_PARALLEL_250UA_LAB",
                  "NO FAB / NO TX / NO BATTERIA / NO VEICOLO"):
        assert token in s,token
    # CAD contains a placeholder DIN0309 body for R2102; DO NOT assume
    # it is a power rating or replace it with DIN0207 in documentation.
    # Verify the explicit R2102 property in the symbol instance, not
    # an unrelated resistor/embedded library default footprint.
    import re
    r2102=re.search(r'\\(property "Reference" "R2102".*?\\(property "Footprint" "([^"]+)"',
                    s,flags=re.S)
    assert r2102 is not None
    assert r2102.group(1)=="Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal"
    with tempfile.TemporaryDirectory(prefix="microchip_thermal_native_") as tmp:
        nets=exported_nets(SCH,Path(tmp)/"microchip_thermal.net")
    assert len(nets)==8 and set(nets)==set(EXPECTED)
    for name,pins in EXPECTED.items():
        require(nets,name,*pins)
        assert nets[name]==pins,(name,sorted(nets[name]))
    assert sum(map(len,nets.values()))==27
    assert ("D2101","1") in nets["FLOATING_COMMON_SOURCE_LAB"]
    assert ("D2102","1") in nets["FLOATING_COMMON_SOURCE_LAB"]
    assert ("D2101","2") in nets["COMMON_GATE_LAB"]
    assert ("D2102","2") in nets["COMMON_GATE_LAB"]
    assert not nets["LAB_RETURN_ONLY"] & nets["FLOATING_COMMON_SOURCE_LAB"]

    # Explicit resistor and shorted-clamp envelope, not a rated design.
    rseries_min=9500.
    absolute_branch_peak_A=48./rseries_min
    resistor_worst_short_W=48.**2/rseries_min
    assert absolute_branch_peak_A<OEM_IZM_A
    assert .24<resistor_worst_short_W<.25
    assert derated_max_w(85.)==.3
    assert derated_max_w(125.)==1/6
    assert derated_max_w(175.)==0.
    # R2102 footprint does not establish 0.25W resistor power or
    # hot derating: no safe claim from this computed dissipated power.
    assert resistor_worst_short_W > .25*.8

    count=0
    both_open_exceed=0
    one_open_exceed=0
    ideal_both_open_highest=0.
    any_healthy_current_imbalance=False
    one_shorted_highest_assertrisk=0.
    max_ideal_zener_current_A=0.
    min_source_for_250ua_one_diode=1e9
    synthetic_all_bounds_pass=True
    # Exhaustive 6 x 2^6 x 5 = 1920 corners with DIFFERENT Zener knees
    # and DIFFERENT synthetic resistances; no identical-diode shortcut.
    states=(("HEALTHY",(1,1)),("D1_OPEN",(0,1)),
            ("D2_OPEN",(1,0)),("BOTH_OPEN",(0,0)),
            ("D1_SHORT",(-1,1)))
    for vsource,rgs,rseries,vz1,vz2,rz1,rz2,temp,stateinfo in itertools.product(
        (0.,13.8,20.,24.,36.,48.),
        (44650.,49350.),
        (9500.,10500.),
        (11.4,12.6),
        (11.4,12.6),
        (0.1,10.),
        (0.1,10.),
        (-40.,25.,85.,125.),
        states
    ):
        mode,active=stateinfo
        # +/- 0.08%/C is a bound on the TEMP COEFFICIENT at OEM
        # test current, NOT guaranteed DC Vz over whole temperature domain.
        effective=(vz1*(1+OEM_TEMP_COEFF_MAX_FRACTION_PER_C*(temp-25.)),
                   vz2*(1+OEM_TEMP_COEFF_MAX_FRACTION_PER_C*(temp-25.)))
        vgs=synthetic_node(vsource,rgs,rseries,active,effective,(rz1,rz2))
        assert 0<=vgs<=vsource+1e-10
        currents=[max(0.,(vgs-vz)/r) if st==1 else 0.
                  for st,vz,r in zip(active,effective,(rz1,rz2))]
        if active[0]==active[1]==1 and abs(currents[0]-currents[1])>1e-7:
            any_healthy_current_imbalance=True
        if mode=="BOTH_OPEN":
            ideal_both_open_highest=max(ideal_both_open_highest,vgs)
            if vgs>20.:both_open_exceed+=1
        if mode in ("D1_OPEN","D2_OPEN") and vgs>20.:
            one_open_exceed+=1
        if mode=="D1_SHORT":
            one_shorted_highest_assertrisk=max(one_shorted_highest_assertrisk,vgs)
        total_iz=sum(currents)
        max_ideal_zener_current_A=max(max_ideal_zener_current_A,total_iz)
        # The 250uA OEM Vz test is NOT guaranteed at every source voltage.
        if mode in ("D1_OPEN","D2_OPEN") and total_iz>=OEM_IZT_A:
            min_source_for_250ua_one_diode=min(min_source_for_250ua_one_diode,vsource)
        if vgs>20. and mode!="BOTH_OPEN":
            synthetic_all_bounds_pass=False
        count+=1

    assert count==6*2**6*4*5==7680
    assert any_healthy_current_imbalance
    assert both_open_exceed>0
    assert one_open_exceed==0 and synthetic_all_bounds_pass
    assert ideal_both_open_highest>40.
    assert one_shorted_highest_assertrisk==0.
    assert max_ideal_zener_current_A<absolute_branch_peak_A
    assert min_source_for_250ua_one_diode<48.
    print("MICROCHIP_1N4106_TWIN_THERMAL_CURRENT_FAULT",{
        "native_nets":len(nets),"native_pins":sum(map(len,nets.values())),
        "synthetic_cases":count,
        "parallel_current_mismatch_produced":any_healthy_current_imbalance,
        "double_open_over_20V_cases":both_open_exceed,
        "single_open_over_20V_synthetic_cases":one_open_exceed,
        "double_open_max_abs_vgs_V":round(ideal_both_open_highest,5),
        "worst_48V_gate_path_current_mA":round(absolute_branch_peak_A*1000,6),
        "R2102_full_short_possible_W":round(resistor_worst_short_W,6),
        "OEM_diode_IZM_mA":OEM_IZM_A*1000,
        "OEM_diode_500mW_at_125C_derated_W":round(derated_max_w(125.),6),
        "OEM_zener_250uA_test_condition_global_VGS_guarantee":False,
        "R2102_temperature_derating_OEM_qualified":False,
        "KSP42_CE_short_failclosed":False,
        "manufacturer_dynamic_temperature_IV_qualified":False,
        "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True
    },flush=True)
    print("PASS_NATIVE_KICAD9_1N4106_TWIN_THERMAL_7680_SYNTHETIC_FAULT_NONFAB",flush=True)

if __name__=="__main__":
    main()
