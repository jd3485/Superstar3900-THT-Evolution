# V2.4 — LM393 supply guard candidate revision: PR03 820R/3W + DO-201 15V/5W

Baseline is merged V2.3, seven real KiCad9 schematic sheets; PR #28 is DRAFT, not a qualified release.

## Real electrical change

Only the input/supervisor sheet changes from V2.3:
- D804 cathode pin 1 moves from OVP_CTL_VCC to OVP_PRECLAMP.
- R1011 Vishay PR03000208200JAC00, 820 ohm 3 W 5% copper-lead PR03 resistor, from OVP_PRECLAMP to OVP_CTL_VCC. The prior 680 ohm 2 W PR02 candidate had inadequate modeled derating margin.
- D806 Diotec 1N5352B, 15 V 5 W 5% DO-201 Zener, cathode pin1 to OVP_CTL_VCC and anode pin2 to GND. Replaces earlier 1N4744A 1 W DO-41 candidate.
- R1002 pin1 moves from clamped OVP_CTL_VCC to upstream FUSED_RAW so the OVP divider measures raw fused supply; pin2 stays SENSE_RAW.
- U801/U802/Q801/Q802 and every other legacy pin-net partition are unchanged; no invented PWR_FLAG and no new power-good/mute circuit.

These KiCad9 footprints are CANDIDATES, not qualified mechanical dimensions:
- Resistor_THT:R_Axial_DIN0617_L17.0mm_D6.0mm_P25.40mm_Horizontal for PR03 (actual lead form, drill, 16.7mm body and P70 board thermal still need samples).
- Diode_THT:D_DO-201_P15.24mm_Horizontal for the 1N5352B (real package and lead dimensions must be checked).
The new Zener is indicated active by Diotec but Diotec declares RoHS under exemption 7(a)-I and NOT lead-free: compliance review OPEN.

## Primary sources

- Vishay PR01/02/03 08-Jul-2025: https://www.vishay.com/docs/28729/pr010203.pdf (PR03 Cu-lead 3W P70, derating vs temperature; Cu vs FeCu 2.5W must not be conflated).
- Diotec 1N5352B: https://diotec.com/en/product/1N5352B.html (15V 5W DO-201, at Izt=75mA Vz=14.2..15.8V; NOT guaranteed at lower current).
- TI LM393-N: https://www.ti.com/product/LM393-N (max 36V supply; analog absolute limits require qualification).
- TI TL431: https://www.ti.com/lit/ds/symlink/tl431.pdf (minimum cathode current depends on suffix and conditions).
- Infineon IRF9540N: https://www.infineon.com/part/IRF9540N (VGS maximum +/-20V).

## 264-point idealized PVT screen, NOT a certified 48V supply

Models 0..48V VIN, 820R +/-5%, diode Vf 0.25..0.65V, LM393 Icc 0.5..1.0mA and three ASSUMED Zener clamp points (14.2, 15.0, 15.8V). The Zener limits are published at 75mA but the idealized modeled current is below that; no vendor dynamic I-V model is used.
Expected screening output: at 13.8V TL431 estimated cathode min 1.216mA; at 10V 0.303mA, therefore brownout unresolved. At ideal 48V clamp, worst R1011 loss about 1.445W and D806 about 0.576W. The PR03 Cu derating curve gives about 1.731W at 125C but only about 1.385W at 140C. This demonstrates a remaining high-temperature limit; the actual resistor ambient, lead thermal condition, Zener self heating and transients are unknown.

**Danger remains:** 48V sustained input NOT rated; if Zener opens or does not conduct, the supervisor may exceed component ratings; if it shorts, currents and state are not proven safe. Gate Q801/Q802 cannot be asserted fail-closed across faults; reverse polarity, F701 fuse / D702 TVS energy, load dump, power-good/mute and LM393 input pin protection all UNQUALIFIED. No vendor SPICE, no breadboard/prototype, no full PCB.

## Required checks

Run the optimized full GitHub CI on FINAL PR HEAD: native 7-sheet ERC zero violations, actual two netlists V2.3 72 groups to V2.4 73 groups, exact preservation except D804/1 and R1002/1, 131/131 THT footprint fields, 7 SVG, generator bit-exact and historical regressions. CI pass verifies CAD correctness, NOT hardware safety. Keep PR #28 draft until further qualification and review; V2.5 priorities are real UVLO, powergood/mute fail-closed, F701/D702 fault energy, supply envelope, nonideal devices/thermal and gate fault analysis. NO FAB / NO TX / NO BATTERY / NO VEHICLE.
