# V2.7 — Contratto di integrazione per secondo interruttore d'alimentazione sorvegliato (candidato, NON CAD)

**16 novembre 2026 — issue #27, fonte master MAIN KiCad9 V2.6, sicurezza non qualificata.**

## Punto di partenza verificato

Il master `04_KiCad/V2.6/PLL_RX_HIERARCHICAL_MASTER_V2.6.kicad_sch` ha 7 fogli e 76 reti. L'attuale catena di ingresso ha il controllo `FUSED_13V8_INPUT/OVP_CTL_VCC` derivato da D804→R1011, verso U801 LM393, D806 Zener e U802 TL431 attraverso R1001. D803 limita idealmente la tensione gate-source del MOSFET Q801; Q802/Q803 in serie attivano lo scarico del suo gate. I loro guasti cortocircuito CE possono bypassare un singolo veto (screen precedente). Non esiste un secondo interruttore di potenza indipendente sul master V2.6. Non confondere 7 schemi ERC0 con un circuito a sicurezza dimostrata.

PR #299, **integrata sul commit main `840430f4d50cffdca21f6c064a5c7e56de6ffdce`**: run #43823862585 FAST/FULL/Required 3/3 verdi, log `PASS_NATIVE_KICAD9_V26_OVP_9072_DUAL_OPEN_RAIL_FAULT_CASES_NONFAB`, 9.072 stati modellati; 324 scenari D806+TL431 aperti a VIN 48V superano 36V, fino a 47,4105V teorici. Il modello **non** autorizza 48V né certifica un singolo difetto.

## Contratto per il prossimo banco KiCad9 isolato

1. Separare chiaramente i domìni `FUSED_RAW`, uscita Q801 protetta primaria, ingresso del secondo switch, uscita protetta secondaria e `GND`. Nominare esplicitamente la nuova uscita: il carico non va mai alimentato da un bypass della serie. Non modificare di nascosto i pin del master V2.6.
2. Candidate topology: secondo interruttore high-side THT in **serie** alla via Q801. Gate con resistore verso source per **OFF passivo** quando manca il comando o il circuito di sorveglianza non è alimentato. Il driver attivo può forzare ON solo se un supervisore *indipendente* afferma OVP e UVLO validi. **Non assumere che tale interruttore, driver o supervisore esistano o siano già qualificati**.
3. **Indipendenza reale**, da comprovare con pin-net KiCad: riferimento e alimentazione del supervisore secondario non possono dipendere esclusivamente da U801/U802/D806 né essere alimentati unicamente dalla valle che essi devono proteggere. Se entrambi dipendono dalla stessa sorgente energetica o condividono un clamp, la perdita comune può invalidare la ridondanza. Definire comportamento per supply absent/brownout/reverse.
4. Proteggere i **pin del supervisore secondario** contro il massimo VIN di laboratorio e fault del suo regolatore: il difetto della rete di bias primaria non deve trasmettere >limite assoluto sul secondo circuito. Non collegare direttamente uno Zener ipotetico alla batteria. Documentare correnti di guasto, TVS/fuse, resistori a caldo, SOA, limiti VGS, I²t e tempi di intervento.
5. Due verifiche fisiche distinte richieste: (a) `Q801 D-S SHORT` deve essere bloccato da un secondo switch OFF; (b) `Q804 D-S SHORT` deve essere bloccato dalla catena primaria OFF. Il semplice `Q802 CE SHORT` o `Q803 CE SHORT` deve essere tollerato soltanto se l'altra via è indipendente e sana. **Non dichiarare fail-safe** per guasti comuni, collegamenti incrociati, driver bloccati, fusione dei contatti, degrado termico o corto su PCB.
6. La logica di power-good e mute RX/TX deve essere progettata **dopo** l'interruzione reale dei rami e con reset di default; il futuro TX richiede autorizzazione distinta. I test non energizzano alcun hardware.

## Gate di accettazione prima del CAD master o PCB

- Datasheet OEM e MPN correnti THT di Q804, secondo supervisore, riferimento, driver, diodi e fusibile; footprint e pad/pin confrontati con package meccanico.
- Schema banco KiCad9 con ERC0, netlist pin↔net esportata, simboli privi di inversioni Q801/Q804 gate/source e controlli di cortocircuito del body diode; nessun PWR_FLAG artificiale.
- Solver DC con soglie e assorbimenti da datasheet vendor (non solamente costanti idealizzate); analisi dinamica di avvio, brownout, sorpasso soglia, fault clamp + transistor e stress termico, con parametri PVT e simulazione vendor se disponibile.
- Interfacce MAIN/FRONT e carichi chiusi realmente nel CAD prima di qualunque layout. DRC e clearance/creepage solo su PCB effettiva, non su un banco senza PCB.
- CI sul commit finale 3/3 verdi e riesame indipendente safety; anche così un banco senza prototipo non costituisce una qualifica hardware.

**Stato: esclusivamente specifica d'interfaccia e criteri di validazione**. Nessun secondo power switch progettato, nessuna verifica fisica. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
