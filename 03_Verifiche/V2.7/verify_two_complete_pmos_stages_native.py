#!/usr/bin/env python3
"""Native KiCad9 THT candidate: TWO complete back-to-back P-FET switches in series.

Physical 4 P-MOS and 2 NPN sinks. Static directed graph of intrinsic diodes,
not an OEM I/V, load/thermal, or safety qualification.
"""
from pathlib import Path
import itertools
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets,require
from verify_q806_dual_zener_clamp_native import N as SINGLE

SCH=ROOT/"04_KiCad/V2.7_DRAFT/MAIN_SECONDARY_OVP_TWO_COMPLETE_STAGES/MAIN_SECONDARY_OVP_TWO_COMPLETE_STAGES_LAB_V2_7_DRAFT.kicad_sch"
REN={
"Q804":"Q814","Q805":"Q815","Q806":"Q816",
"R2101":"R2111","R2102":"R2112","R2103":"R2113","R2104":"R2114",
"D2101":"D2111","D2102":"D2112",
"J2101":"J2111","J2102":"J2112","J2103":"J2113"
}
NET={
"PRIMARY_IN_DRAIN_LAB":"SECONDARY_OUT_DRAIN_LAB",
"SECONDARY_OUT_DRAIN_LAB":"FINAL_SECONDARY_OUT_LAB",
"FLOATING_COMMON_SOURCE_LAB":"FLOATING_SOURCE_B_LAB",
"COMMON_GATE_LAB":"COMMON_GATE_B_LAB",
"DRIVER_SINK_LAB":"DRIVER_SINK_B_LAB",
"ENABLE_LOGIC_5V_LAB":"ENABLE_B_5V_LAB",
"Q806_BASE_LAB":"Q816_BASE_LAB"
}
EXPECTED={k:set(v) for k,v in SINGLE.items()}
for k,members in SINGLE.items():
    dest=NET.get(k,k)
    EXPECTED.setdefault(dest,set()).update((REN[ref],pin) for ref,pin in members)

def direction(gate_a,gate_b):
    # P-FET diode Q804 / Q814 DRAIN->SOURCE, Q805 / Q815 DRAIN->SOURCE
    # Stage A nodes: IN->SRC_A<-MID; Stage B: MID->SRC_B<-OUT.
    # When a stage driver ON, both channels of that complete pair ON.
    e=[("IN","SA"),("MID","SA"),("MID","SB"),("OUT","SB")]
    if gate_a:
        e += [("SA","IN"),("SA","MID")]
    if gate_b:
        e += [("SB","MID"),("SB","OUT")]
    def reachable(start,dest):
        seen={start};pending=[start]
        while pending:
            x=pending.pop()
            if x==dest:return True
            for u,v in e:
                if u==x and v not in seen:
                    seen.add(v);pending.append(v)
        return False
    return reachable("IN","OUT"),reachable("OUT","IN")

def main():
    source=SCH.read_text(encoding="utf-8")
    assert source.count('(symbol (lib_id "LAB_OVP:')==24
    for ref in REN.values():
        assert source.count('(property "Reference" "'+ref+'"')==1,ref
    assert "NO FAB / NO TX / NO BATTERIA / NO VEICOLO" in source
    with tempfile.TemporaryDirectory(prefix="dual_full_series_stage_native_") as t:
        erc=Path(t)/"two_stage.erc"
        result=subprocess.run(["kicad-cli","sch","erc","--exit-code-violations",
                               "-o",str(erc),str(SCH)],
                              cwd=ROOT,capture_output=True,text=True)
        print("TWO_STAGE_NATIVE_ERC",result.stdout,result.stderr,flush=True)
        if erc.exists():print(erc.read_text(encoding="utf-8"),flush=True)
        result.check_returncode()
        net=exported_nets(SCH,Path(t)/"two_stage.net")
    assert set(net)==set(EXPECTED),(set(net)^set(EXPECTED))
    for n,ends in EXPECTED.items():
        require(net,n,*ends)
        assert net[n]==ends,(n,sorted(net[n]^ends))
    assert len(net)==14 and sum(map(len,net.values()))==54
    assert len(set.union(*net.values()))==54
    assert {("Q804","2"),("J2101","1")}<=net["PRIMARY_IN_DRAIN_LAB"]
    assert {("Q805","2"),("Q814","2"),("J2102","1"),("J2111","1")}<=net["SECONDARY_OUT_DRAIN_LAB"]
    assert {("Q815","2"),("J2112","1")}<=net["FINAL_SECONDARY_OUT_LAB"]
    assert {("Q804","3"),("Q805","3")}<=net["FLOATING_COMMON_SOURCE_LAB"]
    assert {("Q814","3"),("Q815","3")}<=net["FLOATING_SOURCE_B_LAB"]
    assert net["FLOATING_COMMON_SOURCE_LAB"].isdisjoint(net["FLOATING_SOURCE_B_LAB"])
    assert net["COMMON_GATE_LAB"].isdisjoint(net["COMMON_GATE_B_LAB"])
    assert net["DRIVER_SINK_LAB"].isdisjoint(net["DRIVER_SINK_B_LAB"])
    assert net["ENABLE_LOGIC_5V_LAB"].isdisjoint(net["ENABLE_B_5V_LAB"])
    assert direction(False,False)==(False,False)
    assert direction(True,False)==(False,False)
    assert direction(False,True)==(False,False)
    assert direction(True,True)==(True,True)
    scenarios=0;one_driver_short_still_both_cut=0
    for en_a,en_b,ce_short_a,ce_short_b in itertools.product((False,True),repeat=4):
        commanded_a=en_a or ce_short_a
        commanded_b=en_b or ce_short_b
        fwd,rev=direction(commanded_a,commanded_b)
        assert (fwd,rev)==(commanded_a and commanded_b,commanded_a and commanded_b)
        if not en_a and not en_b and (ce_short_a != ce_short_b):
            assert not fwd and not rev
            one_driver_short_still_both_cut+=1
        scenarios+=1
    assert scenarios==16 and one_driver_short_still_both_cut==2
    print("TWO_ANTISERIES_THT_STAGE_NATIVE",{
        "physical_THT_components":24,"physical_pins":54,"nets":14,
        "synthetic_directional_fault_states":scenarios,
        "single_CE_short_both_enables_off_blocks_both_directions":2,
        "real_PFET_on_state_qualified":False,
        "common_return_and_external_enables_qualified":False,
        "individual_FET_DS_SHORT_covered":False,
        "surge_clamps_SOA_and_real_PG_qualified":False,
        "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True
    },flush=True)
    print("PASS_NATIVE_KICAD9_TWO_COMPLETE_PMOS_STAGES_54PIN_14NET_16_NONFAB",flush=True)

if __name__=="__main__":
    main()
