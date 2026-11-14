#!/usr/bin/env python3
"""Native 48-case IF455 source-to-ceramic-input interface topology comparison.

FOUR idealized topologies: direct resistive dummy; OEM Rg+R1=Z bench;
ideal narrowband passive L-match; ideal voltage-follower buffer.
No ceramic passband model, SBL-1+ LO-driven output model, real buffer
device/bias/noise, inductors' Q/SRF/tolerance, RF harmonic termination,
or actual PCB. Port pin mappings exported from real KiCad9 standalone CAD.
"""
from pathlib import Path
import cmath
import math
import subprocess
import tempfile

from verify_interboard_audio_contract_native import exported_nets, require
from verify_if455_two_port_source_impedance_native import TANK
from verify_mixer_if_termination_native import MIXER

ROOT=Path(__file__).resolve().parents[2]
F_IF=455000
FREQUENCIES=(445000,455000,465000)
RS=(50,500)
Z_FILTER=(1500,2000)
TOPOLOGIES=("DIRECT","OEM_TEST_SERIES_R","IDEAL_LOWPASS_L_MATCH","IDEAL_UNITY_BUFFER")
BUFFER_RIN=100000.
BUFFER_ROUT=100.

def ideal_matching_parts(rs,load):
    assert 0<rs<load
    q=math.sqrt(load/rs-1)
    w=2*math.pi*F_IF
    return (rs*q/w, q/(load*w))

def expected_transfer(freq,rs,load,topology):
    w=2*math.pi*freq
    if topology=="DIRECT":
        return complex(load/(rs+load))
    if topology=="OEM_TEST_SERIES_R":
        return complex(0.5)
    if topology=="IDEAL_UNITY_BUFFER":
        return complex(BUFFER_RIN/(BUFFER_RIN+rs)*load/(load+BUFFER_ROUT))
    assert topology=="IDEAL_LOWPASS_L_MATCH"
    inductance,capacitance=ideal_matching_parts(rs,load)
    ysh=1/load+1j*w*capacitance
    zsh=1/ysh
    return zsh/(rs+1j*w*inductance+zsh)

def make_deck(freq,rs,load,topology):
    parts=["* Hypothetical 455kHz interface, NOT OEM ceramic or SBL-1+",
           "VSIG src 0 DC 0 AC 1"]
    if topology=="DIRECT":
        parts += [f"RGEN src load {rs}",f"RLOAD load 0 {load}"]
    elif topology=="OEM_TEST_SERIES_R":
        parts += [f"RGEN src intermediate {rs}",
                  f"R1 intermediate load {load-rs}",
                  f"RLOAD load 0 {load}"]
    elif topology=="IDEAL_LOWPASS_L_MATCH":
        inductance,capacitance=ideal_matching_parts(rs,load)
        parts += [f"RGEN src intermediate {rs}",
                  f"LMATCH intermediate load {inductance:.16g}",
                  f"CMATCH load 0 {capacitance:.16g}",
                  f"RLOAD load 0 {load}"]
    else:
        assert topology=="IDEAL_UNITY_BUFFER"
        parts += [f"RGEN src input {rs}",
                  f"R_INPUT input 0 {BUFFER_RIN:.16g}",
                  "EBUFFER active 0 input 0 1",
                  f"R_OUTPUT active load {BUFFER_ROUT:.16g}",
                  f"RLOAD load 0 {load}"]
    parts += [".control","set wr_singlescale",
              f"ac lin 2 {freq} {freq+1}",
              "wrdata output.dat vr(load) vi(load)",
              "quit",".endc",".end",""]
    return "\n".join(parts)

def run_one(folder,freq,rs,load,topology):
    src=folder/"bench.cir"
    src.write_text(make_deck(freq,rs,load,topology),encoding="utf-8")
    proc=subprocess.run(["ngspice","-b","-o",str(folder/"native.log"),str(src)],
                        cwd=folder,capture_output=True,text=True)
    proc.check_returncode()
    log=(folder/"native.log").read_text(encoding="utf-8",errors="replace")
    assert "Error:" not in log and "fatal" not in log.lower(),log[-1800:]
    dat=folder/"output.dat"
    assert dat.is_file(),("missing native ngspice output",topology,rs,load,freq)
    rows=[tuple(map(float,l.split())) for l in dat.read_text().splitlines() if l.strip()]
    assert 1<=len(rows)<=2,(topology,rs,load,freq,rows)
    assert all(len(x)==3 and all(math.isfinite(v) for v in x) for x in rows)
    f,vr,vi=rows[0]
    assert abs(f-freq)<1,(f,freq)
    return complex(vr,vi)

def main():
    with tempfile.TemporaryDirectory(prefix="tht_if455_interface_") as tmp:
        root=Path(tmp)
        mixer=exported_nets(MIXER,root/"mixer.net")
        tank=exported_nets(TANK,root/"tank.net")
        require(mixer,"IF455_MIXER_IF",("MX1701","3"),("MX1701","4"),("J1703","1"))
        require(mixer,"IF_BENCH_GND",("MX1701","2"),("J1703","2"))
        require(tank,"IF455_SOURCE",("J1601","1"),("C1601","1"))
        require(tank,"IF_BENCH_GND",("J1601","2"),("J1602","2"))
        assert mixer["IF455_MIXER_IF"]=={("MX1701","3"),("MX1701","4"),("J1703","1")}
        assert tank["IF455_SOURCE"]=={("J1601","1"),("C1601","1")}
        count=0
        for rs in RS:
            for load in Z_FILTER:
                for topology in TOPOLOGIES:
                    values={}
                    for frequency in FREQUENCIES:
                        folder=root/f"rs{rs}_z{load}_{topology}_{frequency}"
                        folder.mkdir()
                        observed=run_one(folder,frequency,rs,load,topology)
                        expected=expected_transfer(frequency,rs,load,topology)
                        assert abs(observed-expected)<2e-6*max(1,abs(expected)),(
                            rs,load,topology,frequency,observed,expected)
                        assert math.isfinite(abs(observed))
                        values[frequency]=abs(observed)
                        count+=1
                    center=values[F_IF]
                    offsets={f:round(20*math.log10(center/values[f]),6)
                             for f in (445000,465000)}
                    detail={"hypothetical_mixer_R_ohm":rs,
                            "ceramic_input_resistive_dummy_ohm":load,
                            "interface":topology,
                            "magnitude_Vload_per_Vsource_at_455":round(center,9),
                            "amplitude_dB_at_455":round(20*math.log10(center),6),
                            "relative_rejection_minus10k_dB":offsets[445000],
                            "relative_rejection_plus10k_dB":offsets[465000],
                            "actual_ceramic_transfer_simulated":False,
                            "actual_buffer_model_simulated":False,
                            "actual_mixer_model_simulated":False}
                    if topology=="IDEAL_LOWPASS_L_MATCH":
                        l,c=ideal_matching_parts(rs,load)
                        w=2*math.pi*F_IF
                        zin=1j*w*l+1/(1/load+1j*w*c)
                        assert abs(zin-rs)<1e-5,(rs,load,zin)
                        detail["ideal_L_H"]=round(l,12)
                        detail["ideal_C_F"]=round(c,15)
                        detail["ideal_input_Z_at_455_real_ohm"]=round(zin.real,6)
                        detail["ideal_input_Z_at_455_imag_ohm"]=round(zin.imag,6)
                    if topology=="OEM_TEST_SERIES_R":
                        assert abs(center-0.5)<2e-6
                        detail["test_only_R1_ohm"]=load-rs
                    print("IF455_THREE_INTERFACE_FAMILIES_NATIVE",detail,flush=True)
        assert count==len(RS)*len(Z_FILTER)*len(TOPOLOGIES)*len(FREQUENCIES)==48
    print("PASS_NATIVE_KICAD9_IF455_48_NGSPICE_RESISTIVE_LMATCH_BUFFER_IDEAL_COMPARISONS_NO_VENDOR_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
