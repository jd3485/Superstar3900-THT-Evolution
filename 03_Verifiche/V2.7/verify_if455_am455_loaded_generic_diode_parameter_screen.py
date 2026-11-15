#!/usr/bin/env python3
"""Native ngspice stress screening of UNKNOWN nonlinear AM detector diode params.

54 simulations: Is (0.25n/2.5n/25n) x Cjo (2p/4p/8p) x
source amplitude (0.5/2 V peak) x FRONT wiper (10/50/90 %).
These are intentionally synthetic diode parameter alternatives, NOT
Vishay 1N4148 OEM corner bounds, not certified RF sensitivity or THD.
"""
from pathlib import Path
import math
import subprocess
import tempfile
from verify_if455_am455_input_level_sweep_native import number
from verify_am455_front_lm386_loaded_ac_native import check_actual_cad

ROOT=Path(__file__).resolve().parents[2]
DECK=ROOT/"03_Verifiche/V2.7/spice/if455_am455_front_lm386_loaded_generic_diode.cir"
PARAM=".param fc=455k fa=1k depth=0.5 amp=2 wiper=0.5"
DIODE=".model DGENERIC D(Is=2.5n N=1.9 Rs=0.6 Cjo=4p Vj=0.75 Tt=4n)"
IS_VALUES=("0.25n","2.5n","25n")
CJO_VALUES=("2p","4p","8p")
DRIVES=(0.5,2.0)
WIPERS=(0.1,0.5,0.9)

def main():
    check_actual_cad()
    original=DECK.read_text(encoding="utf-8")
    assert original.count(PARAM)==1
    assert original.count(DIODE)==1
    assert "D1501L out_l envelope_l DGENERIC" in original
    assert "RVP_TOP af_l wiper_l {10000*(1-wiper)}" in original
    assert "RLM386_INPUT ampin_l 0 50k" in original
    results=[]
    with tempfile.TemporaryDirectory(prefix="tht_diode_synthetic_screen_") as td:
        base=Path(td)
        for current in IS_VALUES:
            for junction_cap in CJO_VALUES:
                replacement=DIODE.replace("Is=2.5n",f"Is={current}").replace(
                    "Cjo=4p",f"Cjo={junction_cap}")
                assert "DGENERIC" in replacement
                for drive in DRIVES:
                    for position in WIPERS:
                        param=PARAM.replace("amp=2",f"amp={drive}").replace(
                            "wiper=0.5",f"wiper={position}")
                        content=original.replace(DIODE,replacement).replace(PARAM,param)
                        assert content!=original
                        name=f"is_{current}_cjo_{junction_cap}_amp_{drive}_w_{position}"
                        source=base/(name+".cir")
                        logfile=base/(name+".log")
                        source.write_text(content,encoding="utf-8")
                        run=subprocess.run(["ngspice","-b","-o",str(logfile),str(source)],
                            cwd=base,capture_output=True,text=True,timeout=180)
                        log=logfile.read_text(encoding="utf-8",errors="replace") if logfile.exists() else ""
                        run.check_returncode()
                        assert "Error:" not in log and "fatal" not in log.lower(),(name,log[-1500:])
                        baseline=number(log,"coupled_max")-number(log,"coupled_min")
                        at_pin3=number(log,"loaded_input_max")-number(log,"loaded_input_min")
                        loaded_af=number(log,"loaded_af_max")-number(log,"loaded_af_min")
                        out_rf=number(log,"loaded_rf_peak")
                        assert all(math.isfinite(z) and z>0 for z in (baseline,at_pin3,loaded_af,out_rf)),(
                            name,baseline,at_pin3,loaded_af,out_rf)
                        assert at_pin3 < loaded_af,(name,at_pin3,loaded_af)
                        result=(current,junction_cap,drive,position,baseline,at_pin3,at_pin3/baseline)
                        results.append(result)
                        print("GENERIC_DIODE_SYNTHETIC_CORNER",{
                            "Is_A_string":current,"Cjo_F_string":junction_cap,
                            "source_peak_V":drive,"volume_fraction":position,
                            "standalone_af_pp_V":round(baseline,9),
                            "loaded_lm386_input_pp_V":round(at_pin3,9),
                            "ratio_model_only":round(at_pin3/baseline,7),
                            "diode_OEM_corner":False},flush=True)
    assert len(results)==54
    group_sensitivity=[]
    for drive in DRIVES:
        for pos in WIPERS:
            subset=[r[5] for r in results if r[2]==drive and r[3]==pos]
            assert len(subset)==9
            min_v,max_v=min(subset),max(subset)
            assert 0<min_v<=max_v
            group_sensitivity.append((drive,pos,round(min_v,9),round(max_v,9),
                                      round(max_v/min_v,5)))
    assert len(group_sensitivity)==6
    print("GENERIC_DIODE_SYNTHETIC_ENVELOPE_MIN_MAX_BY_DRIVE_WIPER",group_sensitivity,flush=True)
    print("PASS_NGSPICE_54_IF455_AM455_FRONT_LOADED_SYNTHETIC_DIODE_IS_CJO_CORNER_TRANSIENTS_NOT_OEM_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
