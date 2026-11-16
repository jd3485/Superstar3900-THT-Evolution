# Correzione contratto audio MAIN/FRONT: impedire bypass del relè mute

Data 16 novembre 2026. Baseline `main` PR #288 integrata, master FRONT KiCad9 5 sheet, 22 reti, 71 pin, quattro link gerarchici.

## Difetto d'integrazione rilevato

Il precedente schema cavo `INTERBOARD_AUDIO_HARNESS_V2_7_DRAFT.kicad_sch` rappresentava J2401 come `FRONT_J1302`, cioè la presa **a monte** del relè K1901 (volume wiper). Se questa assegnazione fosse stata usata per collegare direttamente J1302 al MAIN J1202, il relè mute non sarebbe stato sul percorso verso l'amplificatore: una modalità di guasto funzionale importante.

## Contratto corretto (candidato elettrico, non cablaggio fabbricabile)

`J2401/1` simula **FRONT J1902/1**, rete `AMP_INPUT_MUTED` (uscita dopo K1901 e R1902): `J2402/1` simula **MAIN J1202/1**, rete `AUDIO_IN`.

`J2401/2` simula **FRONT J1902/2**, rete `AF_GND`: `J2402/2` simula **MAIN J1202/2**, rete `GND` del prototipo audio.

**J1302** resta un'interfaccia locale tra modulo volume e ingresso del relè mute; non è l'uscita verso MAIN. `verify_interboard_audio_contract_native.py` esporta tre netlist native indipendenti e il master FRONT, e impone che J1902/1 e J1302/1 **non** condividano la stessa rete mentre i ritorni AF_GND condividono lo stesso nodo FRONT. Inoltre verifica i due conduttori e quattro terminali KiCad9 con ERC0 del cavo.

## Limiti per il prototipo

La sigla `AMP_INPUT_MUTED` descrive soltanto il punto **post-relè**; **non prova** che K1901 sia un MPN OEM attivo, che NC/NO rispettino un'assegnazione pin fisica, né che un guasto di contatto NO saldato mantenga il mute. Il circuito ha condizioni di fault note per dual NPN e AF_GND interrotta. J2401/J2402 sono astrazioni con pin header maschi generici, NON coppie meccaniche approvate: schermatura, polarizzazione, ritorni, ESD, EMI, pinout e loop di massa MAIN/FRONT ancora da validare. Non è un circuito di sicurezza e non va connesso a hardware alimentato.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**