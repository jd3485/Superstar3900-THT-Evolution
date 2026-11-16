#!/usr/bin/env python3
"""Native KiCad9 physical common-gate fault of anti-series THT P-MOS pair.

Architecture finding only.  A back-to-back pair blocks opposed body diodes
while OFF; tying both gates to one driver is NOT two independent safety cuts.
"""
from pathlib import Path
import itertools
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets,require
from verify_q806_microchip_1n4106_low_current_native import SCH
from verify_q806_dual_zener_clamp_native import N as EXPECTED

def main():
    with tempfile.TemporaryDirectory(prefix="pair_common_gate_fault_") as d:
        nets=exported_nets(SCH,Path(d)/"pair.net")
    assert len(nets)==len(EXPECTED)==8
    for name,parts in EXPECTED.items():
        require(nets,name,*parts)
        assert nets[name]==parts,(name,sorted(nets[name]))
    assert sum(map(len,nets.values()))==27
    gate=nets["COMMON_GATE_LAB"]
    source=nets["FLOATING_COMMON_SOURCE_LAB"]
    assert {("Q804","1"),("Q805","1"),("R2102","2"),("R2101","2")}<=gate
    assert {("Q804","3"),("Q805","3"),("R2101","1")}<=source
    assert {("Q806","3"),("R2102","1")}<=nets["DRIVER_SINK_LAB"]
    assert {("Q806","1"),("R2104","2")}<=nets["LAB_RETURN_ONLY"]
    assert ("Q804","2") in nets["PRIMARY_IN_DRAIN_LAB"]
    assert ("Q805","2") in nets["SECONDARY_OUT_DRAIN_LAB"]
    assert ("Q804","2") not in nets["SECONDARY_OUT_DRAIN_LAB"]
    assert ("Q805","2") not in nets["PRIMARY_IN_DRAIN_LAB"]
    # A BJT C-E short is NOT controlled by the externally supplied ENABLE
    # through R2103; the 10k collector-to-gate path still pulls both gates.
    assert ("J2103","1") in nets["ENABLE_LOGIC_5V_LAB"]
    assert ("J2103","1") not in gate
    assert ("J2103","1") not in nets["DRIVER_SINK_LAB"]
    # Synthetic boundary: BOTH gates experience exactly the same VGS
    # whether driver is nominally enabled or Q806 collector-emitter stuck
    # LOW. Do NOT interpret 'on' as guaranteed current/SOA/safety behavior.
    count=0
    dangerous_common_gate=0
    passive_off=0
    for vs,rgs,rg,enable,short_ce in itertools.product(
        (0.,8.,13.8,16.,24.,48.),
        (44650.,47000.,49350.),
        (9500.,10000.,10500.),
        (False,True),
        (False,True)
    ):
        gate_sink=enable or short_ce
        # No-Zener OPEN worst boundary, without semiconductor nonlinear I/V.
        vgs=-vs*rgs/(rgs+rg) if gate_sink else 0.0
        assert vgs==vgs # finite
        vgs_a=vgs_b=vgs
        assert vgs_a==vgs_b
        if not gate_sink:
            assert vgs_a==vgs_b==0.
            passive_off+=1
        if short_ce and not enable and vs>=13.8:
            # The series switch does not maintain independent OFF control:
            # both devices receive the same negative drive despite ENABLE0.
            assert vgs_a<0. and vgs_b<0.
            dangerous_common_gate+=1
        count+=1
    assert count==216
    assert passive_off==54
    assert dangerous_common_gate==36
    # Model deliberately does not claim actual FET conduction current.
    print("DUAL_PMOS_THT_COMMON_GATE_STUCK_DRIVER",{
      "KiCad9_pins":27,"nets":8,"mathematical_cases":count,
      "passive_driver_open_cases":passive_off,
      "disabled_but_CE_short_both_gates_driven_cases":dangerous_common_gate,
      "back_to_back_body_diodes_separate":True,
      "independent_gate_drivers_present":False,
      "independent_series_power_disconnections_qualified":False,
      "absolute_VGS_OEM_rating_stress_qualified":False,
      "model":"ideal lumped resistor divider with both Zeners OPEN, not OEM",
      "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True
    },flush=True)
    print("PASS_NATIVE_KICAD9_ANTISERIES_PMOS_COMMON_GATE_27PIN_8NET_216_NONFAB",flush=True)

if __name__=="__main__":
    main()
