"""Studio V0.5 RX-only: doppio varicap BB204G a catodo comune.
NON simulazione SPICE. Curve C(V) FIT nominali con ipotesi Vj=0.8 V.
"""
from __future__ import annotations
import math
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"02_Piano_Frequenze/V0.2"))
from frequency_plan_v02 import all_rows,rx_plan

L_NH = 150.0
C_FIXED_PF_ASSUMED = 61.0  # serie Cfeedback/emit, Cjc, PCB, trimmer: NON un singolo componente
C_BLOCK_PF = 1000.0
VJ_V = 0.8
C_3V_PF_MIDPOINT = 36.5
C_30V_PF_TYP = 14.0
M_FIT = math.log(C_3V_PF_MIDPOINT / C_30V_PF_TYP) / math.log((1 + 30 / VJ_V) / (1 + 3 / VJ_V))
CJO_FIT_PF = C_3V_PF_MIDPOINT * (1 + 3 / VJ_V) ** M_FIT

def c_single_pf(v_reverse_v):
    """Fit di capacità di singolo diodo; validità limitata alle ancore 3..30 V."""
    if not 3.0 <= v_reverse_v <= 30.0:
        raise ValueError("Outside 3-30V characterization anchors")
    return CJO_FIT_PF / (1 + v_reverse_v / VJ_V)**M_FIT

def effective_dual_varicap_pf(v_reverse_v, c_block_pf=C_BLOCK_PF):
    """Due giunzioni in parallelo, poi condensatore DC block in serie."""
    c_par = 2.0 * c_single_pf(v_reverse_v)
    if c_block_pf <= 0: raise ValueError("invalid DC block")
    return (c_block_pf * c_par) / (c_block_pf + c_par)

def frequency_hz(v_reverse_v, l_nh=L_NH, cfixed_pf=C_FIXED_PF_ASSUMED):
    if l_nh <= 0 or cfixed_pf <= 0:raise ValueError("nonphysical LC")
    ceff_pf = cfixed_pf + effective_dual_varicap_pf(v_reverse_v)
    return 1/(2*math.pi*math.sqrt(l_nh*1e-9*ceff_pf*1e-12))

def required_vtune_v(f_hz, l_nh=L_NH, cfixed_pf=C_FIXED_PF_ASSUMED):
    if f_hz<=0 or l_nh<=0 or cfixed_pf<=0:raise ValueError("nonphysical")
    req_pf=1/(4*math.pi**2*f_hz*f_hz*l_nh*1e-9)/1e-12-cfixed_pf
    if req_pf<=0 or req_pf>=C_BLOCK_PF:raise ValueError("capacitance geometry outside")
    c_par = req_pf*C_BLOCK_PF/(C_BLOCK_PF-req_pf)
    c_each = c_par/2
    v=VJ_V*((CJO_FIT_PF/c_each)**(1/M_FIT)-1)
    if not 3<=v<=30:raise ValueError("required V outside characterized model")
    return v

def all_channel_biases():
    rows=[]
    for d in all_rows():
        v=required_vtune_v(d["lo_hz"])
        rows.append(dict(banda=d["banda"],canale=d["canale"],n=d["n"],
                         lo1_hz=d["lo_hz"],vtune_v_model=v,tx_permitted=False))
    return rows

def passive_b_type_response_hz(f_hz,r1=2200.,r2=10000.,c=100e-9):
    if min(r1,r2,c)<=0 or f_hz<0:raise ValueError("invalid parameters")
    s=complex(0,2*math.pi*f_hz)
    return (1+s*r2*c)/(1+s*(r1+r2)*c)

def two_rc_response_hz(f_hz,r1=10000.,c1=10e-9,r2=10000.,c2=100e-9):
    """Nodi RC a cascata passiva con CARICO INFINITO: NON filtro PLL dimensionato."""
    if min(r1,r2,c1,c2)<=0 or f_hz<0:raise ValueError("invalid parameters")
    s=complex(0,2*math.pi*f_hz)
    return 1/(1+s*(r1*c1+r1*c2+r2*c2)+s*s*r1*r2*c1*c2)

def magnitude_db(h):
    return 20*math.log10(abs(h))

def bjt_bias_estimate(vcc=9.0,r_top=33000.,r_bot=10000.,re=330.,vbe=0.70):
    """Bias senza carico base, beta o effetti RF: limite inferenziale."""
    vb=vcc*r_bot/(r_top+r_bot)
    ve=max(0.,vb-vbe)
    return dict(base_v_ideal=vb,emitter_v_ideal=ve,
                emitter_current_a_ideal=ve/re)

def safety_model(*,all_stable,pll_lock):
    return dict(rx_unmute_candidate=bool(all_stable and pll_lock),
                rf_tx_enable=False, fabrication_authorized=False)

if __name__=="__main__":
    for r in (all_channel_biases()[0],all_channel_biases()[-1]):print(r)
    print("Vtune range",min(x["vtune_v_model"] for x in all_channel_biases()),
          max(x["vtune_v_model"] for x in all_channel_biases()))
    print("original filter 5kHz dB",magnitude_db(passive_b_type_response_hz(5000)))
    print("twoRC candidate 5kHz dB",magnitude_db(two_rc_response_hz(5000)))
