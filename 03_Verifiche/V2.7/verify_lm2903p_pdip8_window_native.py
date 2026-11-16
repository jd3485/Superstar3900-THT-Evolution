#!/usr/bin/env python3
"""Native KiCad9 LM2903P THT pre-powered UVLO/OVP window proof, NONFAB.

External supply and reference are bench assumptions; no input protection,
power loss clamp or independent power switch is present.
"""
from pathlib import Path
import itertools
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets,require

SCH=ROOT/"04_KiCad/V2.7_DRAFT/MAIN_SECONDARY_LM2903P_WINDOW/MAIN_SECONDARY_LM2903P_WINDOW_LAB_V2_7_DRAFT.kicad_sch"
NET={
"VIN_RAW_LAB":{("J2201","1"),("R2201","1")},
"VIN_SENSE":{("R2201","2"),("R2202","1"),("U2201","3"),("U2201","6")},
"LAB_RETURN":{("J2201","2"),("J2202","2"),("J2203","2"),("J2204","2"),("R2202","2"),("R2204","2"),("R2206","2"),("U2201","4")},
"EXTERNAL_5V_UNQUALIFIED":{("J2202","1"),("U2201","8"),("R2207","1")},
"EXTERNAL_VREF_2V5_UNQUALIFIED":{("J2203","1"),("R2203","1"),("R2205","1")},
"OVP_REF":{("R2203","2"),("R2204","1"),("U2201","5")},
"UVLO_REF":{("R2205","2"),("R2206","1"),("U2201","2")},
"WINDOW_GOOD_OC_BIASED_LAB":{("U2201","1"),("U2201","7"),("R2207","2"),("J2204","1")},
}
def main():
    s=SCH.read_text(encoding="utf8")
    assert "LM2903P_PDIP8_LAB" in s
    assert "Package_DIP:DIP-8_W7.62mm" in s
    assert "NO FAB / NO TX / NO BATTERIA / NO VEICOLO" in s
    assert s.count('(symbol (lib_id "LAB_WINDOW:')==12
    with tempfile.TemporaryDirectory(prefix="lm2903p_native_window_") as d:
        tmp=Path(d)
        report=tmp/"window.erc"
        p=subprocess.run(["kicad-cli","sch","erc","--exit-code-violations",
                          "-o",str(report),str(SCH)],capture_output=True,text=True,cwd=ROOT)
        print("LM2903P_WINDOW_NATIVE_ERC",p.stdout,p.stderr,flush=True)
        if report.exists():print(report.read_text(encoding="utf8"),flush=True)
        p.check_returncode()
        nets=exported_nets(SCH,tmp/"window.net")
    assert set(nets)==set(NET),(set(nets)^set(NET))
    for name,ends in NET.items():
        require(nets,name,*ends)
        assert nets[name]==ends,(name,sorted(nets[name]))
    assert sum(map(len,nets.values()))==30 and len(nets)==8
    assert ("U2201","8") in nets["EXTERNAL_5V_UNQUALIFIED"]
    assert ("U2201","4") in nets["LAB_RETURN"]
    assert ("U2201","3") in nets["VIN_SENSE"]
    assert ("U2201","6") in nets["VIN_SENSE"]
    assert ("U2201","2") in nets["UVLO_REF"]
    assert ("U2201","5") in nets["OVP_REF"]
    assert ("U2201","1") in nets["WINDOW_GOOD_OC_BIASED_LAB"]
    assert ("U2201","7") in nets["WINDOW_GOOD_OC_BIASED_LAB"]
    # Window thresholds with symbolic resistor parts, not OEM reference.
    count=0
    extremes=[[1000.,0.],[1000.,0.]]
    worst_open_pin_V=0.
    for rs_hi,rs_lo,ov_hi,ov_lo,uv_hi,uv_lo,vref in itertools.product(
        (.99,1.01),(.99,1.01),(.99,1.01),(.99,1.01),
        (.99,1.01),(.99,1.01),(2.475,2.525)
    ):
        sense=5000*rs_lo/(100000*rs_hi+5000*rs_lo)
        uvref=vref*20000*uv_lo/(85000*uv_hi+20000*uv_lo)
        ovref=vref*20000*ov_lo/(50000*ov_hi+20000*ov_lo)
        uv=uvref/sense
        ov=ovref/sense
        assert uv<13.8<ov
        assert uv<ov
        extremes[0][0]=min(extremes[0][0],uv)
        extremes[0][1]=max(extremes[0][1],uv)
        extremes[1][0]=min(extremes[1][0],ov)
        extremes[1][1]=max(extremes[1][1],ov)
        # Single R2202 lower sensing resistor OPEN: unprotected
        # input rises to the raw VIN (approx), even though normal
        # divider VIN48 nominal is ~2.286V.
        worst_open_pin_V=max(worst_open_pin_V,48.)
        count+=1
    assert count==128 and worst_open_pin_V==48.
    print("LM2903P_THT_NATIVE_WINDOW_MODEL",{
       "native_pins":30,"native_nets":8,"part_count":12,
       "window_cases":count,
       "UVLO_min_max_V":[round(x,5) for x in extremes[0]],
       "OVP_min_max_V":[round(x,5) for x in extremes[1]],
       "R2202_OPEN_unprotected_pin_V_at_hypothetical_raw48V":48.,
       "comparator_input_48V_absolute_rating_qualified":False,
       "independent_5V_supply_and_2V5_reference_implemented":False,
       "OC_output_high_if_unpowered_guaranteed":False,
       "independent_series_disconnect_present":False,
       "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True
    },flush=True)
    print("PASS_NATIVE_KICAD9_LM2903P_PDIP8_30PIN_8NET_128_WINDOW_NONFAB",flush=True)
if __name__=="__main__": main()
