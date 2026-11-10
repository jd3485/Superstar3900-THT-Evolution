"""Analisi ideale V0.4 di accordo VCO (RX-only). NON modello SPICE.
BB204G Philips: C3=34..39 pF, C30 tipico=14 pF. Tensioni non operative.
Le capacita reali in circuito, Q e variazioni termiche NON sono simulate.
"""
import math
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'02_Piano_Frequenze/V0.2'))
from frequency_plan_v02 import all_rows
L_CANDIDATE_H=220e-9
C_FIXED_EFFECTIVE_PF=57.5
F_LO_MIN=36_310_000
F_LO_MAX=39_000_000
C3_LOW_PF=34.0
C3_HIGH_PF=39.0
C30_TYP_PF=14.0
C3_TYP_EST_PF=36.5 # midpoint of min/max, NOT manufacturer typical value
V_3=3.0
V_30=30.0
R_LOOP_1_OHM=2200.0
R_LOOP_2_OHM=10000.0
C_LOOP_F=100e-9
F_PFD=5000.0

def tank_ceq_pf(f_hz,l_h=L_CANDIDATE_H):
    if f_hz<=0 or l_h<=0: raise ValueError('invalid resonator')
    return 1e12/((2*math.pi*f_hz)**2*l_h)

def nominal_lo_hz(c_var_pf,c_fixed_pf=C_FIXED_EFFECTIVE_PF,l_h=L_CANDIDATE_H):
    if min(c_var_pf,c_fixed_pf,l_h)<=0:raise ValueError('nonphysical resonator')
    return 1/(2*math.pi*math.sqrt(l_h*(c_var_pf+c_fixed_pf)*1e-12))

def tuning_exponent(c3=C3_TYP_EST_PF,c30=C30_TYP_PF):
    if c3<=c30 or c30<=0:raise ValueError('invalid capacitances')
    return math.log(c3/c30)/math.log(10)

def interpolated_varactor_pf(v_rev):
    # POWER LAW INTERPOLATION ASSUMPTION, NOT a datasheet guarantee
    if not 3<=v_rev<=30:raise ValueError('outside model anchors')
    return C3_TYP_EST_PF*(v_rev/3)**(-tuning_exponent())

def interpolated_voltage_v(f_lo):
    # Inverse interpolated model; no active loop analysis or DAC implementation
    c_req=tank_ceq_pf(f_lo)-C_FIXED_EFFECTIVE_PF
    if c_req<=0:raise ValueError('outside tank geometry')
    v=3*(C3_TYP_EST_PF/c_req)**(1/tuning_exponent())
    if not 3<=v<=30:raise ValueError('outside varactor model range')
    return v

def sweep_all_channels():
    data=[]
    for row in all_rows():
        lo=row['lo_hz']
        data.append({'banda':row['banda'],'canale':row['canale'],
                     'n':row['n'],'lo1_hz':lo,'vtune_v_assumed':interpolated_voltage_v(lo),
                     'tx_permitted':False})
    return data

def filter_pole_zero_hz(r1=R_LOOP_1_OHM,r2=R_LOOP_2_OHM,c=C_LOOP_F):
    # PDout -> R1 -> VTUNE ; VTUNE -> R2 -> C -> GND (passive lead/lag)
    # F(s)=(1+s*R2*C)/(1+s*(R1+R2)*C) by manufacturer
    if min(r1,r2,c)<=0:raise ValueError('invalid passive values')
    return {'pole_hz':1/(2*math.pi*(r1+r2)*c),
            'zero_hz':1/(2*math.pi*r2*c),
            'phase_margin_verified':False,'closed_loop_stable_verified':False}

def gate_rx(*,pll_lock,valid_n,ref_ok,rail_ok,retune_complete):
    valid=all((pll_lock,valid_n,ref_ok,rail_ok,retune_complete))
    return {'rx_unmute_candidate':valid,'rf_tx_enable':False,'fab_authorized':False}

if __name__=='__main__':
    print('C requirements pF',round(tank_ceq_pf(F_LO_MIN),3),round(tank_ceq_pf(F_LO_MAX),3))
    print('V(tuning) models V',round(interpolated_voltage_v(F_LO_MIN),3),round(interpolated_voltage_v(F_LO_MAX),3))
    print('Channels',len(sweep_all_channels()),'TX=False')
