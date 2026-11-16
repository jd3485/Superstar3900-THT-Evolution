# V2.7 — due interruttori PMOS anti-serie completi in cascata

**16 novembre 2026 — candidato KiCad9 isolato, NON circuito di sicurezza qualificato.** La V2.6 MAIN e FRONT restano invariati. La PR #328 dimostra che due soli PMOS anti-serie con gate indipendenti, sotto un guasto C–E SHORT singolo, possono consentire un percorso direzionale via il body diode del MOSFET OFF. Questo candidato cambia fisicamente l'architettura, non soltanto il test.

## Schematica THT nativa proposta

File `04_KiCad/V2.7_DRAFT/MAIN_SECONDARY_OVP_TWO_COMPLETE_STAGES/MAIN_SECONDARY_OVP_TWO_COMPLETE_STAGES_LAB_V2_7_DRAFT.kicad_sch`. Due moduli uguali, ciascuno con coppia IRF9540NPBF anti-serie (source comuni in ciascun modulo), resistore source-gate 47k, due Zener Microchip 1N4106-1 in parallelo source-gate, resistor 10k verso NPN onsemi KSP42BU, 4k7 base, 100k pulldown base e ingresso di ENABLE **esterno**. Due stadi in serie:

- Primo interruttore: `J2101/1` → `Q804/Q805` → `SECONDARY_OUT_DRAIN_LAB` → `J2102/1`. Source interno `FLOATING_COMMON_SOURCE_LAB`, gate `COMMON_GATE_LAB`, sink Q806.
- Secondo interruttore: `J2111/1` sullo stesso `SECONDARY_OUT_DRAIN_LAB` → `Q814/Q815` → `FINAL_SECONDARY_OUT_LAB` → `J2112/1`. Source interno **separato** `FLOATING_SOURCE_B_LAB`, gate `COMMON_GATE_B_LAB`, sink Q816. Ogni stage ha 2× P-MOS, 2× clamp, 1× driver BJT.
- I connettori di laboratorio aggiuntivi NON indicano isolamento galvanico né power-good: `LAB_RETURN_ONLY` resta comune. Nessuna rail 5V, supervisione UV/OV, VREF indipendenti o controllo dei fault BJT viene generata.

**Contratto nativo atteso:** 24 componenti THT, **54 pin reali in 14 reti** verificate senza fusione delle due source. ERC zero warning/error, allegare esito CI reale, non presumerlo dal codice.

## Analisi topologica con guasti sintetici

Su grafo diretto ideale di diodi body P-MOS (drain→source) e canali bidirezionali solo quando entrambi i gate del rispettivo stadio sono comandati ON, **un interruttore completo OFF interrompe la raggiungibilità INPUT↔OUTPUT in entrambe le direzioni**. Se il driver Q806 è guasto in C–E SHORT, accende *entrambi* i gate del primo stadio, ma il secondo stadio interamente OFF interrompe ancora il percorso. Simmetricamente Q816 SHORT con primo OFF. 16 stati booleiani ENABLE_A/B e C–E SHORT_A/B, incluso guasto singolo con ENABLE entrambi OFF.

Questo **non** risolve MOSFET D–S SHORT, guasti comuni in ritorno/cablaggio, sovratensioni, startup e brownout, Zener SHORT/OPEN, supply, driver collasso, SOA termica, isolamento tab TO-220, corrente di carico, valori OEM reali o backfeed. Un body diode in conduzione richiede polarizzazione e non è un corto ideale. Il test non è una prova elettrica di fail-safety.

**ISSUE #27 ancora APERTA; nessuna PCB, NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
