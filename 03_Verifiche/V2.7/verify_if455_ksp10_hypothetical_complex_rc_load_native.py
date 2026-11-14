#!/usr/bin/env python3
"""Explore *hypothetical* parallel R/C ceramic input loads on IF455/KSP10.

72 real ngspice AC solves; no OEM impedance, filter model or RX qualification.
"""
import cmath
import math
from pathlib import Path
import subprocess
import tempfile

from verify_interboard_audio_contract_native import exported_nets, require
from verify_if455_two_port_source_impedance_native import TANK
from verify_if455_ksp10_generic_bjt_bias_ac import SCH as KSP10_SCH, BETAS
from verify_if455_j113_ksp10_shared_tank_native import circuit

LOADS_OHM=(1500,2000)
SHUNT_PF=(0,100,330,1000)
FREQUENCIES_HZ=(445000,455000,465000)
INPUT_COUPLING_PF=10000
COUNT=len(BETAS)*len(LOADS_OHM)*len(SHUNT_PF)*len(FREQUENCIES_HZ)

def deck_for(beta, load, shunt_pf, frequency):
    text=circuit("KSP10",beta,load,INPUT_COUPLING_PF)
    original=f"R_DUMMY bufferout 0 {load}"
    assert text.count(original)==1
    # This is a passive RC *surrogate*, not a ceramic equivalent circuit.
    replacement=original+(f"\nC_FILTER_SURROGATE bufferout 0 {shunt_pf}p"
                          if shunt_pf else "")
    text=text.replace(original,replacement)
    assert text.count("ac lin 2 455000 455001")==1
    text=text.replace("ac lin 2 455000 455001",f"ac lin 2 {frequency} {frequency+1}")
    assert text.count("wrdata transfer.dat vm(out) vm(bufferout) vm(input)")==1
    text=text.replace("wrdata transfer.dat vm(out) vm(bufferout) vm(input)",
                      "wrdata transfer.dat v(tank) v(out) v(bufferout)")
    return text

def solve(folder,beta,load,shunt_pf,frequency):
    f=folder/"study.cir"
    f.write_text(deck_for(beta,load,shunt_pf,frequency),encoding="utf-8")
    proc=subprocess.run(["ngspice","-b","-o",str(folder/"spice.log"),str(f)],
                        cwd=folder,capture_output=True,text=True)
    proc.check_returncode()
    log=(folder/"spice.log").read_text(encoding="utf-8",errors="replace")
    assert "Error:" not in log and "fatal" not in log.lower(),log[-2000:]
    rows=[tuple(map(float,line.split())) for line in
          (folder/"transfer.dat").read_text().splitlines() if line.strip()]
    assert 1<=len(rows)<=2 and all(len(row)==7 and all(math.isfinite(x) for x in row) for row in rows),rows
    freq,tr,ti,orr,oi,br,bi=rows[0]
    assert abs(freq-frequency)<1
    tank,output,buffer=complex(tr,ti),complex(orr,oi),complex(br,bi)
    assert all(abs(x)>1e-12 for x in (tank,output,buffer))
    return tank,output,buffer

def main():
    k=KSP10_SCH.read_text(encoding="utf-8")
    assert "ONSEMI_KSP10BU_TO92_CANDIDATE" in k
    assert "2k2_EMITTER_SET_DRAFT" in k
    results={}
    with tempfile.TemporaryDirectory(prefix="if455_rc_load_") as tmp:
        root=Path(tmp)
        kn=exported_nets(KSP10_SCH,root/"ksp10.net")
        tn=exported_nets(TANK,root/"tank.net")
        require(kn,"IFBUF_BASE_BIAS",("Q1701","1"),("C1701","2"))
        require(kn,"IFBUF_EMITTER",("Q1701","2"),("R1703","1"))
        require(tn,"IF455_SOURCE",("J1601","1"),("C1601","1"))
        require(tn,"IF455_TANK",("C1601","2"),("L1601","1"))
        for beta in BETAS:
            for load in LOADS_OHM:
                for shunt in SHUNT_PF:
                    for freq in FREQUENCIES_HZ:
                        folder=root/f"b{beta}_r{load}_c{shunt}_f{freq}"
                        folder.mkdir()
                        tank,port,buffer=solve(folder,beta,load,shunt,freq)
                        z=complex(load,0) if shunt==0 else 1/(1/load+1j*2*math.pi*freq*shunt*1e-12)
                        assert z.real>0 and z.imag<=0
                        results[beta,load,shunt,freq]=(tank,port,buffer)
                        print("IF455_KSP10_HYPOTHETICAL_RC_LOAD_NATIVE",{
                            "generic_beta":beta,"dummy_resistance_ohm":load,
                            "dummy_shunt_capacitance_pF":shunt,"frequency_Hz":freq,
                            "dummy_Z_real_ohm":round(z.real,6),
                            "dummy_Z_imag_ohm":round(z.imag,6),
                            "tank_mag_VperV":round(abs(tank),9),
                            "buffer_mag_VperV":round(abs(buffer),9),
                            "tank_to_buffer_phase_deg":round(math.degrees(cmath.phase(buffer/tank)),6),
                            "OEM_ceramic_or_noise_qualified":False},flush=True)
        assert len(results)==COUNT,(len(results),COUNT)
        # Every nonzero shunt must produce an actual complex output change,
        # while the tank remains the same circuit; do not rank parts by this.
        for beta in BETAS:
            for load in LOADS_OHM:
                for freq in FREQUENCIES_HZ:
                    reference=results[beta,load,0,freq]
                    for shunt in SHUNT_PF[1:]:
                        trial=results[beta,load,shunt,freq]
                        relative=abs(trial[2]/reference[2])
                        assert math.isfinite(relative) and abs(relative-1)>1e-5,(
                            beta,load,shunt,freq,relative)
                        print("IF455_KSP10_RC_TO_RESISTIVE_DUMMY_RATIO",{
                            "beta":beta,"resistance_ohm":load,"shunt_pF":shunt,
                            "frequency_Hz":freq,"buffer_ratio":round(relative,9),
                            "real_filter_model":False},flush=True)
    print("PASS_NATIVE_KICAD9_IF455_KSP10_72_HYPOTHETICAL_COMPLEX_RC_LOAD_NGSPICE_NO_OEM_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
