# V2.4 seven-sheet KiCad9 — LM393 supervisor supply guard CANDIDATE
D804 cathode -> OVP_PRECLAMP -> R1011 Vishay PR03000208200JAC00 820R/3W PR03 Cu-lead -> OVP_CTL_VCC.
D806 Diotec 1N5352B Zener 15V/5W DO-201 from OVP_CTL_VCC (cathode) to GND (anode).
R1002 senses FUSED_RAW before series drop. No other legacy pin-net migration.
CAD footprint candidates: resistor DIN0617 L17/D6 P25.40 and diode DO-201 P15.24.
V2.4 report at 03_Verifiche/V2.4/RAPPORTO_OVP_GUARD_V2.4.md identifies unresolved derating, UVLO, fail-closed, reverse, source energy and package verification.
NO FAB / NO TX / NO BATTERY / NO VEHICLE. Nothing is hardware safety-qualified.
