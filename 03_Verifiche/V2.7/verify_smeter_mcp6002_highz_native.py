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
REFS={"U1901","J1901","J1902","J1903","R1901","R1902","R1903","R1904","C1901","C1902","D1901","D1902","D1903"}
EXPECTED={
 "AM_ENV_DC_BENCH":{("J1901","1"),("R1903","1")},
 "AM_ENV_AFTER_R1903":{("R1903","2"),("U1901","3"),("R1901","1"),("C1902","1"),("D1901","2"),("D1903","1")},
 "SMBUF_BENCH_GND":{("J1901","2"),("J1902","2"),("J1903","2"),("U1901","4"),("U1901","5"),("R1901","2"),("C1901","2"),("C1902","2"),("R1904","2"),("D1902","2"),("D1903","2")},
 "VLAB5_BUFFER":{("J1903","1"),("U1901","8"),("C1901","1"),("D1901","1"),("R1904","1"),("D1902","1")},
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
    assert '(property "Value" "120k_1PCT_1W_INPUT_FAULT_LIMIT_MARGIN_CANDIDATE"' in s
    assert '(property "Footprint" "Resistor_THT:R_Axial_DIN0411_L9.9mm_D3.6mm_P12.70mm_Horizontal" (at 81.28 213.36 0)' in s
    assert s.count('(property "Footprint" "Capacitor_THT:')>=2
    assert '(property "Value" "1nF_50V_C0G_NP0_RF_FILTER_THT_CANDIDATE"' in s
    assert s.count('(property "Footprint" "Connector_PinHeader_2.54mm:')>=3
    # KiCad9 standard DO-35 footprint pad 1 is the K-marked cathode;
    # pad 2 is the anode. This MUST match the custom embedded symbol,
    # otherwise board build would reverse both clamps even if ERC=0.
    diode_pin_k='(name "K" (effects (font (size 1 1)))) (number "1"'
    diode_pin_a='(name "A" (effects (font (size 1 1)))) (number "2"'
    assert diode_pin_k in s and diode_pin_a in s
    assert diode_pin_k in library and diode_pin_a in library
    assert '(property "Footprint" "Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal"' in s
    assert s.count('(property "Footprint" "Diode_THT:')>=3
    assert '(property "Value" "1N4148_DO35_LOWER_NEGATIVE_CLAMP_CANDIDATE_UNQUALIFIED"' in s
    assert '(property "Value" "BZX55C5V6_DO35_ZENER_5V6_RAIL_CANDIDATE_UNQUALIFIED"' in s
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
    assert sum(len(members) for members in nets.values())==32
    # 22M passive shunt in parallel with idealized 47k detector: only
    # predicts nominal static DC loading, NOT opamp input leakage or PVT.
    rdet=47000
    rbias=22000000
    rseries=120000
    # The 120k series resistance lies upstream of the 22M input-bias
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
    assert 900<f_3db<1000
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
    # 200V hypothetical *sustained* event is beyond the original
    # 100k/0.25W thermal rating but below the NEW 1W bench candidate.
    # This still does NOT qualify V(max), mounting or temperature.
    severe_negative=-200.0
    severe_current=abs(severe_negative-assumed_vclamp)/rseries
    severe_power=(severe_negative-assumed_vclamp)**2/rseries
    assert severe_current<ds_input_abs_current
    assert 0.25<severe_power<1.0
    # D1903 is now an EXTERNAL 1N4148 DO35 low-side clamp with
    # cathode pin1 on analog input and anode pin2 on VSS/GND.
    # Unlike the earlier illustrative -0.3V internal-diode assumption,
    # use example -0.7V external junction; not a Vf guarantee at PVT.
    external_vclamp=-0.7
    neg_results={}
    for source_v in (-12.0,-20.0,-40.0,-200.0):
        isink=max(0.0,(external_vclamp-source_v)/rseries)
        p_series=isink*isink*rseries
        neg_results[source_v]=(round(isink*1000,6),round(p_series,6))
        if source_v==-20.0:
            assert 0.00015<isink<0.00017 and p_series<0.005
        if source_v==-200.0:
            assert 0.0016<isink<ds_input_abs_current
            assert 0.25<p_series<1.0 # original 0.25W exceeded; 1W nominally holds
    # A 1W footprint is a nominal power capability, NOT a certified
    # resistor MPN, working voltage, power derating or shock tolerance.
    rated_power=1.0
    original_power=0.25
    nominal_200v_power=((200-0.7)**2)/rseries
    worst_200v_1pct_power=((200-0.2)**2)/(rseries*0.99)
    worst_200v_1pct_current=(200-0.2)/(rseries*0.99)
    assert original_power<nominal_200v_power<rated_power
    assert worst_200v_1pct_power<rated_power
    # 120k/1% nominal model places -200V current below the 2mA
    # absolute stress bound, NOT a normal-use specification.
    # Higher faults, diode PVT and resistor pulse ratings remain unsafe.
    assert worst_200v_1pct_current<ds_input_abs_current
    severe_400v_power=((400-0.7)**2)/rseries
    assert severe_400v_power>rated_power
    print("MCP6002_HIGHZ_R1903_1W_THT_DERATING_STILL_UNQUALIFIED",{
        "R1903_nominal_ohm":rseries,
        "R1903_nominal_rating_W":rated_power,
        "R1903_200V_nominal_W":round(nominal_200v_power,6),
        "R1903_200V_Rminus1pct_Vf0P2_W":round(worst_200v_1pct_power,6),
        "input_current_200V_Rminus1pct_Vf0P2_mA":round(worst_200v_1pct_current*1000,6),
        "input_abs_current_bound_mA":ds_input_abs_current*1000,
        "R1903_400V_nominal_W":round(severe_400v_power,6),
        "temperature_derating_voltage_MPN_ESD_qualified":False,
        "no_fab":True},flush=True)
    # Margin must account for 1% tolerance and low assumed clamp Vf.
    # Source short-circuit = 200V is an illustrative DC bench event.
    rmin=rseries*0.99
    fault_v=200.0
    vf_floor_example=0.2
    icorner=(fault_v-vf_floor_example)/rmin
    pcorner=((fault_v-vf_floor_example)**2)/rmin
    imargin=ds_input_abs_current-icorner
    assert 0<imargin<0.0004
    assert pcorner<1.0
    # Faults above 240V DC still violate the 2mA ceiling in this
    # model. Rate/duration, physical resistor MPN, PCB and diode
    # leakage/thermal effects remain entirely unqualified.
    max_model_fault_for_2mA=vf_floor_example+ds_input_abs_current*rmin
    assert 230<max_model_fault_for_2mA<240
    assert (250-vf_floor_example)/rmin>ds_input_abs_current
    assert loss<0.01
    assert 900<f_3db<1000
    print("MCP6002_HIGHZ_R1903_120K_200V_STRESS_MARGIN_STILL_UNQUALIFIED",{
        "R1903_ohm":rseries,
        "worst_negative_200V_input_mA":round(icorner*1000,6),
        "margin_below_2mA_mA":round(imargin*1000,6),
        "R1903_worst_200V_W":round(pcorner,6),
        "fault_2mA_model_threshold_V":round(max_model_fault_for_2mA,6),
        "nominal_47k_source_loading_percent":round(loss*100,6),
        "RC_3dB_Hz":round(f_3db,4),
        "qualified_for_real_overvoltage_ESD_PVT":False,
        "no_fab":True},flush=True)
    # The external clamp does not eliminate internal ESD current share.
    # 25nA * 146kOhm is an illustrative DC error; high temperature
    # diode leakage and input operating range are NOT characterized.
    illustrative_leakage=25e-9
    assert illustrative_leakage*r_thevenin>0.003
    print("MCP6002_HIGHZ_D1903_LOWER_CLAMP_UNQUALIFIED",{
        "pin1":"K=AM_ENV_AFTER_R1903",
        "pin2":"A=SMBUF_BENCH_GND",
        "assumed_forward_clamp_V":external_vclamp,
        "negative_fault_source_V_to_mA_and_R1903_W":neg_results,
        "R1903_old_0P25W_survives_200V":False,
        "R1903_new_1W_nominal_power_below_rating_at_200V":True,
        "ESD_hot_temp_leakage_and_PVT_qualified":False,
        "no_fab":True},flush=True)
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
    # (Vin - Vfd - Vrail)/120k = Vrail/4k7, with off regulator = open.
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
    # Vishay BZX55C5V6 datasheet: VZ 5.2..6.0V guaranteed at IZT=5mA
    # and 25C. The 120k source cannot supply IZT=5mA for moderate
    # source faults. Therefore 5.6V is NOT a qualified clamp at e.g.
    # +20V or +200V: this is deliberately fail-closed.
    zener_izt=0.005
    zener_vmin_izt=5.2
    zener_vmax_izt=6.0
    def diode_current_if_rail(vin,vrail):
        return max(0.0,(vin-vfd_assumed-vrail)/rseries)
    for vin in (20.0,200.0):
        available=diode_current_if_rail(vin,zener_vmax_izt)
        assert available<zener_izt,(vin,available)
        # Even the total source current falls below the 5mA rated
        # test point: never infer Vz(125C) or transient performance.
    assumed_zener_voltage=5.6
    vin=200.0
    current_from_input=diode_current_if_rail(vin,assumed_zener_voltage)
    current_bleeder=assumed_zener_voltage/r_bleeder
    current_zener=current_from_input-current_bleeder
    assert 0<current_zener<zener_izt
    p_zener=current_zener*assumed_zener_voltage
    assert p_zener<0.005
    # At +20V, the 4k7 bleeder holds Vrail<1V even without Zener.
    # At +200V the 5.6V shunt MIGHT conduct, but its clamped voltage
    # is not specified at the actual ~0.8mA -> no electrical approval.
    print("MCP6002_HIGHZ_D1902_5V6_ZENER_LOW_CURRENT_UNQUALIFIED",{
        "diode_ref":"D1902",
        "VZ_datasheet_at_5mA_25C_V":(zener_vmin_izt,zener_vmax_izt),
        "source_possible_mA_at_200V_Vrail6V":round(diode_current_if_rail(200.0,6.0)*1000,6),
        "assumed_5V6_example_zener_mA_at_200V":round(current_zener*1000,6),
        "actual_zener_voltage_at_fault_current_guaranteed":False,
        "negative_fault_ESD_PVT_power_off_qualified":False,
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
          "pins":32,"R_BIAS":rbias,"R_SERIES":rseries,"theoretical_R47k_load_loss_fraction":round(loss,7),
          "vendor_pinout_MCP6002_PDIP8":"1=OUTA 2=-A 3=+A 4=VSS 5=+B 6=-B 7=OUTB 8=VDD",
          "unqualified_input_ESD_OVP":True,
          "actual_RX_AGC_or_meter_driver":False},flush=True)
    print("PASS_KICAD9_MCP6002_PDIP8_THT_HIGHZ_BUFFER_ERC0_PINS32_LAB_ONLY_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
