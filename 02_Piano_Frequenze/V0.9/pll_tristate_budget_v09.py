"""V0.9 analytical open-loop three-state PDout RC exploration.

This does NOT compute closed-loop transfer function phase margin, PD Kphi, or
charge pump effective output impedance; all parameters are explicitly assumed.
"""
import math,json
PFD_REF_HZ=5000.0
VDD_PLL_V=5.0
PDOUT_PIN_ML145151=4
R_OPTIONS_OHM=(10000.0,47000.0)
C_OPTION_F=1e-6
R_LEAK_MODEL_OHM=100e6
OUTPUT_HIGH_ASSUMED_V=5.0
VCO_FREQ_MHZ_VTUNE8=36.04773
VCO_FREQ_MHZ_VTUNE15=39.19647
VCO_RANGE_VTUNE_V=(8.0,15.0)
LM358_GAIN_ASSUMED=4.0
INPUT_BIAS_ASSUMED_A=20e-9

def time_constant_s(r,c=C_OPTION_F):
    if r<=0 or c<=0:raise ValueError("R/C must be positive")
    return r*c

def corner_hz(r,c=C_OPTION_F):
    return 1/(2*math.pi*time_constant_s(r,c))

def attenuation_db(freq_hz,r,c=C_OPTION_F):
    if freq_hz<0:raise ValueError("frequency must be nonnegative")
    return -10*math.log10(1+(2*math.pi*freq_hz*time_constant_s(r,c))**2)

def small_pulse_step_v(r,pulse_seconds=1e-3,start_v=2.5,target_v=5.0):
    if pulse_seconds<0:raise ValueError("time negative")
    return (target_v-start_v)*(1-math.exp(-pulse_seconds/time_constant_s(r)))

def hold_voltage_v(start_v=2.5,seconds=.03,leak_ohm=R_LEAK_MODEL_OHM):
    if seconds<0 or leak_ohm<=0:raise ValueError("invalid")
    return start_v*math.exp(-seconds/(leak_ohm*C_OPTION_F))

def bias_input_drift_v(seconds,ibias=INPUT_BIAS_ASSUMED_A):
    if seconds<0 or ibias<0:raise ValueError("invalid")
    return ibias*seconds/C_OPTION_F

def vco_slope_mhz_v_sampled():
    return (VCO_FREQ_MHZ_VTUNE15-VCO_FREQ_MHZ_VTUNE8)/(VCO_RANGE_VTUNE_V[1]-VCO_RANGE_VTUNE_V[0])

def require_physical_pll_gates():
    return {"vco_fine_calibration":"OPEN","pfd_charge_drive_characterized":False,
            "loop_phase_margin":"NOT_RUN","lock_detector_debounced":False,
            "powergood_hardware":False,"kicad_erc":"NOT_RUN",
            "tx_authorized":False,"fabrication_authorized":False}

def report():
    return {
        "PDout_pin":PDOUT_PIN_ML145151,
        "phase_detector_type":"three_state_output_real_datasheet_idealized_surrogate",
        "ref_hz":PFD_REF_HZ,
        "voltage_supply_v":VDD_PLL_V,
        "ranges":[{"r_ohm":r,"c_f":C_OPTION_F,
                   "time_constant_ms":1000*time_constant_s(r),
                   "f_corner_hz":corner_hz(r),
                   "attenuation_at_pfd_db_ideal":attenuation_db(PFD_REF_HZ,r),
                   "step_v_one_1ms_pulse":small_pulse_step_v(r)}
                  for r in R_OPTIONS_OHM],
        "hold_initial_2p5_after_30ms_v":hold_voltage_v(),
        "bias_current_example_drift_30ms_v":bias_input_drift_v(.03),
        "sampled_vco_kvco_mhz_per_v_not_vendor":vco_slope_mhz_v_sampled(),
        "sampled_input_sensitivity_lo_mhz_per_pd_filter_v":vco_slope_mhz_v_sampled()*LM358_GAIN_ASSUMED,
        "loop_and_device_qualification":require_physical_pll_gates()
    }
if __name__=="__main__":
 print(json.dumps(report(),indent=2))
