#!/usr/bin/env python3
"""KSP10 input coupling tradeoff, native KiCad9 and 48 ngspice cases.

Using original PR156 common IF455 tank/source/deck, only temporary CIN
changes. No manufacturer BJT or ceramic input Z(f) model, noise,
linearity, PCB or hardware release. Eight capacitances, three generic
beta corners and two resistor-only loads.
"""
from pathlib import Path
import math
import subprocess
import tempfile

from verify_interboard_audio_contract_native import exported_nets,require
from verify_if455_two_port_source_impedance_native import TANK
from verify_if455_ksp10_generic_bjt_bias_ac import SCH as KSP10_SCH,BETAS
from verify_if455_j113_ksp10_shared_tank_native import circuit

VALUES_PF=(10,22,47,100,220,470,1000,10000)
LOADS=(1500,2000)
CENTER=455000

def run_case(directory,beta,load,cin):
    # Reuse fully specified, previously CI-verified shared tank and KSP10.
    original=circuit("KSP10",beta,load,10)
    old="CIN out input 10p"
    assert original.count(old)==1
    net=original.replace(old,f"CIN out input {cin}p")
    assert net.count("CIN out input ")==1
    path=directory/"if455.cir"
    path.write_text(net,encoding="utf-8")
    p=subprocess.run(["ngspice","-b","-o",str(directory/"native.log"),str(path)],
                     cwd=directory,capture_output=True,text=True)
    p.check_returncode()
    log=(directory/"native.log").read_text(encoding="utf-8",errors="replace")
    assert "Error:" not in log and "fatal" not in log.lower(),log[-1600:]
    out=directory/"transfer.dat"
    assert out.is_file(),(beta,load,cin)
    rows=[tuple(map(float,x.split())) for x in out.read_text().splitlines() if x.strip()]
    assert 1<=len(rows)<=2,(beta,load,cin,rows)
    assert all(len(row)==4 and all(math.isfinite(v) for v in row) for row in rows)
    freq,tank,buffer,base=rows[0]
    assert abs(freq-CENTER)<1
    assert 0<tank<3 and 0<buffer<5 and 0<base<5,(beta,load,cin,rows)
    return tank,buffer,base

def main():
    sch=KSP10_SCH.read_text(encoding="utf-8")
    assert "ONSEMI_KSP10BU_TO92_CANDIDATE" in sch
    assert "2k2_EMITTER_SET_DRAFT" in sch
    assert "10n" in sch, "Original KSP10 physical coupling not found"
    values={}
    with tempfile.TemporaryDirectory(prefix="ksp10_if455_cin_tradeoff_") as t:
        root=Path(t)
        b=exported_nets(KSP10_SCH,root/"ksp10.net")
        tank=exported_nets(TANK,root/"if455.net")
        require(b,"IFBUF_BASE_BIAS",("Q1701","1"),("C1701","2"))
        require(b,"IFBUF_EMITTER",("Q1701","2"),("R1703","1"))
        require(b,"VLAB6_IFBUF_ONLY",("Q1701","3"),("J1703","1"))
        require(tank,"IF455_SOURCE",("J1601","1"),("C1601","1"))
        require(tank,"IF455_TANK",("C1601","2"),("L1601","1"))
        for beta in BETAS:
            for load in LOADS:
                for cin in VALUES_PF:
                    folder=root/f"b{beta}_z{load}_cin{cin}"
                    folder.mkdir()
                    tx=run_case(folder,beta,load,cin)
                    values[beta,load,cin]=tx
                    print("IF455_KSP10_CIN_TRADEOFF_NATIVE",{
                        "generic_BJT_beta":beta,"dummy_load_ohm":load,
                        "SPICE_only_input_coupling_pF":cin,
                        "tank_out_VperV":round(tx[0],9),
                        "buffer_out_VperV":round(tx[1],9),
                        "base_input_VperV":round(tx[2],9),
                        "manufacturer_model":False},flush=True)
        assert len(values)==48
        # Anchors: previously verified PR156 exact KSP10 model and tank.
        a=values[80,2000,10]
        z=values[80,2000,10000]
        assert abs(a[0]-0.462701267)<1e-6
        assert abs(a[1]-0.079264690)<1e-6
        assert abs(z[0]-0.124579814)<1e-6
        assert abs(z[1]-0.119093670)<1e-6
        for beta in BETAS:
            for load in LOADS:
                reference_tank=values[beta,load,10][0]
                original=values[beta,load,10000][1]
                for cin in VALUES_PF:
                    tank,output,_=values[beta,load,cin]
                    assert original>0 and reference_tank>0
                    print("IF455_KSP10_CIN_NORMALIZED",{
                        "beta":beta,"load_ohm":load,"cin_pF":cin,
                        "tank_ratio_to_10p":round(tank/reference_tank,8),
                        "buffer_ratio_to_original_10n":round(output/original,8)},flush=True)
                # Explicitly expose the tradeoff; not a design winner:
                # the theoretical max output is not necessarily the case
                # that best preserves tank Q, noise or frequency response.
                best=max(VALUES_PF,key=lambda c:values[beta,load,c][1])
                print("IF455_KSP10_CIN_MAX_ONLY_UNQUALIFIED",{
                    "beta":beta,"load_ohm":load,
                    "maximum_model_output_coupling_pF":best,
                    "not_a_released_design_value":True},flush=True)
    print("PASS_NATIVE_KICAD9_KSP10_48_IF455_CIN_PF_TANK_VS_OUTPUT_TRADEOFF_NO_VENDOR_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
