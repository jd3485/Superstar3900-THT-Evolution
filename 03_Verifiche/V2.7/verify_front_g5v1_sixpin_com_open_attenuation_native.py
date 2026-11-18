#!/usr/bin/env python3
"""Native OEM G5V-1 six-pad FRONT: NC attenuation lost by COM bond failures.

Checks AC magnitude loss of mute in deenergized, no-weld contact corner,
not absolute safety limits. References are bounded only with intact AF_GND.
"""
from pathlib import Path
from itertools import product
import math
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets
from verify_front_g5v1_six_terminal_oem_pin_map_native import OEM_TO_EXISTING_NET
from verify_front_g5v1_sixpin_dual_com_impedance_ac_native import (
  reduced,nodal3,FREQ,CC,RSRC,COM_OHM,CONTACT_OHM)
SCH=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_CONTROL_PARTIAL_G5V1_SIXPIN_CANDIDATE.kicad_sch"

def main():
    with tempfile.TemporaryDirectory(prefix="front_com_open_attenuation_") as tmp:
        nets=exported_nets(SCH,Path(tmp)/"candidate.net")
    endpoint={}
    for name,members in nets.items():
        for member in members:
            assert member not in endpoint
            endpoint[member]=name.rsplit("/",1)[-1]
    assert {str(pin):endpoint[("K1901",str(pin))] for pin in OEM_TO_EXISTING_NET}=={
        str(pin):net for pin,net in OEM_TO_EXISTING_NET.items()}
    assert endpoint[("K1901","5")]==endpoint[("K1901","6")]==endpoint[("R1902","1")]
    n=0
    maximum_single_bond_degradation=1.
    maximum_dual_bond_degradation=1.
    for f,cc,rs,nc,good_com in product(FREQ,CC,RSRC,CONTACT_OHM,COM_OHM[:2]):
        # Cable injection from 1V AC source, relay deenergized NC engaged,
        # no welded NO. Single OPEN removes one physical COM solder bond.
        both=reduced(f,cc,rs,nc,math.inf,good_com,good_com)
        one=reduced(f,cc,rs,nc,math.inf,good_com,math.inf)
        none=reduced(f,cc,rs,nc,math.inf,math.inf,math.inf)
        nc_open=reduced(f,cc,rs,math.inf,math.inf,good_com,good_com)
        assert abs(none-nc_open)<1e-12,(f,cc,rs,nc,none,nc_open)
        assert abs(both)<=abs(one)*(1+1e-8),(f,cc,rs,nc,both,one)
        assert abs(one)<=abs(none)*(1+1e-8),(f,cc,rs,nc,one,none)
        assert abs(both)>0.
        assert abs(one-nodal3(f,cc,rs,nc,math.inf,good_com,math.inf))<1e-8
        assert abs(none-nodal3(f,cc,rs,nc,math.inf,math.inf,math.inf))<1e-12
        maximum_single_bond_degradation=max(maximum_single_bond_degradation,abs(one)/abs(both))
        maximum_dual_bond_degradation=max(maximum_dual_bond_degradation,abs(none)/abs(both))
        n+=1
    assert n==len(FREQ)*len(CC)*len(RSRC)*len(CONTACT_OHM)*2
    assert maximum_single_bond_degradation>=1
    assert maximum_dual_bond_degradation>maximum_single_bond_degradation
    print("PASS_FRONT_G5V1_NATIVE_DUAL_COM_BOND_OPEN_MUTED_AC_DEGRADATION",{
      "native_deenergized_NC_cases":n,
      "single_bond_open_can_weaken_shunt":True,
      "both_bonds_open_equivalent_to_NC_open":True,
      "maximum_single_bond_degradation_ratio_hypothetical":maximum_single_bond_degradation,
      "maximum_both_bonds_degradation_ratio_hypothetical":maximum_dual_bond_degradation,
      "shared_ground_open_unbounded":True,
      "silence_or_product_safety_qualified":False,
      "PCB_or_DRC":False,
      "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True},flush=True)
if __name__=="__main__":main()
