#!/usr/bin/env python3
"""25C SPICE model consistency screen against Vishay 1N4148 published limits.

Reference: Vishay 1N4148 rev 1.6 (07 Nov 2024), doc 81857, pp. 1-2.
https://www.vishay.com/docs/81857/1n4148.pdf
DO-35 1N4148-TAP candidate, not an approved automotive part.
Datasheet: VF <= 1V at IF=10mA; IR <= 25nA at VR=20V at 25C;
CD <= 4pF at VR=0, f=1MHz, 50mV signal. DC diode model Cjo is NOT
itself an actual measured full CD and model parameters are NOT vendor data.
We expressly require the 8p synthetic test to be tagged OUTSIDE the OEM
zero-bias capacitance upper-bound, never a 1N4148 production corner.
"""
from __future__ import annotations
import math
from pathlib import Path
import re
import subprocess
import tempfile
from verify_if455_am455_loaded_generic_diode_parameter_screen import (
    IS_VALUES, CJO_VALUES, DIODE, DECK as TRANSIENT_DECK
)
from verify_interboard_audio_contract_native import exported_nets,require

ROOT=Path(__file__).resolve().parents[2]
DEM=ROOT/"04_KiCad/V2.7_DRAFT/AM455_ENVELOPE/AM455_ENVELOPE_THT_V2_7_DRAFT.kicad_sch"
SOURCE="https://www.vishay.com/docs/81857/1n4148.pdf"
VF10MA_MAX=1.0
IR20V_MAX_A=25e-9
CD_ZERO_MAX_F=4e-12

def numeric(log,label):
    match=re.search(r"(?im)^\s*"+re.escape(label)+
        r"\s*=\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)",log)
    assert match,("Missing ngspice .op value",label,log[-1400:])
    result=float(match.group(1))
    assert math.isfinite(result),label
    return result

def make_deck(is_string:str,cjo_string:str):
    # Two separate instances: forward current forced, reverse bias forced.
    # No rectifier power rail or real IF chain is energized by this test.
    return f"""VREV cath_rev 0 DC -20
DREV cath_rev 0 DSYN
IFORCE 0 anode_fwd DC 10m
DFWD anode_fwd 0 DSYN
.model DSYN D(Is={is_string} N=1.9 Rs=0.6 Cjo={cjo_string} Vj=0.75 Tt=4n)
.control
set noaskquit
op
print v(anode_fwd)
print vrev#branch
quit
.endc
.end
"""

def main():
    assert SOURCE.startswith("https://www.vishay.com/docs/81857/")
    raw=TRANSIENT_DECK.read_text(encoding="utf-8")
    assert raw.count(DIODE)==1
    assert set(IS_VALUES)=={"0.25n","2.5n","25n"}
    assert set(CJO_VALUES)=={"2p","4p","8p"}
    assert "D1501L out_l envelope_l DGENERIC" in raw
    assert "VISHAY_1N4148_TAP_CANDIDATE" in DEM.read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory(prefix="tht_vishay_model_screen_") as td:
        folder=Path(td)
        nets=exported_nets(DEM,folder/"demod.net")
        require(nets,"IF455_BENCH_IN",("J1501","1"),("D1501","2"))
        require(nets,"AM_RECTIFIED_ENV",("D1501","1"),("C1501","1"))
        results=[]
        for is_string in IS_VALUES:
            for cjo_string in CJO_VALUES:
                name=f"is_{is_string}_cjo_{cjo_string}"
                deck=folder/(name+".cir")
                logpath=folder/(name+".log")
                deck.write_text(make_deck(is_string,cjo_string),encoding="utf-8")
                run=subprocess.run(["ngspice","-b","-o",str(logpath),str(deck)],
                    cwd=folder,capture_output=True,text=True,timeout=90)
                log=logpath.read_text(encoding="utf-8",errors="replace") if logpath.exists() else ""
                run.check_returncode()
                assert "Error:" not in log and "fatal" not in log.lower(),(name,log[-1600:])
                vf=numeric(log,"v(anode_fwd)")
                # Bias -20V: ngspice source branch current is opposite to
                # the reverse diode current in the chosen direction.
                leakage=abs(numeric(log,"vrev#branch"))
                assert 0<vf<VF10MA_MAX,(name,vf)
                assert 0<leakage<=IR20V_MAX_A,(name,leakage)
                cjo_pf=float(cjo_string[:-1])
                stress_outside=cjo_pf*1e-12>CD_ZERO_MAX_F
                assert stress_outside==(cjo_string=="8p"),(name,stress_outside)
                results.append((name,vf,leakage,stress_outside))
                print("VISHAY_1N4148_NON_OEM_SYNTHETIC_SPICE_DC_SCREEN",{
                    "Is_string":is_string,"Cjo_string":cjo_string,
                    "VF10mA_V":round(vf,7),"IR20V_A":leakage,
                    "Cjo_exceeds_datasheet_zero_bias_CD_max":stress_outside,
                    "Cjo_is_NOT_measured_total_CD":True,
                    "vendor_model":False,"OEM_production_qualified":False},flush=True)
    assert len(results)==9
    assert sum(x[3] for x in results)==3
    print("VISHAY_1N4148_DOCUMENT_81857_REV_1P6",{
        "VF_max_at_10mA_25C_V":VF10MA_MAX,
        "IR_max_at_VR20V_25C_A":IR20V_MAX_A,
        "CD_max_at_0V_1MHz_50mV_F":CD_ZERO_MAX_F,
        "part":"1N4148-TAP_DO-35",
        "source":SOURCE,
        "OEM_forward_reverse_only_screen":True,
        "OEM_diode_model_available_here":False,
        "NO_FAB_NO_TX":True},flush=True)
    print("PASS_NGSPICE_9_VISHAY_DATASHEET_DC_MODEL_SCREEN_8PF_OUT_OF_SPEC_NOT_VENDOR_MODEL_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
