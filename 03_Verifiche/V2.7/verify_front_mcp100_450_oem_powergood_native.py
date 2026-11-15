#!/usr/bin/env python3
"""Native MCP100-450DI/TO D-bondout THT supervisor candidate, 54-case OEM DC screen.

Manufacturer original: https://ww1.microchip.com/downloads/en/devicedoc/11187f.pdf
TO-92 D bondout *viewed from front*: pin1 RST_N, pin2 VDD, pin3 VSS.
MCP100 active-low RESET push-pull. Datasheet: 4.25-4.50V trip,
VOH >= VDD-0.7 at <=3mA source and VDD>VTRIPmax, release delay
150-700ms, output behavior guaranteed down to VDD=1.0V.
Not a relay driver/vehicle proof; unqualified NO FAB/NO TX.
"""
from __future__ import annotations
from pathlib import Path
from itertools import product
import subprocess
import tempfile
from verify_interboard_audio_contract_native import exported_nets,require
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_MUTE_MCP100"
SCH=BASE/"FRONT_MCP100_450_POWER_GOOD_THT_V2_7_DRAFT.kicad_sch"
DRIVER=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_MUTE_COIL_DRIVER/FRONT_NC_MUTE_DUAL_ENABLE_COIL_DRIVER_V2_7_DRAFT.kicad_sch"
BOARD=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_PLACEMENT/FRONT_CONTROL_13REFS_PLACEMENT_NONFAB.kicad_pcb"
EXPECTED={
 "PGOOD_5V_LAB":{("U2101","2"),("C2101","1"),("J2101","1")},
 "DRIVER_GND":{("U2101","3"),("C2101","2"),("J2101","2"),("J2102","2")},
 "POWER_GOOD_LAB":{("U2101","1"),("J2102","1")}
}
OEM_PDF="https://ww1.microchip.com/downloads/en/devicedoc/11187f.pdf"

def screen_reset_fault_states():
    """216 illustrative supervisor fault cases; no safety release.

    These are logical output/ground failure injections, NOT OEM guaranteed
    electrical waveforms or measured relay response. A rail above VTRIP max
    still cannot force a welded/stuck output to the intended state.
    """
    faults=("nominal","output_stuck_high","output_stuck_low","ground_open")
    counts={name:0 for name in faults}
    false_high_below_trip=0
    unavailable_high_above_trip=0
    ambiguous_ground=0
    for vin,rcoil,vcesat,fault in product(
        (3.5,4.25,4.5,4.6,5.0,5.5),
        (150.3,167.0,183.7),(.15,.2,.3),faults
    ):
        counts[fault]+=1
        assert rcoil>0 and 0<vcesat<vin
        # An output logic state is not the same as guaranteed relay contact.
        if fault=="nominal":
            guaranteed_high=vin>4.5
            guaranteed_low=1.0<=vin<4.25
            if 4.25<=vin<=4.5:
                assert not guaranteed_high and not guaranteed_low
        elif fault=="output_stuck_high":
            if vin<=4.5:
                false_high_below_trip+=1
        elif fault=="output_stuck_low":
            if vin>4.5:
                unavailable_high_above_trip+=1
        else:
            # Ground reference lost: reset signal is undefined at the load.
            ambiguous_ground+=1
    assert counts==dict.fromkeys(faults,54),counts
    assert false_high_below_trip==27
    assert unavailable_high_above_trip==27
    assert ambiguous_ground==54
    print("MCP100_216_FAULT_STATE_SCREEN_NOT_SAFETY_RELEASE",{
        "cases":sum(counts.values()),
        "false_high_below_or_at_trip_stuck_high":false_high_below_trip,
        "unavailable_high_above_trip_stuck_low":unavailable_high_above_trip,
        "undefined_ground_reference":ambiguous_ground,
        "below_1V_unmodelled":True,
        "contact_weld_not_modelled":True,
        "relay_release_delay_not_qualified":True,
        "no_fab_no_tx":True,
    },flush=True)


def screen_driver_source_current_feasibility():
    """Manufacturer guaranteed VOH only at 3mA: screen upper NPN base load.

    This does not demonstrate a physical driver, coil pull-in, VBE maximum,
    transistor hFE or tolerance/temperature qualification.
    """
    states=0
    impossible_at_oem_source_limit=0
    achievable_in_illustrative_current_only_model=0
    base_ohm=1500.0
    pull_ohm=10000.0
    for vin,rcoil,drop in product(
        (4.6,5.0,5.5),(150.3,167.0,183.7),(.15,.2,.3)
    ):
        # Source must supply both the transistor base and the 10k pulldown.
        # 0.8V VBE and two equal VCEsat drops are illustrative.
        source_cap=0.003
        pull_current=0.8/pull_ohm
        required_base=(vin-2*drop)/(rcoil*10.0)
        required_source=required_base+pull_current
        if required_source>source_cap:
            impossible_at_oem_source_limit+=1
        else:
            achievable_in_illustrative_current_only_model+=1
        # Original nominal base resistor cannot be upgraded merely by
        # choosing a smaller value: verify the allowed source-current region.
        source_at_voh_min=(vin-0.7-0.8)/base_ohm
        assert 0<source_at_voh_min<source_cap
        states+=1
    assert states==27
    assert impossible_at_oem_source_limit>0
    assert impossible_at_oem_source_limit+achievable_in_illustrative_current_only_model==27
    print("MCP100_3MA_OEM_OUTPUT_SOURCE_FEASIBILITY_NOT_DRIVER_RELEASE",{
        "states":states,
        "oem_3mA_source_limit_incompatible_states":impossible_at_oem_source_limit,
        "illustratively_current_feasible_states":achievable_in_illustrative_current_only_model,
        "nominal_Rbase_ohm":base_ohm,
        "assumed_VBE_V":0.8,
        "source_current_bound_mA":3.0,
        "NPN_OEM_and_transient_unqualified":True,
        "NO_FAB_NO_TX":True
    },flush=True)

def main():
    assert SCH.with_suffix(".kicad_pro").is_file()
    assert '(name "TH_MCP100")' in (BASE/"sym-lib-table").read_text(encoding="utf-8")
    library=(BASE/"TH_MCP100.kicad_sym").read_text(encoding="utf-8")
    assert '(symbol "MCP100_450_D_BOND_TO92"' in library
    for pin_no,pin_name in ((1,"RESET_N_PUSH_PULL"),(2,"VDD"),(3,"VSS")):
        assert '(name "'+pin_name+'"' in library
        assert '(number "'+str(pin_no)+'"' in library
    raw=SCH.read_text(encoding="utf-8")
    assert raw.count('(symbol (lib_id "TH_MCP100:MCP100_450_D_BOND_TO92")')==1
    assert raw.count('(symbol (lib_id "TH_MCP100:CAP_THT")')==1
    assert raw.count('(symbol (lib_id "TH_MCP100:PORT2")')==2
    assert "(property \"Footprint\" \"\"" in raw
    assert "NO FAB / NO TX" in raw
    board=BOARD.read_text(encoding="utf-8")
    assert "U2101" not in board and board.count('(segment ')==35
    with tempfile.TemporaryDirectory(prefix="tht_mcp100_oem_") as td:
        d=Path(td)
        erc=d/"mcp100_erc.txt"
        run=subprocess.run(["kicad-cli","sch","erc","--exit-code-violations",
                            "-o",str(erc),str(SCH)],cwd=ROOT,capture_output=True,
                           text=True,timeout=120)
        print("MCP100_OEM_NATIVE_ERC",run.stdout,run.stderr,flush=True)
        if erc.exists():print(erc.read_text(encoding="utf-8"),flush=True)
        run.check_returncode()
        nets=exported_nets(SCH,d/"mcp100.net")
        drv=exported_nets(DRIVER,d/"coil.net")
    assert set(nets)==set(EXPECTED)
    for name,members in EXPECTED.items():
        require(nets,name,*members)
        assert nets[name]==members,(name,nets[name],members)
    require(drv,"POWER_GOOD_LAB",("J1913","1"),("R1912","1"))
    require(drv,"DRIVER_GND",("J1913","2"),("Q1912","3"))
    assert ("U2101","1") not in nets["PGOOD_5V_LAB"]
    total=0;on_requested=0;unsupported_beta=0;valid_output_load=0
    for vin,rcoil,drop in product(
        (3.5,4.25,4.5,4.6,5.,5.5),(150.3,167.,183.7),(.15,.2,.3)):
        # Datasheet guarantees released (high) after startup delay
        # only when VDD strictly exceeds maximum threshold 4.5V.
        if vin>4.50:
            on_requested+=1
            # Manufacturer guaranteed minimum VOH at 3mA
            output_high=vin-.7
            # Intended Q1912 1k5 base resistor and 10k pull to GND:
            # VBE=0.8V is illustrative, not a transistor OEM guarantee.
            ibase=(output_high-.8)/1500.-.8/10000.
            assert 0<ibase<.003
            valid_output_load+=1
            icoil=(vin-2*drop)/rcoil
            if ibase<icoil/10:
                unsupported_beta+=1
        total+=1
    assert total==54 and on_requested==27 and valid_output_load==27
    assert unsupported_beta==27
    # MCP100 D-bondout must not be assigned to a generic TO92 footprint
    # or safety-released based solely on textual pin ordering.
    assert OEM_PDF.endswith("11187f.pdf")
    assert 4.25 < 4.375 < 4.5
    assert 150<=350<=700
    screen_reset_fault_states()
    screen_driver_source_current_feasibility()
    print("FRONT_MCP100_450_TO92_OEM_SCREEN",{
        "OEM_datasheet":OEM_PDF,
        "part_candidate":"MCP100-450DI/TO",
        "manufacturer_D_bondout_pins":{1:"RST_N",2:"VDD",3:"VSS"},
        "Vtrip_min_typ_max_V":(4.25,4.375,4.5),
        "RESET_release_delay_min_typ_max_ms":(150,350,700),
        "VOH_min_at_3mA":"VDD-0.7",
        "cases":total,"high_guaranteed_after_release_states":on_requested,
        "high_output_at_most_3mA_load_tested":valid_output_load,
        "167ohm_Omron_hypothetical_forced_beta10_unsatisfied_cases":unsupported_beta,
        "relay_unqualified":True,
        "deep_supply_below_1V_unspecified":True,
        "bouncing_interboard_audio_ground_unresolved":True,
        "TO92_footprint_not_assigned":True,
        "NO_FAB_NO_TX":True},flush=True)
    print("PASS_KICAD9_MCP100_450_DI_TO_D_BOND_3NET_ERC0_54_OEM_SCREEN_NONFAB",flush=True)
if __name__=="__main__":main()
