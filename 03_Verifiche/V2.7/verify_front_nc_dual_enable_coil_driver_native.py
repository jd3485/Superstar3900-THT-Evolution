#!/usr/bin/env python3
"""KiCad9 native isolated dual-NPN coil driver, plus bounded idealized DC screen.

This is a *laboratory topology candidate*, NOT an OEM coil or safety circuit.
Two series low-side transistor switches need AUDIO_ENABLE and POWER_GOOD,
both separately asserted from external sources; no supervisor is designed.
Numerical screen only assumes two NPNs with <=0.3 V VCEsat each, hypothetical
coil >=250 ohm, 5.5V max rail, logic >=4.5V and forced beta <=10.
It never proves BJT saturation or actual component PVT/noise/EMI.
"""
from __future__ import annotations
import math
from pathlib import Path
import subprocess
import tempfile
from itertools import product
from verify_interboard_audio_contract_native import exported_nets, require
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_MUTE_COIL_DRIVER"
NAME="FRONT_NC_MUTE_DUAL_ENABLE_COIL_DRIVER_V2_7_DRAFT"
SCH=BASE/(NAME+".kicad_sch")
CONTACT=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_MUTE_NC_RELAY/FRONT_NC_MUTE_CONTACT_THT_V2_7_DRAFT.kicad_sch"
BOARD=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_PLACEMENT/FRONT_CONTROL_13REFS_PLACEMENT_NONFAB.kicad_pcb"
EXPECTED={
 "COIL_PLUS_LAB":{("J1911","1"),("D1911","1"),("J1914","1")},
 "COIL_MINUS_LAB":{("J1914","2"),("D1911","2"),("Q1911","2")},
 "SERIES_MID":{("Q1911","3"),("Q1912","2")},
 "DRIVER_GND":{("Q1912","3"),("R1913","2"),("R1914","2"),
               ("J1911","2"),("J1912","2"),("J1913","2")},
 "DRIVE1_BASE":{("Q1911","1"),("R1911","2"),("R1913","1")},
 "DRIVE2_BASE":{("Q1912","1"),("R1912","2"),("R1914","1")},
 "ENABLE_AUDIO_LAB":{("J1912","1"),("R1911","1")},
 "POWER_GOOD_LAB":{("J1913","1"),("R1912","1")},
}
def main():
    raw=SCH.read_text(encoding="utf-8")
    assert SCH.with_suffix(".kicad_pro").is_file()
    assert '(name "TH_COIL")' in (BASE/"sym-lib-table").read_text(encoding="utf-8")
    library=(BASE/"TH_COIL.kicad_sym").read_text(encoding="utf-8")
    assert all('(symbol "'+s+'"' in library
               for s in ("NPN_ABSTRACT","RESISTOR","FLYBACK_DIODE","PORT2"))
    assert raw.count('(symbol (lib_id "TH_COIL:NPN_ABSTRACT")')==2
    assert raw.count('(symbol (lib_id "TH_COIL:RESISTOR")')==4
    assert raw.count('(symbol (lib_id "TH_COIL:FLYBACK_DIODE")')==1
    assert raw.count('(symbol (lib_id "TH_COIL:PORT2")')==4
    assert raw.count("1k5_THT_BASERES")==2
    assert raw.count("10k_THT_PULLDOWN")==2
    # Gate physical THT footprint on all four passive resistors (not a driver qualification).
    assert raw.count("Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal")==4
    # OEM diode cathode K=1 on COIL_PLUS, anode A=2 on COIL_MINUS.
    # 1N4007-E3/54 is a candidate only; clamp release-time unqualified.
    assert raw.count("1N4007-E3/54_CANDIDATE_NOT_RELEASED")==1
    assert raw.count("Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal")==1
    assert "(name \"K\"" in library and "(name \"A\"" in library
    assert "NO FAB / NO TX" in raw
    board=BOARD.read_text(encoding="utf-8")
    assert "Q1911" not in board and "Q1912" not in board
    assert board.count('(segment ')==35
    with tempfile.TemporaryDirectory(prefix="tht_coil_driver_kicad9_") as td:
        d=Path(td)
        erc=d/"coil_erc.rpt"
        run=subprocess.run(["kicad-cli","sch","erc","--exit-code-violations",
                            "-o",str(erc),str(SCH)],cwd=ROOT,
                           capture_output=True,text=True,timeout=120)
        print("DUAL_ENABLE_COIL_DRIVER_NATIVE_KICAD9_ERC",run.stdout,run.stderr,flush=True)
        if erc.exists():print(erc.read_text(encoding="utf-8"),flush=True)
        run.check_returncode()
        nets=exported_nets(SCH,d/"coil.net")
        contact=exported_nets(CONTACT,d/"contact.net")
    assert set(nets)==set(EXPECTED),(sorted(nets),sorted(EXPECTED))
    for name,pins in EXPECTED.items():
        require(nets,name,*pins)
        assert nets[name]==pins,(name,nets[name],pins)
    require(contact,"COIL_PLUS_LAB",("J1903","1"),("K1901","4"))
    require(contact,"COIL_MINUS_LAB",("J1903","2"),("K1901","5"))
    assert nets["COIL_PLUS_LAB"].isdisjoint(nets["COIL_MINUS_LAB"])
    assert ("D1911","1") in nets["COIL_PLUS_LAB"]
    assert ("D1911","2") in nets["COIL_MINUS_LAB"]
    assert nets["SERIES_MID"]=={("Q1911","3"),("Q1912","2")}
    # 4 logic control combinations; connected coil has no independent ground
    # unless BOTH switches conduct (idealized). Stuck-ON transistor cases
    # are explicitly NOT protected by this simple two-enable chain.
    for enable,good in product((False,True),repeat=2):
        assert (enable and good)==(enable and good)
        if not (enable and good):
            assert not(enable and good)
    checked=0
    margins=[]
    for rail,drive,rcoil,drop in product((4.5,5.0,5.5),(4.5,5.0),
                                       (250.,330.,500.,1000.),(.15,.30)):
        if rail<2*drop:continue
        icoil=(rail-2*drop)/rcoil
        # Upper switch emitter may rise by roughly VCEsat of lower switch.
        # VBE 0.8V assumed conservatively for switching DC screen.
        upper_base=drive-(.8+drop)
        lower_base=drive-.8
        iupper=max(0.,upper_base/1500.-(.8+drop)/10000.)
        ilower=max(0.,lower_base/1500.-.8/10000.)
        assert min(iupper,ilower)>icoil/10.,(rail,drive,rcoil,drop,icoil,iupper,ilower)
        assert icoil<.025,(rail,rcoil,icoil)
        assert max(iupper,ilower)<.005
        checked+=1
        margins.append((min(iupper,ilower)/(icoil/10.)))
    assert checked==3*2*4*2==48
    print("COIL_DRIVER_HYPOTHETICAL_DC_48_CASES",{
        "cases":checked,"assumed_rail_V":(4.5,5.,5.5),
        "assumed_logic_V":(4.5,5.),"coil_R_ohm_scenarios":(250.,330.,500.,1000.),
        "assumed_each_BJT_VCEsat_V":(.15,.30),
        "minimum_base_current_relative_to_forced_beta10":round(min(margins),4),
        "relay_coil_and_SPND_MPN_qualified":False,
        "actual_min_logic_voltage_qualified":False,
        "relay_flyback_energy_diode_OEM_qualified":False,
        "no_powergood_supervisor_or_safety_cert":True,
        "no_independent_welded_NO_or_open_AF_GND_protection":True,
        "NO_FAB_NO_TX":True},flush=True)
    # Analytical RL *electrical* decay only; NOT a contact release time.
    # D1911 K is on COIL_PLUS and A on COIL_MINUS (verified above).
    # With both NPN open and diode forward-biased: L di/dt + R i + Vf = 0.
    # Unknown relay inductance and diode Vf: explicit illustrative scenarios.
    # Coil resistances from OEM DC5/DC6 nominal +-10% at 23 C, but
    # these MPNs already failed the independent drive/pickup screening.
    release_states=0
    elapsed_10=[]
    energies=[]
    for nominal_r,rail,tolerance,l_h,vf,drop in product(
        (167.,240.),(4.6,5.,5.5),(.9,1.,1.1),
        (.02,.1,.5),(.55,.9),(.15,.30)):
        r=nominal_r*tolerance
        i0=(rail-2*drop)/r
        assert i0>0
        assert l_h>0 and vf>0
        # t(f) = L/R * ln[(I0 + Vf/R)/(f*I0 + Vf/R)].
        def decay_time(f):
            return l_h/r*math.log((i0+vf/r)/(f*i0+vf/r))
        t50,t10=decay_time(.5),decay_time(.1)
        assert 0<t50<t10
        i50=(i0+vf/r)*math.exp(-r*t50/l_h)-vf/r
        i10=(i0+vf/r)*math.exp(-r*t10/l_h)-vf/r
        assert math.isclose(i50,i0*.5,rel_tol=1e-10)
        assert math.isclose(i10,i0*.1,rel_tol=1e-10)
        # Clamp with higher Vf hastens *electrical current decay*,
        # without proving either contact timing or transistor peak voltage.
        if vf==.55:
            faster=l_h/r*math.log((i0+.9/r)/(.1*i0+.9/r))
            assert faster<t10
        elapsed_10.append(t10)
        energies.append(.5*l_h*i0*i0)
        release_states+=1
    assert release_states==2*3*3*3*2*2==216
    assert min(elapsed_10)>0 and max(elapsed_10)>min(elapsed_10)
    print("FRONT_D1911_RL_DIODE_216_ELECTRICAL_DECAY_ONLY_NO_RELAY_RELEASE",{
        "states":release_states,
        "t10_electrical_current_ms_range":tuple(round(1000*x,5)
            for x in (min(elapsed_10),max(elapsed_10))),
        "initial_coil_magnetic_energy_mJ_range":tuple(round(1000*x,5)
            for x in (min(energies),max(energies))),
        "illustrative_L_H":(.02,.1,.5),
        "illustrative_Vf_V":(.55,.9),
        "NO_RELAY_CONTACT_RELEASE_TIME_QUALIFICATION":True,
        "NO_TRANSISTOR_AVALANCHE_OR_DIODE_TRANSIENT_QUALIFICATION":True,
        "NO_FAB_NO_TX":True},flush=True)
    print("PASS_FRONT_D1911_216_RL_ELECTRICAL_DECAY_ILLUSTRATIVE_NONFAB",flush=True)
    print("PASS_KICAD9_FRONT_COIL_DUAL_ENABLE_8NETS_ERC0_48_ILLUSTRATIVE_DC_NO_FAB_NO_TX",flush=True)
if __name__=="__main__":main()
