# V2.4 KiCad 9 — candidate LM393 supply guard on seven-sheet RX/PLL
Native 7 KiCad sheets. See 03_Verifiche/V2.4/RAPPORTO_OVP_GUARD_V2.4.md.
Input power: D804 K1 -> OVP_PRECLAMP -> R1011 680R/2W -> OVP_CTL_VCC;
D806 15V zener cathode VCC anode GND; R1002 raw sense FUSED_RAW.
No added flags, no gate redesign or approved UVLO/mute. Baseline V2.3 preserved.
**NOT A SAFETY QUALIFICATION; NO FAB / NO TX / NO BATTERY / NO VEHICLE.**
