"""V0.9 linearized receive PLL math, grounded in the V0.6 FIVE sample VCO curve.
NO vendor Kphi, real VCO Kvco/temp, PFD switch impedance, PCB spur or loop-lock proof.
Lansdale ML145151 datasheet equation: PDout nominal Kphi=VDD/(4*pi) V/rad;
N is TOTAL division from LO to 5 kHz comparison (includes /2 prescaler).
Proposed model only: R901=22k, C901=100n; LM358 noninvert nominal gain4.
"""
from __future__ import annotations
import math,json
from pathlib import Path
from dataclasses import dataclass
ROOT=Path(__file__).resolve().parents[2]
VCO_DATA_PATH=ROOT/"03_Verifiche/V0.6/MISURE_SPICE_V0.6.json"
F_PFD_HZ=5000.
PD_VDD_V=5.
PD_PIN=4
LD_PIN=28
PDOUT_ON_LOCK="HIGH_IMPEDANCE"
LOOP_R_OHM=22000.
LOOP_C_F=100e-9
LOOP_GAIN_ASSUMED=4.0
BIAS_CURRENT_ASSUMED_A=20e-9
HOLD_SECS_ASSUMED=.015
REF_FREQUENCY_HZ=10_240_000.
R_DIVIDER=2048
PRESCALER=2
def source_points():
    data=json.loads(VCO_DATA_PATH.read_text())
    p=data["candidateB"]
    return [(float(v),float(f)*1e6) for v,f in zip(p["vtune_v"],p["frequency_mhz"])]
@dataclass(frozen=True)
class SmallSignal:
    vtune_start_v:float
    vtune_end_v:float
    midpoint_hz:float
    sample_kvco_hz_per_v:float
    total_divider_nominal:float
    natural_frequency_hz:float
    damping_factor:float
    overshoot_fraction_ideal:float
    settling_2pct_ms_ideal:float
def linear_segments():
    out=[]
    pairs=source_points()
    kphi=PD_VDD_V/(4*math.pi)
    tau=LOOP_R_OHM*LOOP_C_F
    for (v0,f0),(v1,f1) in zip(pairs,pairs[1:]):
        k=(f1-f0)/(v1-v0)
        navg=(f0+f1)/2/F_PFD_HZ
        kvco_angular=2*math.pi*LOOP_GAIN_ASSUMED*k
        wn=math.sqrt(kphi*kvco_angular/(navg*tau))
        z=1/(2*wn*tau)
        overshoot=math.exp(-math.pi*z/math.sqrt(1-z*z)) if z<1 else 0.
        out.append(SmallSignal(v0,v1,(f0+f1)/2,k,navg,
                               wn/(2*math.pi),z,overshoot,4000/(z*wn)))
    return out
def rc_5khz_attenuation_db():
    w=2*math.pi*F_PFD_HZ*LOOP_R_OHM*LOOP_C_F
    return -10*math.log10(1+w*w)
def nominal_hold_voltage_drift(t=HOLD_SECS_ASSUMED,current=BIAS_CURRENT_ASSUMED_A):
    if t<0 or current<0:raise ValueError("nonphysical hold assumptions")
    return current*t/LOOP_C_F*LOOP_GAIN_ASSUMED
def max_frequency_drift_assumed_hz(t=HOLD_SECS_ASSUMED,current=BIAS_CURRENT_ASSUMED_A):
    return nominal_hold_voltage_drift(t,current)*max(x.sample_kvco_hz_per_v for x in linear_segments())
def rx_unmute_contract(*,supply_ok,ref_ok,ld_stable,channel_stable,settling_elapsed):
    return {"rx_unmute_allowed":all((supply_ok,ref_ok,ld_stable,channel_stable,settling_elapsed)),
            "rf_tx_enable":False,"fabrication_authorized":False}
def summary():
    return {
      "datasheet":"Lansdale ML145151 legacy, PDout pin4 and LD pin28",
      "pdout_state_on_lock":PDOUT_ON_LOCK,"kphi_v_per_rad_ideal":PD_VDD_V/(4*math.pi),
      "f_pfd_hz":REF_FREQUENCY_HZ/R_DIVIDER,
      "prescaler":PRESCALER,
      "small_signal_segments":[vars(x) for x in linear_segments()],
      "rc_pole_hz":1/(2*math.pi*LOOP_R_OHM*LOOP_C_F),
      "rc_attenuation_5khz_db_ideal":rc_5khz_attenuation_db(),
      "nominal_leakage_assumption_a":BIAS_CURRENT_ASSUMED_A,
      "hold_time_s":HOLD_SECS_ASSUMED,
      "hold_vtune_error_v":nominal_hold_voltage_drift(),
      "max_hold_lo_error_hz_assumed":max_frequency_drift_assumed_hz(),
      "full_vco_closed_loop_model":False,"verified_phase_margin":False,
      "frequency_accuracy_hardware_verified":False,
      "kicad_full_radio_erc":"NOT_RUN",
      "tx_authorized":False,"fabrication_authorized":False
    }
if __name__=="__main__":
 print(json.dumps(summary(),indent=2))
