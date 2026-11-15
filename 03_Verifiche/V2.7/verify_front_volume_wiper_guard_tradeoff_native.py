#!/usr/bin/env python3
"""FRONT pot fault mitigation: independent shunt-resistor tradeoff, not release.

This study screens an ALWAYS-CONNECTED resistor from RV1301 wiper (pin2)
directly to the external AF_GND, independent of potentiometer pin3.
A potentiometer terminal3 open is explicitly distinguished from an external
AF_GND harness open: the latter defeats the candidate and remains UNSAFE.
Reference real KiCad9 healthy nets; candidate is NOT mounted in CAD.
"""
from __future__ import annotations
import cmath
import math
from verify_am455_front_lm386_loaded_ac_native import (
    VALUES, FREQUENCIES, INPUT_RIN, WIPER_FRACTIONS,
    direct, check_actual_cad
)
from verify_front_volume_open_low_fault_kcl_native import series_parallel_open_low

GUARD_RESISTORS_OHM=(100.0,330.0,1000.0,3300.0,10000.0)
ATOL=3e-10

def reduction(freq:float,position:float,rin:float,guard:float,low_open:bool)->complex:
    """Rtop -> parallel(guard, optional Rbottom, C1201+R1201+Rin)."""
    omega=2*math.pi*freq
    zdet=1/(1j*omega*VALUES["C1502"])
    zamp=1/(1j*omega*VALUES["C1201"])+VALUES["R1201"]+rin
    rtop=(1-position)*VALUES["RV1301"]
    yparallel=1/guard+1/zamp
    if not low_open:
        yparallel+=1/(position*VALUES["RV1301"])
    zwiper=1/yparallel
    zload=1/(1/VALUES["R1502"]+1/(rtop+zwiper))
    return zload/(zdet+zload)*zwiper/(rtop+zwiper)*rin/zamp

def independent_kcl(freq:float,position:float,rin:float,guard:float,low_open:bool)->complex:
    """Three-node GJ solve with original-matrix residual, not the reduction."""
    omega=2*math.pi*freq
    ydet=1j*omega*VALUES["C1502"]
    ysh=1/VALUES["R1502"]
    ytop=1/((1-position)*VALUES["RV1301"])
    yguard=1/guard
    ylow=0. if low_open else 1/(position*VALUES["RV1301"])
    yamp=1/(VALUES["R1201"]+1/(1j*omega*VALUES["C1201"]))
    yin=1/rin
    m=[
        [ydet+ysh+ytop,-ytop,0j],
        [-ytop,ytop+ylow+yguard+yamp,-yamp],
        [0j,-yamp,yamp+yin],
    ]
    b=[ydet,0j,0j]
    original=[row[:] for row in m]
    original_b=b[:]
    for k in range(3):
        pivot=max(range(k,3),key=lambda i:abs(m[i][k]))
        assert abs(m[pivot][k])>1e-15
        m[k],m[pivot]=m[pivot],m[k]
        b[k],b[pivot]=b[pivot],b[k]
        scale=m[k][k]
        for j in range(k,3):m[k][j]/=scale
        b[k]/=scale
        for i in range(3):
            if i==k:continue
            a=m[i][k]
            for j in range(k,3):m[i][j]-=a*m[k][j]
            b[i]-=a*b[k]
    error=max(abs(sum(original[i][j]*b[j] for j in range(3))-original_b[i])
              for i in range(3))
    assert error<1e-8,(freq,position,rin,guard,low_open,error)
    return b[2]

def main():
    check_actual_cad()
    points=0
    summary=[]
    for guard in GUARD_RESISTORS_OHM:
        max_nominal_discrepancy=0.
        for freq in FREQUENCIES:
            for position in WIPER_FRACTIONS:
                for rin in INPUT_RIN:
                    normal=reduction(freq,position,rin,guard,False)
                    fault=reduction(freq,position,rin,guard,True)
                    assert abs(normal-independent_kcl(freq,position,rin,guard,False))<ATOL
                    assert abs(fault-independent_kcl(freq,position,rin,guard,True))<ATOL
                    baseline=direct(freq,position,rin)
                    unsafe=series_parallel_open_low(freq,position,rin)
                    assert 0<abs(normal)<abs(baseline)<1
                    assert 0<abs(fault)<abs(unsafe)<1
                    assert abs(fault)>abs(normal)
                    assert all(math.isfinite(x) for z in (normal,fault) for x in (z.real,z.imag))
                    max_nominal_discrepancy=max(max_nominal_discrepancy,abs(normal-baseline))
                    points+=1
        low_nom=abs(reduction(1000.,.01,50000.,guard,False))
        low_open=abs(reduction(1000.,.01,50000.,guard,True))
        high_nom=abs(reduction(1000.,.99,50000.,guard,False))
        unguarded_low_open=abs(series_parallel_open_low(1000.,.01,50000.))
        unguarded_high_nom=abs(direct(1000.,.99,50000.))
        summary.append({
            "guard_ohm":int(guard),
            "low_1pct_nominal":round(low_nom,8),
            "low_1pct_low_terminal_open":round(low_open,8),
            "low_fault_reduction_vs_unguarded":round(low_open/unguarded_low_open,6),
            "high_99pct_nominal":round(high_nom,8),
            "high_volume_retained_vs_unguarded":round(high_nom/unguarded_high_nom,6),
            "max_nominal_complex_transfer_deviation":round(max_nominal_discrepancy,6),
        })
    assert points==5*5*3*5==375
    assert all(a["low_fault_reduction_vs_unguarded"]<b["low_fault_reduction_vs_unguarded"]
               for a,b in zip(summary,summary[1:])),summary
    assert all(a["high_volume_retained_vs_unguarded"]<b["high_volume_retained_vs_unguarded"]
               for a,b in zip(summary,summary[1:])),summary
    # No candidate may be promoted as a no-loss safety solution.
    assert summary[0]["high_volume_retained_vs_unguarded"]<.1
    assert summary[-1]["low_fault_reduction_vs_unguarded"]>.5
    print("FRONT_WIPER_GUARD_1KHZ_50K_INPUT_TRADEOFF",summary,flush=True)
    print("FRONT_WIPER_GUARD_LIMITS",{
        "frequency_cases":len(FREQUENCIES),
        "wiper_cases":len(WIPER_FRACTIONS),
        "input_rin_cases":len(INPUT_RIN),
        "guard_resistor_candidates":len(GUARD_RESISTORS_OHM),
        "complex_cases_checked":points,
        "independent_gnd_required":True,
        "open_AF_GND_harness_not_mitigated":True,
        "open_guard_resistor_reverts_to_original_unsafe_fault":True,
        "no_mpn_oem_or_hw_qualification":True,
        "no_candidate_inserted_into_schematic_or_board":True,
        "NO_FAB_NO_TX":True},flush=True)
    print("PASS_FRONT_WIPER_GUARD_SHUNT_375_DUAL_KCL_CASES_NATIVE_PIN_MAP_NOT_FAILSAFE_RELEASE",flush=True)

if __name__=="__main__": main()
