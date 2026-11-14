#!/usr/bin/env python3
"""Native KiCad9 MCP6002 PDIP8 bench-only high-Z AM-envelope follower.

An actual MAIN RX/AGC source, reverse/overvoltage input protection, full
output stress qualification and moving-coil driver are NOT implemented.
"""
import math
import subprocess
import tempfile
from pathlib import Path
from verify_interboard_audio_contract_native import exported_nets,require

ROOT=Path(__file__).resolve().parents[2]
SCHEMATIC=ROOT/"04_KiCad/V2.7_DRAFT/SMETER_MCP6002_HIGHZ_BENCH/SMETER_MCP6002_HIGHZ_BENCH_V2_7_DRAFT.kicad_sch"
REFS={"U1901","J1901","J1902","J1903","R1901","R1902","R1903","R1904","C1901","C1902","D1901"}
EXPECTED={
 "AM_ENV_DC_BENCH":{("J1901","1"),("R1903","1")},
 "AM_ENV_AFTER_R1903":{("R1903","2"),("U1901","3"),("R1901","1"),("C1902","1"),("D1901","1")},
 "SMBUF_BENCH_GND":{("J1901","2"),("J1902","2"),("J1903","2"),("U1901","4"),("U1901","5"),("R1901","2"),("C1901","2"),("C1902","2"),("R1904","2")},
 "VLAB5_BUFFER":{("J1903","1"),("U1901","8"),("C1901","1"),("D1901","2"),("R1904","1")},
 "SMBUF_A_FB":{("U1901","1"),("U1901","2"),("R1902","1")},
 "SMBUF_B_FB":{("U1901","6"),("U1901","7")},
 "SMBUF_VOUT_BENCH":{("R1902","2"),("J1902","1")},
}

def main():
    s=SCHEMATIC.read_text(encoding="utf-8")
    # KiCad9 CLI recognizes project-local symbol tables only when the
    # same-basename .kicad_pro exists beside the standalone schematic.
    project=SCHEMATIC.with_suffix(".kicad_pro")
    assert project.is_file(),("Missing KiCad9 project for local symbols",project)
    table=(SCHEMATIC.parent/"sym-lib-table").read_text(encoding="utf-8")
    library=(SCHEMATIC.parent/"TH_SMETERBUF.kicad_sym").read_text(encoding="utf-8")
    assert '(name "TH_SMETERBUF")' in table
    assert 'KIPRJMOD}/TH_SMETERBUF.kicad_sym' in table
    for k in ("J","R","C","U","D"):
        assert '(symbol "'+k+'"' in library
    assert s.count("(symbol (lib_id ")==len(REFS)
    assert s.count('(property "Footprint" "Package_DIP:DIP-8_W7.62mm"')>=1
    assert s.count('(property "Footprint" "Resistor_THT:')>=4
    assert '(property "Value" "4k7_1PCT_0P25W_RAIL_BLEEDER_THT_CANDIDATE"' in s
    assert '(property "Value" "100k_1PCT_0P25W_INPUT_FAULT_LIMIT_CANDIDATE"' in s
    assert s.count('(property "Footprint" "Capacitor_THT:')>=2
    assert '(property "Value" "1nF_50V_C0G_NP0_RF_FILTER_THT_CANDIDATE"' in s
    assert s.count('(property "Footprint" "Connector_PinHeader_2.54mm:')>=3
    assert s.count('(property "Footprint" "Diode_THT:')>=1
    assert '(property "Value" "1N4148_DO35_UPPER_CLAMP_CANDIDATE_NOT_QUALIFIED"' in s
    assert 'MICROCHIP_MCP6002_I_P_PDIP8_CANDIDATE' in s
    assert '(property "Value" "22MEG_1PCT_BIAS_TO_GND_THT"' in s
    assert 'NO MAIN AGC/FSD' in s
    with tempfile.TemporaryDirectory(prefix="tht_mcp6002_highz_") as d:
        temp=Path(d)
        erc=temp/"erc.rpt"
        cp=subprocess.run(
            ["kicad-cli","sch","erc","--exit-code-violations","-o",str(erc),str(SCHEMATIC)],
            cwd=ROOT,capture_output=True,text=True)
        print("MCP6002_HIGHZ_ERC_STDOUT",cp.stdout,cp.stderr,flush=True)
        if erc.exists():
            print("MCP6002_HIGHZ_ERC_REPORT",erc.read_text(encoding="utf-8"),flush=True)
        cp.check_returncode()
        nets=exported_nets(SCHEMATIC,temp/"highz.net")
    assert set(nets)==set(EXPECTED),("Wrong native nets",nets.keys())
    for name,members in EXPECTED.items():
        require(nets,name,*sorted(members))
        assert set(nets[name])==members,("Unexpected pin-net assignment",name,nets[name])
    assert sum(len(members) for members in nets.values())==28
    # 22M passive shunt in parallel with idealized 47k detector: only
    # predicts nominal static DC loading, NOT opamp input leakage or PVT.
    rdet=47000
    rbias=22000000
    rseries=100000
    # The 100k series resistance lies upstream of the 22M input-bias
    # return; this is an ideal DC loading estimate, NOT ESD clamp testing.
    loss=(rdet+rseries)/(rdet+rbias+rseries)
    assert loss<0.01
    for v in (0.1,0.5,1,3,4):
        node=v*rbias/(rdet+rbias+rseries)
        assert math.isclose(node,v*(1-loss),rel_tol=1e-12)
    # RC shunt after R1903: preserve the DC network, attenuate RF in
    # a linear 47k Thevenin laboratory source. This is NOT a nonlinear
    # 455kHz AM demodulator model and excludes pad/PCB/parasitic C.
    c_rf=1e-9
    r_thevenin=1/(1/rbias+1/(rdet+rseries))
    f_3db=1/(2*math.pi*r_thevenin*c_rf)
    attenuation=lambda f:1/math.sqrt(1+(f/f_3db)**2)
    assert 1000<f_3db<1200
    assert attenuation(455000)<0.003
    assert attenuation(10)>0.9999
    assert math.isclose(0.1*rbias/(rdet+rbias+rseries),
                        0.1*(1-loss),rel_tol=1e-12)
    print("MCP6002_HIGHZ_RC_RF_LAB_ONLY",{"C1902_F":c_rf,
          "linear_Thevenin_ohm":round(r_thevenin,2),
          "fc_Hz":round(f_3db,2),
          "gain_455kHz_linear":round(attenuation(455000),7),
          "envelope_demodulation_or_emi_qualification":False},flush=True)
    # Microchip DS20001733L section 4.1.2 + Figures 4-1/4-2:
    # INTERNAL low-side ESD diodes exist; the datasheet calls for
    # EXTERNAL diodes to VDD to prevent high-side overvoltage.
    # The old hypothetical +0.3V upper clamp is NOT present in CAD!
    # Absolute max VIN is VSS-1V..VDD+1V; input +/-2mA is a stress
    # ceiling, never a normal-use specification. Resistive source model
    # demonstrates a dangerous high-positive fault without D1.
    ds_analog_abs_negative=-1.0
    ds_analog_abs_above_rail=1.0
    ds_input_abs_current=0.002
    def upper_unclamped_dc(vsrc):
        return vsrc*rbias/(rbias+rseries)
    upper_fault_cases=((20.0,5.0),(20.0,0.0),(12.0,5.0))
    upper_results={}
    for vsrc,vdd in upper_fault_cases:
        vpin=upper_unclamped_dc(vsrc)
        violates=vpin>vdd+ds_analog_abs_above_rail
        assert violates,(vsrc,vdd,vpin)
        upper_results[(vsrc,vdd)]=round(vpin,4)
    # Negative clamp model is illustrative only: actual diode forward
    # drop and dynamic current are not guaranteed by Figure 4-1.
    neg_src=-20.0
    assumed_vclamp=-0.3
    negative_current=abs(neg_src-assumed_vclamp)/rseries
    assert 0<negative_current<ds_input_abs_current
    # 200V hypothetical *sustained* event is beyond the 100k/0.25W
    # resistor power budget even if current remains near 2mA.
    severe_negative=-200.0
    severe_current=abs(severe_negative-assumed_vclamp)/rseries
    severe_power=(severe_negative-assumed_vclamp)**2/rseries
    assert severe_current<ds_input_abs_current
    assert severe_power>0.25
    # Real D1901 is on the CAD netlist but does NOT make the upstream
    # 5V rail capable of absorbing injection, especially if unpowered.
    assert '(symbol (lib_id "TH_SMETERBUF:D")' in s
    assumed_vf=0.7 # modelling assumption at tiny positive fault current
    injected={}
    for source_v,rail_v in upper_fault_cases:
        if source_v>rail_v+assumed_vf:
            current=(source_v-rail_v-assumed_vf)/rseries
            injected[(source_v,rail_v)]=current
            assert current<ds_input_abs_current
    assert (20.0,0.0) in injected
    # Capacitor C1901 (100nF) is not a DC current sink. If the regulator
    # cannot sink current, input injection raises VDD, including at OFF.
    supply_capacitance=100e-9
    one_volt_charge=supply_capacitance*1.0
    seconds_to_rail_rise=one_volt_charge/injected[(20.0,0.0)]
    assert 0<seconds_to_rail_rise<0.001
    # Real R1904 is a passive 4k7 bleeder, not a qualified power-off
    # rail clamp: model diode as fixed 0.7V (NOT guaranteed PVT).
    # For a floating lab 5V rail with only 4k7 DC load, solve
    # (Vin - Vfd - Vrail)/100k = Vrail/4k7, with off regulator = open.
    r_bleeder=4700
    vfd_assumed=0.7
    for vin in (12.0,20.0,40.0,200.0):
        vrail=max(0,(vin-vfd_assumed)*r_bleeder/(rseries+r_bleeder))
        injection=max(0,(vin-vfd_assumed-vrail)/rseries)
        pbleeder=vrail*vrail/r_bleeder
        assert math.isclose(injection,vrail/r_bleeder,rel_tol=1e-12)
        if vin==20.0:
            assert vrail<1.0
            assert pbleeder<0.0003
        if vin==200.0:
            assert vrail>5.0 # rail overvoltage remains, NOT protected
            assert pbleeder>0.01
    nominal_bleeder_current=5.0/r_bleeder
    nominal_bleeder_power=25/r_bleeder
    assert 0.001<nominal_bleeder_current<0.0011
    assert nominal_bleeder_power<0.01
    # C1901 has 100nF and R1904 nominal tau 0.47ms. The diode and
    # DC source may still exceed absolute maximum at other faults.
    assert math.isclose(r_bleeder*supply_capacitance,0.00047,rel_tol=1e-12)
    print("MCP6002_HIGHZ_R1904_RAIL_BLEEDER_CANDIDATE",{
        "bleeder_ohm":r_bleeder,
        "VDD5_bleeder_A":round(nominal_bleeder_current,8),
        "VDD5_bleeder_W":round(nominal_bleeder_power,7),
        "VDDoff_Vin20V_model_rail_V":round((20-vfd_assumed)*r_bleeder/(rseries+r_bleeder),7),
        "VDDoff_Vin200V_model_rail_V":round((200-vfd_assumed)*r_bleeder/(rseries+r_bleeder),7),
        "regulator_or_rail_sink_qualified":False,
        "abs_max_fault_stress_qualified":False,
        "no_fab":True},flush=True)
    # Illustrative 25nA/20V/25C 1N4148 max reverse leakage from a
    # vendor data sheet (not MCP6002 bias!). Does not certify leak at
    # 5V, high temperatures or all manufacturer MPNs.
    assumed_diode_reverse_leakage=25e-9
    connected_leakage_err=assumed_diode_reverse_leakage*r_thevenin
    open_leakage_err=assumed_diode_reverse_leakage*rbias
    assert connected_leakage_err>0.003
    assert open_leakage_err>0.5
    print("MCP6002_HIGHZ_D1901_UPPER_DIODE_CANDIDATE_UNQUALIFIED",
          {"assumed_Vf_V":assumed_vf,
           "upper_diode_current_A":{str(k):round(v,9) for k,v in injected.items()},
           "unpowered_1V_rail_rise_s_if_no_sink":round(seconds_to_rail_rise,7),
           "illustrative_25nA_reverse_leak_connected_V":round(connected_leakage_err,7),
           "illustrative_25nA_reverse_leak_open_V":round(open_leakage_err,4),
           "external_upper_diode_present":True,
           "rail_sink_backfeed_or_leakage_qualified":False,
           "no_fab_no_power_off_qualification":True},flush=True)
    # MCP6002 DS-20001733L: data-sheet Vos up to +/-4.5mV,
    # Ibias example 1pA at 25C, 19pA at 85C, 1100pA at 125C.
    # Bias examples are not guaranteed maxima; temperature qualification
    # would require device-specific guaranteed limits and measurements.
    # Distinguish connected 47k detector from an OPEN connector. Unlike
    # the floating case, the detector shunts the 22M bias network.
    vos_max=0.0045
    bias_examples={25:1e-12,85:19e-12,125:1100e-12}
    low_level=0.1
    results={}
    for temp,ib in bias_examples.items():
        rth_connected=1/(1/rbias+1/(rdet+rseries))
        rth_open=rbias
        node_connected=low_level*rbias/(rbias+rdet+rseries)
        input_shift_connected=ib*rth_connected
        input_shift_open=ib*rth_open
        worst_output_error_abs=abs(low_level-node_connected)+vos_max+input_shift_connected
        worst_output_error_frac=worst_output_error_abs/low_level
        results[temp]={"bias_A_example":ib,
                       "connected_bias_shift_V":round(input_shift_connected,9),
                       "open_bias_shift_V":round(input_shift_open,9),
                       "worst_signed_offset_error_fraction":round(worst_output_error_frac,6)}
        assert input_shift_connected<input_shift_open
        # The 1% envelope specification is NOT certified at 100mV:
        # 4.5mV maximum data-sheet offset alone consumes 4.5%.
        assert worst_output_error_frac>0.01
    assert math.isclose(results[125]["open_bias_shift_V"],0.0242,rel_tol=1e-9)
    # The nominal 1% loading check above excludes offset and leakage.
    print("MCP6002_HIGHZ_PVT_UNQUALIFIED",results,
          "VOS_MAX_V",vos_max,
          "reference","Microchip DS-20001733L; 1/19/1100pA are example temperature figures, not guaranteed maxima",
          "1pct_accuracy_at_100mV",False,
          "ESD_OVP_unpowered_qualified",False,flush=True)
    print("MCP6002_HIGHZ_NATIVE",{"components":len(REFS),"nets":len(nets),
          "pins":28,"R_BIAS":rbias,"R_SERIES":rseries,"theoretical_R47k_load_loss_fraction":round(loss,7),
          "vendor_pinout_MCP6002_PDIP8":"1=OUTA 2=-A 3=+A 4=VSS 5=+B 6=-B 7=OUTB 8=VDD",
          "unqualified_input_ESD_OVP":True,
          "actual_RX_AGC_or_meter_driver":False},flush=True)
    print("PASS_KICAD9_MCP6002_PDIP8_THT_HIGHZ_BUFFER_ERC0_PINS28_LAB_ONLY_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
