# V1.6 — reale integrazione KiCad9 dei rail 5V nel RX PLL THT
Data 10 novembre 2026, repository indipendente THT.

**Nuova struttura**: root `04_KiCad/V1.6/PLL_RX_HIERARCHICAL_MASTER_V1.6.kicad_sch` e quattro sottoschemi nativi: PLL digitale U401/U402; filtro RC/LM358; VCO Colpitts Q501/Q502 con buffer SN74AC14N; alimentazione U601 L7805CV TO-220. Il foglio V1.5 è stato promosso a child, mantenendo gli stessi componenti e le resistenze serie 1Ω.

**Quattro reti condivise** tramite pin/hierarchical label veri: GND fisicamente cablato nel root, e `+5V_PLL`, `VCC_VCO5`, `VCC_BUF5` su brevi wire e **label locali esclusivamente sul foglio radice** (non global label che scavalcano la gerarchia). Le altre reti originali NON devono fondersi. Attesi 50+6−4 = **52 gruppi elettrici** nella netlist KiCad.

**Gate automatizzato**: generazione JS bit-per-bit dai 5 schemi KiCad originali V1.4/V1.5, ERC KiCad9 su 5 pagine senza waivers, export SVG 5 pagine, 3 netlist native V1.4/V1.5/V1.6, verifica di conservazione di **tutti** i gruppi pin delle 50+6 reti e solo i quattro collegamenti intenzionali. Controlla inoltre ingresso 13.8V distinto, uscita +5V_REG distinta dai rami, VTUNE e LO precedenti invariati.

**Al primo commit: CI PENDING.** Non è una prova di regolazione 5 V né RF o elettrica di veicolo. `+13V8_PROTECTED` è solo un nome di porta esterna e **NON un fusibile/polarity/TVS realmente progettato**. Il budget termico V1.5 ha segnalato 4/12 scenari di rischio con carichi ipotizzati; correnti reali, dissipatore, ripple, power sequencing non conosciuti. Boost 20V per VTUNE, powergood/mute e PCB non esistono. Il VCO Colpitts/AC14 non è qualificato per lock, phase margin e ricezione; L501 footprint non selezionato. NO FAB / NO TX.

## ERC primo run e correzione senza waivers
Il primo native KiCad9 run [42917594372](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42917594372) ha individuato **1 violazione reale `pin_to_pin`**: due flag di alimentazione tipo `power_out` sulla GND comune, `PWR402` originale PLL e `PWR602` importato dal vecchio laboratorio 5V standalone. Rimosso **solo PWR602** nel child V1.6 (simbolo ERC-only `on_board no`, wire e label isolati); mantiene PWR402 come fonte ERC già verificata. La connessione di massa fisica e i componenti V1.5 invariati. Nessun waiver, rerun ERC/netlist obbligatorio prima di dichiarare PASS.
