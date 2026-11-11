# V2.6 — Q802/Q803: un corto singolo elude l'interblocco OVP/UVLO

**Esito progettuale rilevante:** lo stadio Q802 (2N3904 superiore) + Q803 (2N3904 inferiore), in **serie** da GATE_SINK verso GND, implementa una logica di consenso AND **solo con entrambi i transistor funzionanti**. Non soddisfa il requisito di mantenere OFF con **qualsiasi singolo cortocircuito collettore-emettitore**. Questo documento non modifica lo schema; qualifica esplicitamente l'insufficienza della topologia candidata.

## Pin-net KiCad 9 da verificare obbligatoriamente
- R1009 pin2 = Q802 pin3 (C): **GATE_SINK**; Q802 pin1 (E) = Q803 pin3 (C): **SERIES_MID**.
- Q803 pin1 (E) = U801 pin4 = **GND**.
- Q802 pin2 (B) = R1007 pin2, consenso OVP; Q803 pin2 (B) = R1016 pin2, consenso UVLO.
- R1009 pin1 = D803 pin2 = **PFET_GATE**; D803 pin1 = Q801 pin3 = source alta (**FUSED_RAW**).
- Il test `03_Verifiche/V2.6/audit_q802_q803_single_fault_v26.py` controlla **20 casi logici** e verifica queste connessioni da **netlist nativa KiCad9 a 76 reti**. Una semplice tabella o un test di rete ideale non è una simulazione elettrica o prova reale.

## Tavola di pericolosità logica
| OVP consente? | UVLO consente? | Entrambi sani | Q802 C-E in corto | Q803 C-E in corto |
|---|---|---|---|---|
| NO | NO | sink OFF | sink OFF | sink OFF |
| NO | SÌ | sink OFF | **sink ON, OVP bypassata** | sink OFF |
| SÌ | NO | sink OFF | sink OFF | **sink ON, UVLO bypassata** |
| SÌ | SÌ | sink ON | sink ON | sink ON |

Un singolo transistor guasto C-E in corto **non è provato** fail-safe. Le modalità C-E aperto bloccano il sink *nel solo modello binario*; non sono state validate dispersione, rottura per VCEO 40V, effetti capacitivi, leakage, drive di base, avvio, transitori e FET switching. Il MOSFET Q801 va comunque analizzato in tutte le condizioni di tensione e guasto D803.

## Decisione ingegneristica e blocchi
1. **Non dichiarare Q802+Q803 una protezione ridondante a guasto singolo**; solo un interblocco di funzione nominale (AND).
2. Prima di considerare la main PCB pronta, progettare un'architettura **power-good + mute / enable indipendente**, che non dipenda dall'identico percorso di sink a due NPN; separare comando e protezione così un corto di uno dei driver non abiliti inavvertitamente la radio.
3. Considerare separatamente guasti singoli a D806, TL431, D803, Q801, Q802, Q803, rail LM393, più reverse/OVP/Brownout, e verificare con modelli vendor e test di banco. Una singola valutazione binaria non prova la sicurezza del circuito fisico.
4. **Nessuna modifica agli schemi o al master KiCad V2.6.** Il blocco reale resta [Issue #27](https://github.com/jd3485/Superstar3900-THT-Evolution/issues/27). ADR-001 a due PCB rimane il requisito definitivo.

**NO FAB / NO TX / NO BATTERIA/VEICOLO**. No PCB reali, DRC o qualifica hardware.  
Datasheet onsemi 2N3904: https://www.onsemi.com/download/data-sheet/pdf/2n3904-d.pdf .
