#!/usr/bin/env python3
"""Native ngspice step-load rail response, explicitly NOT an LM317 vendor model.

Two ideal Thevenin source + resistor + capacitor + pulse current load circuits.
Purpose: demonstrate effects of cable resistance, reject underestimated droop.
No validation of actual LM317 regulation, LM386 output power or car electrical safety.
"""
from pathlib import Path
import math
import re
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[2]
NET=ROOT/"03_Verifiche/V2.7/spice/audio_6v_lab_rail_step_behavioral.cir"
V_NOM=5.952
I_IDLE=0.020
I_STEP=0.140
R_REG_ASSUMED=0.25
R_CABLE_GOOD=0.20
R_CABLE_BAD=1.50
# Native .meas labels must be present; never treat a failure as pass.
MEASUREMENTS=("vpre_good","vload_good","vrest_good",
              "vpre_bad","vload_bad","vrest_bad",
              "vgndload_good","vgndload_bad")


def parse_measurements(output):
    result={}
    for key in MEASUREMENTS:
        regex=r"(?im)^\s*"+key+r"\s*=\s*([-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)"
        match=re.search(regex,output)
        if not match:
            raise AssertionError("Missing actual ngspice .meas "+key+": "+output[-3000:])
        result[key]=float(match.group(1))
        assert math.isfinite(result[key]),key
    return result


def main():
    raw=NET.read_text(encoding="utf-8")
    assert "NOT FOR FAB OR VEHICLE" in raw
    assert "* BEHAVIORAL PASSIVE NETWORK ONLY" in raw
    assert "C1402_GOOD psu_good 0 10u" in raw
    assert "C1402_BAD psu_bad 0 10u" in raw
    assert "RREG_GOOD reg_good psu_good 0.25" in raw
    assert "RCABLE_GOOD psu_good amp_good 0.20" in raw
    assert "RCABLE_BAD psu_bad amp_bad 1.50" in raw
    assert "RRETURN_GOOD amp_gnd_good 0 0.20" in raw
    assert "RRETURN_BAD amp_gnd_bad 0 1.50" in raw
    assert "C1206_GOOD amp_good amp_gnd_good 100u" in raw
    assert "C1206_BAD amp_bad amp_gnd_bad 100u" in raw
    assert "ILOAD_GOOD amp_good amp_gnd_good PULSE(0.020 0.140" in raw
    with tempfile.TemporaryDirectory(prefix="tht_audio_step_ngspice_") as folder:
        output_file=Path(folder)/"ngspice.log"
        process=subprocess.run(["ngspice","-b","-o",str(output_file),str(NET)],
                               cwd=ROOT, capture_output=True,text=True)
        logfile=output_file.read_text(encoding="utf-8",errors="replace") if output_file.exists() else ""
        print("NATIVE_NGSPICE_STDOUT",process.stdout[-1000:],flush=True)
        print("NATIVE_NGSPICE_STDERR",process.stderr[-1000:],flush=True)
        print("NATIVE_NGSPICE_MEASUREMENTS",logfile[-3500:],flush=True)
        process.check_returncode()
        assert not re.search(r"(?im)^\s*(?:error|fatal):",logfile),"ngspice reports error"
        vals=parse_measurements(logfile)
    for suffix,cable in (("good",R_CABLE_GOOD),("bad",R_CABLE_BAD)):
        r_total=R_REG_ASSUMED+2*cable
        expected_before=V_NOM-I_IDLE*r_total
        expected_during=V_NOM-I_STEP*r_total
        assert math.isclose(vals["vpre_"+suffix],expected_before,abs_tol=0.006),(
            suffix,"pre",vals)
        assert math.isclose(vals["vload_"+suffix],expected_during,abs_tol=0.006),(
            suffix,"step",vals)
        assert math.isclose(vals["vrest_"+suffix],expected_before,abs_tol=0.006),(
            suffix,"recovery",vals)
        drop=vals["vpre_"+suffix]-vals["vload_"+suffix]
        assert math.isclose(drop,(I_STEP-I_IDLE)*r_total,abs_tol=0.009),(
            suffix,"resistive drop",drop)
    good_drop=vals["vpre_good"]-vals["vload_good"]
    bad_drop=vals["vpre_bad"]-vals["vload_bad"]
    assert bad_drop>good_drop*4.0
    assert math.isclose(vals["vgndload_good"],I_STEP*R_CABLE_GOOD,abs_tol=.005)
    assert math.isclose(vals["vgndload_bad"],I_STEP*R_CABLE_BAD,abs_tol=.005)
    assert vals["vgndload_bad"] > vals["vgndload_good"]*4
    # This circuit cannot certify power supply; it has no semiconductor model.
    print("PASS_NGSPICE_BEHAVIORAL_AUDIO_6V_RAIL_STEP_NO_VENDOR_OR_FAB",
          {"droop_good_V":round(good_drop,4),
           "droop_high_cable_R_V":round(bad_drop,4),
           "amp_ground_shift_good_V":round(vals["vgndload_good"],4),
           "amp_ground_shift_bad_V":round(vals["vgndload_bad"],4)},flush=True)


if __name__=="__main__":
    main()
