#!/usr/bin/env python3
"""Native V2.6 LM393 supervisor dual-open fault diagnostic; NOT safety release.

D806 ideal 15V Zener and U802 TL431 open/healthy statuses are simplified
independent faults; LM393 consumption is assumed and does not establish
a guaranteed fault-safe supervisor or automotive input rating.
"""
from itertools import product
from pathlib import Path
import json,subprocess,tempfile,sys
from math import isclose
# Shared native KiCad netlist exporter lives in V2.7, not V2.6.
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"V2.7"))
from verify_interboard_audio_contract_native import exported_nets,require

ROOT=Path(__file__).resolve().parents[2]
SCH=ROOT/"04_KiCad/V2.6/PLL_RX_HIERARCHICAL_MASTER_V2.6.kicad_sch"
VIN=(10.,11.5,13.8,16.5,24.,36.,48.)
VF=(.2,.4,.7)
RS=(779.,820.,861.)
RB=(1710.,1800.,1890.)
VREF=(2.45,2.50,2.55)
ICC=(.0005,.001,.002,.003)
ZENER_IDEAL=15.
LM393_VCC_ABS_MAX=36.

def rail_equiv(vin,vf,r1011,r1001,vref,icc,tl431_open,d806_open):
    """Closed-form KCL with TL431 current only in healthy regulation hypothesis."""
    vsource=vin-vf
    if tl431_open:
        # No TL431 current; ONLY assumed LM393 Icc remains.
        vfree=vsource-r1011*icc
    else:
        # TL431 hypothetical maintained 2.5V cathode/reference.
        vfree=(vsource-r1011*icc+r1011*vref/r1001)/(1+r1011/r1001)
        assert vfree>vref, "Healthy TL431 regulation hypothesis invalid"
    clamped=(not d806_open and vfree>ZENER_IDEAL)
    v=ZENER_IDEAL if clamped else vfree
    ik=0. if tl431_open else (v-vref)/r1001
    iz=max(0.,(vsource-v)/r1011-icc-ik) if clamped else 0.
    assert isclose((vsource-v)/r1011,icc+ik+iz,rel_tol=2e-12,abs_tol=2e-12)
    return v,ik,iz,clamped

def rail_numeric(vin,vf,r1011,r1001,vref,icc,tl431_open,d806_open):
    """Independent monotone nodal root via bisection, including diode clamp."""
    vs=vin-vf
    def residual(v):
        load=icc+(0. if tl431_open else (v-vref)/r1001)
        if not d806_open and v>ZENER_IDEAL:
            # Ideal Zener forces 15V; solve free branch, cap afterwards.
            return (vs-v)/r1011-load
        return (vs-v)/r1011-load
    lo=0.;hi=vs
    assert residual(lo)>0 and residual(hi)<0
    for _ in range(85):
        mid=(hi+lo)/2
        if residual(mid)>0:lo=mid
        else:hi=mid
    v=(hi+lo)/2
    return min(v,ZENER_IDEAL) if not d806_open else v

def native():
    with tempfile.TemporaryDirectory(prefix="v26_ovp_dual_open_") as d:
        nets=exported_nets(SCH,Path(d)/"main.net")
    def same(name,*pairs):
        require(nets,name,*pairs)
    # On the real 7-sheet MAIN export, child-local nets carry the sheet
    # hierarchy prefix. Do not silently alias standalone and parent labels.
    same("FUSED_13V8_INPUT/OVP_CTL_VCC",("R1011","2"),("D806","1"),("R1001","1"),("U801","8"))
    same("FUSED_13V8_INPUT/OVP_PRECLAMP",("R1011","1"),("D804","1"))
    same("GND",("D806","2"),("U801","4"),("U802","2"))
    # Zener & TL431 share return, but not their cathodes.
    a=[name for name,pins in nets.items() if ("U802","1") in pins]
    assert len(a)==1
    assert ("R1001","2") in nets[a[0]] and ("U802","3") in nets[a[0]]
    assert a[0]!="FUSED_13V8_INPUT/OVP_CTL_VCC"
    assert len(nets)==76

def main():
    native()
    rows=0;unsafe_dual=0;bad_single=0;max_dual=(0.,None)
    state_counts={}
    for params in product(VIN,VF,RS,RB,VREF,ICC):
        vin,vf,rs,rb,vref,icc=params
        for tl_open,d_open in product((False,True),repeat=2):
            v,ik,iz,clamped=rail_equiv(*params,tl_open,d_open)
            numerical=rail_numeric(*params,tl_open,d_open)
            assert isclose(v,numerical,rel_tol=1e-11,abs_tol=1e-10),(params,tl_open,d_open,v,numerical)
            key=("TL431_OPEN" if tl_open else "TL431_REGULATING")+"/"+("D806_OPEN" if d_open else "D806_IDEAL")
            state_counts[key]=state_counts.get(key,0)+1
            if tl_open and d_open:
                unsafe_dual+=v>LM393_VCC_ABS_MAX
                if v>max_dual[0]:max_dual=(v,params)
            if not tl_open and d_open and v>=LM393_VCC_ABS_MAX:bad_single+=1
            rows+=1
    assert rows==9072
    assert set(state_counts.values())=={2268}
    assert unsafe_dual>0 and bad_single==0
    assert isclose(rail_equiv(48.,.2,779.,1800.,2.5,.0005,True,True)[0],47.4105)
    assert rail_equiv(48.,.2,779.,1800.,2.5,.0005,True,False)[0]==15.
    assert rail_equiv(48.,.2,779.,1800.,2.5,.0005,False,True)[0]<36.
    print("V26_LM393_D806_TL431_NATIVE_COMBINED_OPEN_FAULT",{
       "cases":rows,"cases_each_state":2268,
       "dual_open_above_36V_cases":unsafe_dual,
       "single_D806_open_TL431_hypothetical_regulating_above_36V_cases":bad_single,
       "max_dual_open_V_and_hypothetical_case":max_dual,
       "diotec_zener_iv_verified":False,
       "LM393_max_supply_36V":LM393_VCC_ABS_MAX,
       "TL431_stays_regulating_during_fault_qualified":False,
       "LM393_actual_current_during_fault_qualified":False,
       "OVP_fail_closed_qualified":False,
       "reverse_transient_energy_qualified":False,
       "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True},flush=True)
    print("PASS_NATIVE_KICAD9_V26_OVP_9072_DUAL_OPEN_RAIL_FAULT_CASES_NONFAB",flush=True)

if __name__=="__main__":main()
