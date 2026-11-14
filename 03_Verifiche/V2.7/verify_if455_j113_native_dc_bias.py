#!/usr/bin/env python3
"""DC bias evidence for existing native KiCad9 onsemi J113 THT candidate.

18 actual ngspice transient-to-DC samples: generic NJF VTO x Idss x
source resistors 680/1000/2200 ohm. All actual CAD values unchanged.
Not a vendor J113 model; no device noise, nonlinearity, temperature,
RF swing, AM sensitivity or fabrication qualification.
"""
from pathlib import Path
import math
import subprocess
import tempfile

from verify_interboard_audio_contract_native import exported_nets, require
from verify_if455_two_port_source_impedance_native import TANK
from verify_if455_j113_ceramic_load_native import SCH, spice_deck, VTO, IDSS

RS_VALUES=(680,1000,2200)
VCC=6.0
F=455000

def dc_deck(vto,idss,rs):
    original=spice_deck(vto,idss,2000)
    old="R1802 source_j 0 2.2k"
    assert original.count(old)==1
    original=original.replace(old,f"R1802 source_j 0 {rs}")
    control_start=original.index(".control")
    # The JFET is biased at true DC: AC-stimulus is zero at DC, coupling
    # capacitors block the filter dummy, and the source resistor sets Id.
    return original[:control_start]+"\n".join([
        ".control","set wr_singlescale",
        "tran 1u 5u",
        "wrdata bias.dat v(gate) v(source_j) v(vcc) i(VLAB)",
        "quit",".endc",".end",""
    ])

def dc_case(folder,vto,idss,rs):
    circuit=folder/"j113_dc.cir"
    circuit.write_text(dc_deck(vto,idss,rs),encoding="utf-8")
    process=subprocess.run(["ngspice","-b","-o",str(folder/"ngspice.log"),
                            str(circuit)],cwd=folder,capture_output=True,text=True)
    process.check_returncode()
    log=(folder/"ngspice.log").read_text(encoding="utf-8",errors="replace")
    assert "Error:" not in log and "fatal" not in log.lower(),log[-2000:]
    out=folder/"bias.dat"
    assert out.is_file(),(vto,idss,rs)
    rows=[tuple(map(float,line.split())) for line in out.read_text().splitlines()
          if line.strip()]
    assert len(rows)>=2,(vto,idss,rs,len(rows))
    assert all(len(x)==5 and all(math.isfinite(t) for t in x) for x in rows)
    time,gate,source,rail,supply=rows[-1]
    assert abs(time-5e-6)<2e-7,(vto,idss,rs,time)
    assert abs(gate)<1e-5,(vto,idss,rs,gate)
    assert abs(rail-VCC)<1e-5,(vto,idss,rs,rail)
    # Independent DC KCL check: the rail supplies only JFET drain,
    # coupling capacitors isolate the 2k load. ngspice current through
    # positive VLAB voltage source is negative when it supplies the FET.
    source_i=source/rs
    supply_i=-supply
    assert 0<source<rail,(vto,idss,rs,source,rail)
    assert supply_i>0,(vto,idss,rs,supply)
    assert abs(source_i-supply_i)<max(2e-8,0.01*source_i),(
        "JFET DC current balance violated",vto,idss,rs,source_i,supply_i)
    vgs=gate-source
    vds=rail-source
    assert vgs<0 and vds>0,(vto,idss,rs,vgs,vds)
    return {"source_V":source,"gate_V":gate,"drain_V":rail,
            "gate_source_V":vgs,"drain_source_V":vds,
            "source_R_ohm":rs,"source_current_mA":source_i*1000,
            "supply_current_mA":supply_i*1000,
            "KCL_relative_error":abs(source_i-supply_i)/source_i}

def main():
    sch=SCH.read_text(encoding="utf-8")
    assert "ONSEMI_J113_TO92_1D_2S_3G_ONLY_CANDIDATE" in sch
    assert "2k2_SOURCE_SELF_BIAS_DRAFT" in sch
    with tempfile.TemporaryDirectory(prefix="tht_j113_dc_bias_") as tmp:
        root=Path(tmp)
        pins=exported_nets(SCH,root/"j113.net")
        ifnets=exported_nets(TANK,root/"tank.net")
        require(pins,"JFET_GATE",("Q1801","3"),("C1801","2"),("R1801","1"))
        require(pins,"JFET_SOURCE",("Q1801","2"),("R1802","1"),("C1802","1"))
        require(pins,"VLAB6_JFET_ONLY",("Q1801","1"),("J1803","1"))
        require(pins,"JFET_AC_OUT",("C1802","2"),("J1802","1"),("R1803","1"))
        require(ifnets,"IF455_SOURCE",("J1601","1"),("C1601","1"))
        results={}
        for rs in RS_VALUES:
            for vto in VTO:
                for idss in IDSS:
                    job=root/f"r{rs}_v{abs(vto)}_idss{idss}"
                    job.mkdir()
                    measured=dc_case(job,vto,idss,rs)
                    results[rs,vto,idss]=measured
                    print("J113_NATIVE_GENERIC_DC_BIAS",{
                        "trial_source_R_ohm":rs,"generic_VTO_V":vto,
                        "hypothetical_Idss_A":idss,
                        "Vsource":round(measured["source_V"],9),
                        "Vgs":round(measured["gate_source_V"],9),
                        "Vds":round(measured["drain_source_V"],9),
                        "supply_current_mA":round(measured["supply_current_mA"],9),
                        "current_KCL_relative_error":round(measured["KCL_relative_error"],8),
                        "actual_OEM_J113_model":False,
                        "temperature_noise_linearity_verified":False},flush=True)
        assert len(results)==18
        for vto in VTO:
            for idss in IDSS:
                original=results[2200,vto,idss]
                for rs in (680,1000):
                    candidate=results[rs,vto,idss]
                    # Changing Rsource changes operating point, even if
                    # previous AC comparison was worse than 2k2.
                    delta=candidate["source_current_mA"]-original["source_current_mA"]
                    assert math.isfinite(delta)
                    print("J113_GENERIC_DC_ALTERNATIVE_VS_2200",{
                        "generic_VTO_V":vto,"hypothetical_Idss_A":idss,
                        "candidate_source_ohm":rs,
                        "delta_supply_current_mA":round(delta,9),
                        "actual_device_operating_limits_checked":False},flush=True)
    print("PASS_NATIVE_KICAD9_J113_18_GENERIC_DC_BIAS_AND_INDEPENDENT_R_SOURCE_KCL_NO_OEM_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
