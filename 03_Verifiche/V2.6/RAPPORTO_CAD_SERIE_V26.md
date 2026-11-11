# V2.6 — Revisione candidata con sette schemi nativi KiCad 9

**Precisazione successiva alla PR #31 (audit D803):** D803 onsemi 1N4742A 12 V / 1 W è già collegato al gate/source Q801 in V2.6. L'avvertimento teorico di |VGS| >20 V a VIN 48 V per il solo partitore R1008/R1009 corrisponde al **guasto D803 aperto**. L'audit nativo [43081722718](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43081722718) verifica l'orientamento reale del diodo. Il suo comportamento reale a pochi mA e i transitori restano non qualificati. Consultare `03_Verifiche/V2.6/RAPPORTO_D803_GATE_CLAMP.md`. **Non dedurre un via libera a 48 V.**

Questa revisione deriva dalla V2.5 e preserva le revisioni precedenti. Master `04_KiCad/V2.6/PLL_RX_HIERARCHICAL_MASTER_V2.6.kicad_sch`. **La V2.6 non è qualificata e non autorizza fabbricazione.**

## Circuito modificato
- U801/7 (comparatore B UVLO): da CMP_OUT a **UVLO_OC**.
- Q802/1 emettitore: da GND a **SERIES_MID**.
- Q803: nuovo 2N3904 onsemi TO-92 THT, 1 emettitore→GND, 2 base→UVLO_BASE, 3 collettore→SERIES_MID.
- R1014 4,7 kΩ THT tra VREF2V5 e UVLO_OC; R1015 470 kΩ THT tra UVLO_OC e UVLO_SENSE.
- R1016 22 kΩ THT tra UVLO_OC e UVLO_BASE; R1017 100 kΩ THT tra UVLO_BASE e GND.
- U801/1 rimane su CMP_OUT, conservando R1005 di isteresi OVP. **Non** è presente D807 Schottky.

Q802 e Q803 sono in serie nel percorso gate-sink del MOSFET, così l'abilitazione nominale richiede due consensi indipendenti. La retroazione UVLO è separata da quella OVP. Questa topologia è **solo candidata**, non dimostra fail-safe su guasto singolo.

## Verifiche obbligatorie sulla nuova HEAD
1. `node 04_KiCad/V2.6/genera_uvlo_serie_v26.js --check` deve confermare 7 schemi e 3 librerie bit-exact.
2. KiCad 9 ERC su tutta la gerarchia con zero violazioni, senza waiver.
3. Netlist native V2.5/V2.6 e `verify_kicad_v26.py`: 73→76 gruppi elettrici previsti, 133→138 componenti, tutte impronte THT, solo U801/7 e Q802/1 migrati; reti legacy conservate.
4. Export nativo di almeno 7 SVG; regressioni precedenti e analisi Python.
5. CI consolidata verde sul commit finale. **Non dichiarare superati i gate prima di controllare i log.**

## Limiti di sicurezza
Onsemi 2N3904: pin 1 emettitore, 2 base, 3 collettore, VCEO max 40 V. TI LM393-N: Vs max 36 V. Questa revisione non affronta in modo qualificato 48 V/load-dump, reverse battery, VGS MOSFET in guasto, limiti di common-mode, riferimento TL431 assente o errato, saturazione BJT alta/bassa temperatura, circuito power-good/mute indipendente, corrente e termica TVS/fusibile, startup e disturbi. Soglie nominali UVLO 11,50 e 11,67 V sono soltanto risultati idealizzati. Occorre validazione vendor e hardware.

Fonti: https://www.onsemi.com/download/data-sheet/pdf/2n3904-d.pdf ; https://www.ti.com/product/LM393-N .

Stato: PR #28 Draft, issue #27 aperta, main V2.3; nessuna PCB, nessun DRC PCB, nessun Gerber/ordine, nessun TX. **NO FAB / NO TX / NO BATTERIA / VEICOLO.**
