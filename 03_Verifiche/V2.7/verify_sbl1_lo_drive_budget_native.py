#!/usr/bin/env python3
"""SBL-1+ LO port engineering budget + native KiCad9 V2.6 VCO connector contract.

This is a sinusoidal, resistive 50-ohm REFERENCE LOAD feasibility envelope,
not an OEM VCO measurement, an RF simulation, or proof of +7 dBm at the mixer.
Never connect CMOS square-wave output directly to the SBL-1+ on this basis.
NO FAB / NO TX / NO BATTERY / NO VEHICLE.
"""
from __future__ import annotations
from pathlib import Path
import math
import tempfile
from verify_interboard_audio_contract_native import exported_nets, require

ROOT=Path(__file__).resolve().parents[2]
VCO=ROOT/"04_KiCad/V2.6/VCO_RX_AND_LOBUF_V2.6.kicad_sch"
MIXER=ROOT/"04_KiCad/V2.7_DRAFT/MIXER_SBL1_CANDIDATE/MIXER_SBL1_BENCH_THT_V2_7_DRAFT.kicad_sch"
RLOAD=50.0
TARGET_DBM=7.0
SOURCE_RS_OHMS=(0.0,10.0,25.0,50.0,100.0,200.0)
RF_BENCH_HZ=27_000_000.0
IF_HZ=455_000.0

def required_open_circuit_vpp(rsrc:float, target_dbm:float=TARGET_DBM)->float:
    assert rsrc>=0
    watts=1e-3*10**(target_dbm/10)
    vload_rms=math.sqrt(watts*RLOAD)
    # Source Thevenin sinus, rms->peak-to-peak, voltage division.
    return 2*math.sqrt(2)*vload_rms*(1+rsrc/RLOAD)

def delivered_dbm(vsrc_pp:float, rsrc:float)->float:
    assert vsrc_pp>0 and rsrc>=0
    vrms=vsrc_pp/(2*math.sqrt(2))*RLOAD/(RLOAD+rsrc)
    return 10*math.log10((vrms*vrms/RLOAD)/1e-3)

def find_connector(nets,ref,signal_name):
    # Require signal and GND on an actual two-pin KiCad connector.
    require(nets,signal_name,(ref,"1"))
    require(nets,"GND",(ref,"2"))

def main():
    assert VCO.is_file() and MIXER.is_file()
    with tempfile.TemporaryDirectory(prefix="tht_sbl1_lo_native_") as td:
        nets=exported_nets(VCO,Path(td)/"vco.net")
        mx=exported_nets(MIXER,Path(td)/"mixer.net")
    find_connector(nets,"J523","LO1_ANALOG_OUT")
    find_connector(nets,"J522","LO1_CMOS_BUFFERED")
    require(mx,"LO_27MHZ_OFFSET_PENDING",("MX1701","8"),("J1702","1"))
    require(mx,"IF_BENCH_GND",("MX1701","2"),("MX1701","5"),
            ("MX1701","6"),("MX1701","7"),("J1702","2"))
    assert ("J522","1") not in nets["LO1_ANALOG_OUT"],"Analog/CMOS LO shorted"
    assert ("J523","1") not in nets["LO1_CMOS_BUFFERED"],"CMOS/analog LO shorted"
    # A connector naming contract != a physically qualified 50-ohm output.
    watts=1e-3*10**(TARGET_DBM/10)
    vrms=math.sqrt(watts*RLOAD)
    assert abs(watts-.00501187233627)<1e-12
    assert abs(vrms-.500593)-0.0<0.00001
    for rs in SOURCE_RS_OHMS:
        vpp=required_open_circuit_vpp(rs)
        assert abs(delivered_dbm(vpp,rs)-TARGET_DBM)<1e-10
        print(f"LO_50OHM_THEVENIN_REFERENCE Rs={rs:g}ohm target={TARGET_DBM:g}dBm "
              f"required_source_open_circuit_sine={vpp:.6f}Vpp",flush=True)
    assert abs(required_open_circuit_vpp(0.0)-1.415893)<0.00001
    assert abs(required_open_circuit_vpp(50.0)-2.831785)<0.00001
    # Two possible injection plans for a 27 MHz reference channel.
    assert RF_BENCH_HZ-IF_HZ==26_545_000.0
    assert RF_BENCH_HZ+IF_HZ==27_455_000.0
    print("LO_PLAN_CANDIDATES_HZ",(RF_BENCH_HZ-IF_HZ,RF_BENCH_HZ+IF_HZ),
          "NO_IMAGE_REJECTION_OR_VCO_TUNING_VERIFIED",flush=True)
    print("NATIVE_VCO_LO_CONNECTOR_REFERENCES",sorted(nets["LO1_ANALOG_OUT"]),
          sorted(nets["LO1_CMOS_BUFFERED"]),flush=True)
    print("PASS_NATIVE_KICAD9_VCO_TO_MIXER_LO_PORT_SEPARATE_7DBM_THEVENIN_ENVELOPE_NOT_A_VCO_OUTPUT_MEASUREMENT_NO_FAB_NO_TX",flush=True)

if __name__=="__main__": main()
