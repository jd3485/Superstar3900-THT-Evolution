# V1.7 — Vero sesto foglio KiCad nativo THT per ingresso 13,8 V (CANDIDATO)
Data: 10/11 novembre 2026. Si conserva intatto lo storico THT V0.1–V1.6 e non si tocca SMD.

## Componenti con pin e topologia reale
`04_KiCad/V1.7/PLL_RX_HIERARCHICAL_MASTER_V1.7.kicad_sch` contiene il sesto foglio `INPUT_FUSE_REVERSE_TVS_V1.7.kicad_sch`. `J701 pin1` è il nuovo ingresso +13V8_RAW, pin2 massa. **F701 Littelfuse 0251.500MXL**, 500mA *fast-acting* axial candidate, pin1 ingresso raw, pin2 `FUSED_RAW`. **D701 Vishay 1N5819** Schottky DO-41: anodo pin2 `FUSED_RAW`, catodo pin1 `+13V8_PROTECTED` — blocco candidato contro inversione DC. **D702 ST P6KE20CA** bidirezionale DO-15: pin1 `FUSED_RAW`, pin2 GND, soppressione transitoria a monte dello Schottky. **PWR701** è solo flag ERC, non un circuito power-good.

Due interfacce gerarchiche reali: `+13V8_PROTECTED` e `GND` con sheet pins e hierarchical labels e wire nel root; il child precedente `POWER5_DISTRIBUTION` U601 ora riceve la tensione solo dal nuovo ramo. Rimossi **J601** (header di laboratorio che avrebbe permesso di aggirare le protezioni) e il vecchio PWR601 ERC-only nella revisione V1.7, preservando i componenti effettivi. Restano header di test sui rami a 5 V: non devono essere popolati/collegati a sorgenti esterne in una PCB finale. Il layout è di laboratorio e non può essere considerato vehicle safe.

## Vendor evidence (THT solo)
- Littelfuse PICO II 251 0251.500MXL, **0,5 A**, axial THT, *fast-blow*, 125 V, resistenza nominale a freddo circa **0,302 Ω** da catalogo distributore: https://www.digikey.it/en/products/detail/littelfuse-inc/0251-500MXL/700707 — footprint **VUOTO**. È un candidato, non fusibile validato per corrente totale della futura radio, picco, I²t, corto in ingresso, holder, capacità interruttiva nell'impianto reale.
- Vishay **1N5819**, 1A, 40V max reverse, DO-41, Vf circa 0,60V alla corrente di riferimento: https://www.vishay.com/docs/88525/1n5817.pdf ; pin K1/A2 coerenti al footprint KiCad 9 `Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal`.
- ST **P6KE20CA** bidirezionale axial DO-15, VRWM **17,1 V**; breakdown 19–21 V; clamp max **27,7 V solo al picco d'impulso specificato**, 600W per forma 10/1000µs: https://www.st.com/resource/en/datasheet/p6ke12ca.pdf e https://diotec.com/en/product/P6KE20CA.html. Footprint **VUOTO** fino a verifica lead pitch, body e MPN effettivo.
- Script `screen_input_protection_v17.py` riporta 12 scenari puramente aritmetici ingresso 11/13,8/15,5V e 0,05–0,4A, assumendo Vf=0,6V e Rfuse=0,302Ω; non simula energia, termica, fuse opening o surge.

## Fondamentale: cosa NON protegge
- **La TVS NON garantisce lo spegnimento con sovratensione DC prolungata**: per 16–19V può non clampare e oltre breakdown può scaldare/distruggersi o aprire il fusibile in modo non controllato. Non si dichiara OVP.
- **Nessuna qualifica automotive**, ISO 7637, reverse battery -24V, cold crank, load dump, EMI, fault current / I²t, cross-connection, cablaggio, TVS termica, fuse interrupting coordination; nessun test fisico.
- Output al 7805 non validato termicamente: studio V1.5 già segnala 4/12 scenari termici a rischio. Oltre al pilot 5V rimangono assenti boost 27V/regolazione 20V VTUNE, power-good/mute, fail-closed, controller N, RF/IF/audio e PCB. Nessuna frequenza RF o locked PLL dimostrata.
- Nessun footprint definitivo per F701/D702, nessuna KiCad PCB, nessun DRC, Gerber e prova reale. **NO FAB / NO TX; NON collegare a batteria/veicolo.**

## Gate CAD
CI KiCad 9 per root+5 child: ERC zero senza waiver, export netlist 52 baseline V1.6 vs **54 attese V1.7** per due sole reti nuove raw/fused, eliminazione intenzionale dei 2 pin J601, conservazione integrale del resto; verifiche pin-to-net D701 A2/K1, TVS FUSED_RAW/GND, 5V rail e VTUNE/LO. SVG 6 pagine e libreria simboli nativa. **PENDING prima della prima esecuzione GitHub Actions.**
