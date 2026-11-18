#!/usr/bin/env python3
"""Native KiCad9 FRONT six-pin: finite dual COM solder impedance in AC faults.

Independent 3-node complex nodal KCL vs independently reduced Norton network.
The values are hypothetical screening corners, not OEM contact specifications.
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
SCH=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_CONTROL_PARTIAL_G5V1_SIXPIN_CANDIDATE.kicad_sch"
MUTE=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_MUTE_NC_RELAY/FRONT_G5V1_SIXPIN_ISOLATED_NATIVE_CANDIDATE.kicad_sch"
COM_OHM=(0.05,5.,math.inf)
CONTACT_OHM=(0.1,10.)
FREQ=(300.,1000.,3000.)
CC=(100e-12,1e-9)
RSRC=(10000.,50000.)
SERIES=1000.
BLEED=100000.
INPUT_R=10000.
INPUT_C=100e-9
LM386_RIN=50000.

def g(r):
    return 0. if math.isinf(r) else 1./r

def components(f,cc,rsource,nc_ohm,no_ohm,com5_ohm,com6_ohm):
    omega=2.*math.pi*f
    yc=1j*omega*cc
    ya=1./(INPUT_R+1./(1j*omega*INPUT_C)+LM386_RIN)
    yb=1./BLEED
    gs=1./SERIES
    gc=g(com5_ohm)+g(com6_ohm)
    gn=g(nc_ohm)
    go=0. if math.isinf(no_ohm) else 1./(rsource+no_ohm)
    return yc,ya,yb,gs,gc,gn,go

def reduced(f,cc,rs,nc,no,c5,c6):
    yc,ya,yb,gs,gc,gn,go=components(f,cc,rs,nc,no,c5,c6)
    if gc==0:
        vm=yc/(yc+yb+ya)
    else:
        d=gc+gn+go
        assert d>0
        # Current at board common B through two parallel COM solder bonds.
        ycontact=gc*(gn+go)/d
        ino=gc*go/d
        vm=(yc+gs*ino/(gs+ycontact))/(yc+yb+ya+gs*ycontact/(gs+ycontact))
    return vm*LM386_RIN*ya

def gaussian3(matrix,rhs):
    # Independently solved 3-node KCL with partial pivoting.
    m=[[complex(v) for v in row]+[complex(y)] for row,y in zip(matrix,rhs)]
    for k in range(3):
        pivot=max(range(k,3),key=lambda i:abs(m[i][k]))
        assert abs(m[pivot][k])>1e-15
        m[k],m[pivot]=m[pivot],m[k]
        scale=m[k][k]
        m[k]=[x/scale for x in m[k]]
        for j in range(3):
            if j==k:continue
            q=m[j][k]
            m[j]=[m[j][i]-q*m[k][i] for i in range(4)]
    return [m[i][3] for i in range(3)]

def nodal3(f,cc,rs,nc,no,c5,c6):
    yc,ya,yb,gs,gc,gn,go=components(f,cc,rs,nc,no,c5,c6)
    if gc==0:
        # Floating internal COM isolated from board by BOTH pad bonds.
        vm=yc/(yc+yb+ya)
        return vm*LM386_RIN*ya
    matrix=((gc+gn+go,-gc,0),
            (-gc,gc+gs,-gs),
            (0,-gs,gs+yc+yb+ya))
    rhs=(go,0,yc)
    vc,vb,vm=gaussian3(matrix,rhs)
    for row,target,actual in zip(matrix,rhs,(vc,vb,vm)):
        assert abs(sum(x*y for x,y in zip(row,(vc,vb,vm)))-target)<1e-9
    return vm*LM386_RIN*ya

def main():
    with tempfile.TemporaryDirectory(prefix="front_sixpin_com_impedance_") as td:
        nets=exported_nets(SCH,Path(td)/"front.net")
    members={}
    for name,pins in nets.items():
        for pin in pins:
            assert pin not in members
            members[pin]=name.rsplit("/",1)[-1]
    assert {p:members[("K1901",p)] for p in OEM_TO_EXISTING_NET}=={
        str(p):net for p,net in OEM_TO_EXISTING_NET.items()}
    assert members[("K1901","5")]==members[("K1901","6")]=="RELAY_COM_AUDIO"
    assert members[("J1902","1")]==members[("R1902","2")]=="AMP_INPUT_MUTED"
    assert members[("R1901","2")]==members[("K1901","1")]=="AF_GND"
    assert '1k_SERIES_AUDIO_INPUT_CANDIDATE' in MUTE.read_text()
    assert '100k_AMP_INPUT_BLEED_CANDIDATE' in MUTE.read_text()
    simulations=0
    undefined_ground=0
    both_com_open=0
    discrepancy=0.
    for coil,nc_open,no_weld,ground_open,c5,c6,rcn,rco,f,cc,rs in product(
            (False,True),(False,True),(False,True),(False,True),
            COM_OHM,COM_OHM,CONTACT_OHM,CONTACT_OHM,FREQ,CC,RSRC):
        if ground_open:
            # Shared reference opened; a finite voltage answer would be false.
            undefined_ground+=1
            continue
        nc=rcn if not coil and not nc_open else math.inf
        no=rco if coil or no_weld else math.inf
        a=reduced(f,cc,rs,nc,no,c5,c6)
        b=nodal3(f,cc,rs,nc,no,c5,c6)
        assert all(math.isfinite(v) for v in (a.real,a.imag,b.real,b.imag))
        assert abs(a-b)<max(1e-10,1e-8*max(abs(a),abs(b))),(coil,nc_open,no_weld,c5,c6,rcn,rco,f,cc,rs,a,b)
        discrepancy=max(discrepancy,abs(a-b))
        both_com_open+=int(math.isinf(c5) and math.isinf(c6))
        simulations+=1
    assert simulations==8*9*4*3*2*2
    assert undefined_ground==simulations
    assert both_com_open==simulations//9
    print("PASS_FRONT_G5V1_FINITE_DUAL_COM_NATIVE_AC_TWO_SOLVERS",{
        "defined_reference_cases":simulations,
        "unbounded_shared_ground_cases":undefined_ground,
        "both_COM_solder_bonds_open_cases":both_com_open,
        "max_solver_discrepancy":discrepancy,
        "COM_resistance_hypothetical_ohm":COM_OHM,
        "production_PVT_or_contact_qualification":False,
        "PCB_or_DRC":False,
        "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True},flush=True)
if __name__=="__main__":main()
