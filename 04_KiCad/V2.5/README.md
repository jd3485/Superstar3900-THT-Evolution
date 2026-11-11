# V2.5 KiCad9: LM393B UVLO window candidate on seven real schematics

U801 pin5 now UVLO_SENSE instead of GND; pin6 remains VREF2V5; pin7 now CMP_OUT (wired-AND with pin1). R1012 Yageo 36k 1%, R1013 Yageo 10k 1% form raw VIN divider, nominal UVLO 11.5V. R1001 Vishay PR01 1k8 supports the TL431 bias at lower VIN in an idealized model. Source V2.4 kept unchanged.

NOT fail-closed for all single faults; no hysteresis/vendor SPICE/powergood/mute; footprint and thermals unqualified. NO FAB / NO TX / NO BATTERY / VEHICLE.
