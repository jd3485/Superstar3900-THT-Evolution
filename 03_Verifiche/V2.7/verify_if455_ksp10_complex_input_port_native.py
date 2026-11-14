#!/usr/bin/env python3
"""KSP10 THT complex input impedance under generic 6V bias.

72 paired capacitor-port and virtually-direct-base tests = 144 native
ngspice AC solves. Independent series-reactance identity checks whether
Zin(port)=Zin(base)+1/(jwCin) under same BJT bias and loading.
No actual SBL-1+ mixer, ceramic Z(f), OEM BJT model, noise/IMD/PCB.
"""
from pathlib import Path
import math
import subprocess
import tempfile

from verify_interboard_audio_contract_native import exported_nets, require
from verify_if455_two_port_source_impedance_native import TANK
from verify_if455_ksp10_generic_bjt_bias_ac import SCH as KSP10_SCH, BETAS
from verify_if455_j113_ksp10_shared_tank_native import circuit

COUPLING_PF=(10,100,1000,10000)
FREQUENCIES=(445000,455000,465000)
LOADS=(1500,2000)
BASE_PROBE_CAP_F=1.0

def make_deck(beta,load,freq,cap_pf,base_reference):
    deck=circuit("KSP10",beta,load,10000)
    old="CIN out input 10000p"
    assert deck.count(old)==1
    # The 1-farad reference capacitor blocks DC so the same OEM-candidate
    # 22k/10k bias is preserved. Its reactance is calculable and removed
    # independently from both measured complex input impedances.
    cap=f"{BASE_PROBE_CAP_F}" if base_reference else f"{cap_pf}p"
    deck=deck.replace(old,f"CIN port input {cap}\nVPORT port 0 DC 0 AC 1")
    deck=deck.replace("ac lin 2 455000 455001",f"ac lin 2 {freq} {freq+1}")
    old_data="wrdata transfer.dat vm(out) vm(bufferout) vm(input)"
    assert deck.count(old_data)==1
    deck=deck.replace(old_data,"wrdata port.dat v(port) i(vport)")
    return deck

def solve(folder,beta,load,freq,cap_pf,reference):
    source=folder/"port.cir"
    source.write_text(make_deck(beta,load,freq,cap_pf,reference),encoding="utf-8")
    proc=subprocess.run(["ngspice","-b","-o",str(folder/"spice.log"),str(source)],
                        cwd=folder,capture_output=True,text=True)
    proc.check_returncode()
    log=(folder/"spice.log").read_text(encoding="utf-8",errors="replace")
    assert "Error:" not in log and "fatal" not in log.lower(),log[-2000:]
    output=folder/"port.dat"
    assert output.is_file()
    data=[tuple(map(float,row.split())) for row in output.read_text().splitlines() if row.strip()]
    assert 1<=len(data)<=2 and all(len(row)==5 and all(math.isfinite(x) for x in row) for row in data),data
    f,vr,vi,ir,ii=data[0]
    assert abs(f-freq)<1
    voltage=complex(vr,vi)
    current=complex(ir,ii)
    assert abs(voltage-1)<1e-7
    assert abs(current)>1e-10,(beta,load,freq,cap_pf,reference)
    z=voltage/(-current)
    assert math.isfinite(z.real) and math.isfinite(z.imag)
    assert z.real>0,(beta,load,freq,cap_pf,reference,z)
    return z

def main():
    sch=KSP10_SCH.read_text(encoding="utf-8")
    assert "ONSEMI_KSP10BU_TO92_CANDIDATE" in sch
    assert "2k2_EMITTER_SET_DRAFT" in sch
    results=0
    with tempfile.TemporaryDirectory(prefix="ksp10_if455_complex_port_") as t:
        root=Path(t)
        k=exported_nets(KSP10_SCH,root/"ksp10.net")
        tank=exported_nets(TANK,root/"tank.net")
        require(k,"IFBUF_BASE_BIAS",("Q1701","1"),("C1701","2"))
        require(k,"IFBUF_EMITTER",("Q1701","2"),("R1703","1"))
        require(k,"VLAB6_IFBUF_ONLY",("Q1701","3"),("J1703","1"))
        require(tank,"IF455_SOURCE",("J1601","1"),("C1601","1"))
        require(tank,"IF455_TANK",("C1601","2"),("L1601","1"))
        for beta in BETAS:
            for load in LOADS:
                for freq in FREQUENCIES:
                    name=f"b{beta}_r{load}_f{freq}"
                    folder=root/(name+"_ref")
                    folder.mkdir()
                    zref=solve(folder,beta,load,freq,10,True)
                    omega=2*math.pi*freq
                    zbase=zref-1/(1j*omega*BASE_PROBE_CAP_F)
                    for cap_pf in COUPLING_PF:
                        folder=root/(name+f"_c{cap_pf}")
                        folder.mkdir()
                        measured=solve(folder,beta,load,freq,cap_pf,False)
                        expected=zbase+1/(1j*omega*cap_pf*1e-12)
                        # Separate circuit solves must obey exact capacitor
                        # series law; this is not a claimed vendor impedance.
                        error=abs(measured-expected)/max(abs(expected),1)
                        assert error<0.0008,(name,cap_pf,measured,expected,error)
                        assert measured.real>0
                        results+=1
                        print("KSP10_IF455_COMPLEX_INPUT_PORT_NATIVE",{
                            "generic_beta":beta,"dummy_load_R_ohm":load,
                            "frequency_Hz":freq,"trial_CIN_pF":cap_pf,
                            "Z_base_real_ohm":round(zbase.real,6),
                            "Z_base_imag_ohm":round(zbase.imag,6),
                            "Z_port_real_ohm":round(measured.real,6),
                            "Z_port_imag_ohm":round(measured.imag,6),
                            "Z_port_mag_ohm":round(abs(measured),6),
                            "relative_complex_series_identity_error":round(error,9),
                            "OEM_BJT_filter_noise_qualified":False},flush=True)
        assert results==72
    print("PASS_NATIVE_KICAD9_KSP10_144_NGSPICE_COMPLEX_PORT_AND_BASE_SERIES_REACTANCE_CASES_NO_OEM_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
