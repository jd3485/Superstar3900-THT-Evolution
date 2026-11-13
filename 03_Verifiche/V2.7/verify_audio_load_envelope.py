#!/usr/bin/env python3
"""Conservative *analytical* LM386/LM317 load envelope for THT audio lab drafts.

This is a specification consistency gate, not a Spice model or proof of
audio fidelity, regulator thermal safety, battery or vehicle suitability.
Speaker load current MUST NOT be equated with regulator input supply current.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import pi, sqrt, isclose
from pathlib import Path
import csv
from verify_audio_psu_lm317_native import vout_pvt_endpoints

ROOT = Path(__file__).resolve().parents[2]
TABLE = ROOT / "03_Verifiche/V2.7/AUDIO_LOAD_ENVELOPE_LM386_6V.csv"

@dataclass(frozen=True)
class Envelope:
    speaker_ohms: float
    output_watts: float
    output_vrms: float
    output_irms: float
    output_ipeak_sine: float
    coupling_hz_ideal: float

def speaker_ideal(speaker_ohms: float, output_watts: float,
                  coupling_farads: float = 220e-6) -> Envelope:
    assert speaker_ohms > 0 and output_watts > 0 and coupling_farads > 0
    vrms = sqrt(speaker_ohms * output_watts)
    irms = sqrt(output_watts / speaker_ohms)
    return Envelope(speaker_ohms, output_watts, vrms, irms,
                    sqrt(2) * irms, 1/(2*pi*speaker_ohms*coupling_farads))

def theta_required_c_per_w(vin_max: float, vout_min: float,
                            combined_supply_a: float, tamb: float,
                            budget_tj: float = 125) -> float:
    """Threshold for *assumed DC constant* output; NO heatsink conclusion."""
    assert vin_max > vout_min > 0 and combined_supply_a > 0
    assert tamb < budget_tj
    return (budget_tj - tamb)/((vin_max-vout_min)*combined_supply_a)

def junction_scenario_c(vin_max: float, vout_min: float, supply_a: float,
                         ambient_c: float, theta_c_per_w: float) -> float:
    assert all(x > 0 for x in (vin_max, vout_min, supply_a, theta_c_per_w))
    assert vin_max > vout_min
    return ambient_c+(vin_max-vout_min)*supply_a*theta_c_per_w

def theoretical_supply_floor_a(load_power_w: float, supply_v: float) -> float:
    """Energy-conservation lower bound at 100% efficiency, NOT a prediction."""
    assert load_power_w >= 0 and supply_v > 0
    return load_power_w/supply_v

def run():
    scenarios=[(8,0.100),(8,0.125),(8,0.250),(4,0.100),(4,0.125)]
    results=[speaker_ideal(ohms,power) for ohms,power in scenarios]
    # Reference: TI SNAS545D §6.5; 250mW is MIN at *10% THD* for 6V/8ohm.
    # 125mW, 0.2% THD is TYP at 1kHz; 4ohm data are not guaranteed.
    assert isclose(results[0].output_vrms, sqrt(.8), rel_tol=1e-9)
    assert isclose(results[0].output_irms, sqrt(.1/8), rel_tol=1e-9)
    assert 90 < results[0].coupling_hz_ideal < 91
    assert 180 < results[3].coupling_hz_ideal < 182
    assert results[2].output_ipeak_sine > results[1].output_ipeak_sine
    assert all(r.output_ipeak_sine >= r.output_irms for r in results)
    low, nominal, high = vout_pvt_endpoints()
    assert 5.5 < low < nominal < high < 6.4
    # Conservative scenario: V_IN 10.5V max, V_OUT minimum reference estimate,
    # ambient 60C, reference junction budget 125C; theta=50C/W is ASSUMED.
    for combined_current in (.10,.20,.25,.35):
        implied_temp=junction_scenario_c(10.5, low, combined_current,60,50)
        theta_limit=theta_required_c_per_w(10.5,low,combined_current,60)
        assert isclose(60+(10.5-low)*combined_current*theta_limit,125,abs_tol=1e-9)
        if combined_current==.35: assert implied_temp>125
        if combined_current==.20: assert 100 < implied_temp < 112
    assert theta_required_c_per_w(10.5,low,.35,60)<40
    assert theoretical_supply_floor_a(.125,6)<.03
    # A floor at 100% efficiency is not the LM386 operating current.
    # Do not infer actual PSU current, amplifier package dissipation or THD.
    assert not any(x.speaker_ohms==4 and x.output_watts==.250 for x in results)

    with TABLE.open(newline="",encoding="utf-8") as fh:
        saved=list(csv.DictReader(fh))
    assert len(saved)==len(results)
    for actual,expected in zip(saved,results):
        assert isclose(float(actual["speaker_ohms"]),expected.speaker_ohms)
        assert isclose(float(actual["output_watts"]),expected.output_watts)
        for key,calc in (("speaker_vrms",expected.output_vrms),
                         ("speaker_irms",expected.output_irms),
                         ("speaker_ipeak_sine",expected.output_ipeak_sine),
                         ("ideal_coupling_fc_hz",expected.coupling_hz_ideal)):
            assert isclose(float(actual[key]),calc,abs_tol=0.0002)
    print("LM386_SPEAKER_ONLY_ANALYTICAL_SCENARIOS",
          [(x.speaker_ohms,x.output_watts,round(x.output_ipeak_sine,3))
           for x in results],flush=True)
    print("LM317_REFERENCE_THERMAL_SCENARIO_NOT_QUALIFIED",
          {"vin_max":10.5,"vout_min_reference":round(low,4),
           "ambient_C":60,"theta_assumed_C_per_W":50,
           "tj_at_0p2A_C":round(junction_scenario_c(10.5,low,.2,60,50),2),
           "max_theta_at_0p35A_C_per_W":round(
               theta_required_c_per_w(10.5,low,.35,60),2)},flush=True)
    print("PASS_LM386_LM317_ANALYTICAL_LOAD_ENVELOPE_NO_POWER_CERTIFICATION",flush=True)

if __name__=="__main__":
    run()
