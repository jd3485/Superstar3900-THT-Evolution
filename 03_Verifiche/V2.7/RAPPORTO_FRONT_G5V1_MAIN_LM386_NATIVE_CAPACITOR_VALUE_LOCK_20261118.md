# FRONT six-pin G5V-1 mute / MAIN LM386 native capacitor-and-solver lock — 18 Nov 2026

PR [#354](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/354) **MERGED** on main `a5043334dd5ce458939ed000242f16438b980f85` from head `007760298d64c10f2926598b6cf49cd01e0d37a4`, CI run #44288450896 FAST/FULL/Required **3/3 SUCCESS**. That revision added native resistor instance-to-model verification.

This revision extends the SAME native FULL regression `03_Verifiche/V2.7/verify_front_g5v1_sixpin_ac_model_component_values_native.py`. The real KiCad9 MAIN audio netlist must show C1201 pin 1 on AUDIO_IN and pin 2 on PRE_IN, with R1201 pin 1 on PRE_IN, pin 2 and LM386 U1201 pin 3 on AMP_IN. Component instance C1201 (not library symbol or string elsewhere) must be `100nF_50V_INPUT` and its parsed SI capacitance must match the `100e-9 F` assumption across all three existing independent AC models; the existing R1901/R1902/R1201 instance checks remain mandatory. The parser rejects unknown or malformed capacitance formats; small floating point rounding does not mask meaningful changes.

Scope of claims: schematic and model parameter consistency, not actual capacitor capacitance, tolerance, voltage derating, LM386 input impedance across frequency, electromagnetic susceptibility or PCB DRC. Physical front relay and #27/#292 remain unqualified/open. No FAB, TX, battery, vehicle.
