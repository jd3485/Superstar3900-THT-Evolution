#!/usr/bin/env python3
"""Real ngspice laboratory counterexample/screen: TWO idealized series current servos.

NOT vendor-validated and NOT a safety design. Current sensing at both BJT
emitters differs from collector/meter current; no startup/transient, cable,
ESD, shared rail, reference, opamp, or double fault safety qualification.
"""
import math
import re
import subprocess
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
CIR=Path(__file__).with_name("SMETER_DUAL_SERIES_GUARD_BENCH_V2_7.cir")


def simulate(rcoil=2000, vdd=5, vmain=0.4, vguard=0.45, short_main=False, short_guard=False):
    if not all(math.isfinite(v) for v in (rcoil,vdd,vmain,vguard)):
        raise ValueError("nonfinite bench parameter")
    if rcoil <= 0 or vdd < 0 or vmain < 0 or vguard < 0:
        raise ValueError("invalid bench parameter")
    s=CIR.read_text(encoding="utf-8")
    for required in (
        "QMAIN METER_LOW BASE_MAIN SENSE_MAIN QGEN",
        "QGUARD GUARD_COLL BASE_GUARD SENSE_GUARD QGEN",
        "RS_MAIN SENSE_MAIN GUARD_COLL 10000",
        "RS_GUARD SENSE_GUARD 0 10000",
        "BMAIN DRIVE_MAIN 0",
        "BGUARD DRIVE_GUARD 0",
        ".model QGEN NPN",
    ):
        assert required in s,required
    for old,new in (
        ("VDD VDD 0 5\n",f"VDD VDD 0 {vdd}\n"),
        ("VSETMAIN CMD_MAIN 0 0.4\n",f"VSETMAIN CMD_MAIN 0 {vmain}\n"),
        ("VSETGUARD CMD_GUARD 0 0.45\n",f"VSETGUARD CMD_GUARD 0 {vguard}\n"),
        ("RCOIL VDD METER_LOW 2000\n",f"RCOIL VDD METER_LOW {rcoil}\n"),
    ):
        assert old in s,old
        s=s.replace(old,new)
    fault=""
    if short_main:
        fault+="RMAIN_CE_FAULT METER_LOW SENSE_MAIN 0.001\n"
    if short_guard:
        fault+="RGUARD_CE_FAULT GUARD_COLL SENSE_GUARD 0.001\n"
    assert s.count(".op\n.end\n")==1
    s=s.replace(".op\n.end\n",fault+
        ".control\nset noaskquit\nop\nlet meter_ua = -i(vdd)*1e6\n"
        "print meter_ua\nquit\n.endc\n.end\n")
    with tempfile.TemporaryDirectory(prefix="tht_smeter_dual_") as temp:
        p=Path(temp)/"dual.cir"
        p.write_text(s,encoding="utf-8")
        cp=subprocess.run(["ngspice","-b",str(p)],cwd=ROOT,capture_output=True,text=True,timeout=30)
    out=cp.stdout+"\n"+cp.stderr
    assert cp.returncode==0,out[-3500:]
    m=re.search(r"meter_ua\s*=\s*([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)",out,re.I)
    assert m,("ngspice operating point not printed",out[-2500:])
    return float(m.group(1))


def main():
    normal=simulate()
    main_ce=simulate(short_main=True)
    guard_ce=simulate(short_guard=True)
    two_ce=simulate(short_main=True,short_guard=True)
    two_ce_20k=simulate(rcoil=20000,short_main=True,short_guard=True)
    top_ce_20k=simulate(rcoil=20000,short_main=True)
    top_ce_500=simulate(rcoil=500,short_main=True)
    off=simulate(vmain=0,vguard=0)
    off_main_fault=simulate(vmain=0,vguard=0,short_main=True)
    off_guard_fault=simulate(vmain=0,vguard=0,short_guard=True)
    vdd0=simulate(vdd=0,short_main=True)
    # Only behavioral model checks. Not a real-world fail-closed guarantee.
    assert 35 < normal < 43,normal
    assert 40 < main_ce < 50,main_ce
    assert 35 < guard_ce < 44,guard_ce
    assert 40 < top_ce_20k < 50,top_ce_20k
    assert 40 < top_ce_500 < 50,top_ce_500
    assert two_ce > 4*50,two_ce
    assert 110 < two_ce_20k < 130,two_ce_20k
    assert abs(off) < .5 and abs(off_main_fault) < .5 and abs(off_guard_fault) < .5
    assert abs(vdd0) < .5
    # Independent two-fault resistor-network cross-check.
    assert math.isclose(two_ce, 5/(2000+20000)*1e6, rel_tol=.03)
    assert math.isclose(two_ce_20k, 5/(20000+20000)*1e6, rel_tol=.03)
    print("SMETER_DUAL_SERIES_GUARD_NGSPICE_BEHAVIORAL_ONLY",{
        "normal_uA":normal,
        "QMAIN_CE_short_uA":main_ce,
        "QGUARD_CE_short_uA":guard_ce,
        "both_CE_short_2k_uA":two_ce,
        "both_CE_short_20k_uA":two_ce_20k,
        "QMAIN_CE_short_20k_uA":top_ce_20k,
        "QMAIN_CE_short_500ohm_uA":top_ce_500,
        "both_commands_off_uA":off,
        "off_command_main_CE_short_uA":off_main_fault,
        "off_command_guard_CE_short_uA":off_guard_fault,
        "lab_supply_off_main_short_uA":vdd0,
        "guard_current_is_OEM_FSD_qualified":False,
        "two_single_short_cases_tested":True,
        "dual_short_fail_closed":False,
        "shared_faults_ESD_transient_and_BOM_qualified":False,
        "KiCad_schematic_or_PCB_exists_for_dual_stage":False,
        "NO_FAB_NO_TX":True,
    },flush=True)


if __name__=="__main__":
    main()
