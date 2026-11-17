# Mechanical TO-220 mounting isolation: exhaustive conductive partitions (17 Nov 2026)

A real PCB and heatsink do **not** yet exist. As documented in issue #27, the IRF9540NPbF TO-220AB mounting tab is bonded to the drain, pin 2. The isolated KiCad9 two-stage lab has four physical transistors Q804/Q805/Q814/Q815 with drain nets respectively **IN/MID/MID/OUT**. Insulation is not shown or guaranteed by schematic ERC.

This revision extends the physical tab-contact hazard in merged PR #340 by examining the **Bell(4)=15** possible partitions of the four tabs into electrically conductive mounting groups. Each group means its tabs are hypothetically shorted by shared conductive mounting material; distinct groups remain isolated. For each partition, both stages' commanded states are evaluated (OFF/OFF, ON/OFF, OFF/ON, ON/ON): **60 native-net-anchored directed diode/connectivity scenarios**, not OEM device simulation.

**Result:** with both stages OFF, **7/15** mounting partitions bypass the IN↔OUT isolation in both graph directions. With only A or B ON, **10/15** each bypass; when both are ON, **15/15** conduct as intended by the idealized graph. When all mounting conductor groups contain only tabs from the **same drain net**, there is no such both-OFF bypass in this model. This is merely a necessary mechanical partition rule; it does not qualify dielectric isolation, mounting hole/fastener geometry, thermal interface pad withstand, leakage under humidity, arc clearance, heatsink electrical potential or fault energy.

New FULL test `03_Verifiche/V2.7/verify_to220_insulation_partition_native.py` exports actual KiCad9 netlists (24 THT / 54 pins / 14 nets) and checks each exact drain pin mapping, 15 unique partitions and all 60 ideal directed states. It independently reuses and expands the earlier contact-pair graph. The report documents this **engineering hazard**, not a PCB DRC or hardware proof. Issue #27 remains OPEN.

Parent PR #340 integrated on main `5b2581ba4f82d1f364e7642378896ecd2f6e10ab`, run #44120191088 FAST/FULL/Required all SUCCESS. New review requires its own CI on final head before any merge. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**.
