# V2.7 — LM2903P THT: sensing ridondante e falsi consensi in guasto singolo

**16 novembre 2026 — nuovo schema KiCad9 isolato e test native, NON supervisore/PCB qualificate.**

## Schema fisico candidato

`04_KiCad/V2.7_DRAFT/MAIN_SECONDARY_LM2903P_REDUNDANT_SENSE/MAIN_SECONDARY_LM2903P_REDUNDANT_SENSE_LAB_V2_7_DRAFT.kicad_sch`, nuova libreria locale THT; 1 LM2903P PDIP-8, **9 resistenze** R2201–R2209 e 4 connettori THT, **14 componenti/34 pin/9 reti attesi da KiCad9 ERC+netlist**. Nessuna modifica al master MAIN V2.6.

**R2208 100kΩ in SERIE con R2201 100kΩ** fra VIN_RAW e VIN_SENSE. **R2202 10kΩ in PARALLELO con R2209 10kΩ** fra VIN_SENSE e LAB_RETURN. Normalmente: high 200kΩ, low 5kΩ equivalente, rapporto 1/41. Il precedente partitore singolo 100k/5k era 1/21. Per centrare soglie ~10V UVLO e ~15V OVP con riferimento **2,5V esterno NON qualificato**, R2205 UVLO high è ora **185k** (low R2206 20k), R2203 OVP high **116k** (low R2204 20k). Componenti resistivi e footprint DIN0207 sono ancora nominali; tolleranze PVT, riferimento, potenza e failure fisici non confermati.

## Risultato matematico — non garantisce fail-closed

`03_Verifiche/V2.7/verify_lm2903p_redundant_sense_native.py` (FULL) esporta la **vera** netlist KiCad9 e impone 34 terminali/9 reti; quindi enumera **34.560 scenari sintetici**: 8 resistori indipendenti ±1% (256 corner), VIN ipotetico a 15 valori 0–48V, e nove stati: sano o **OPEN/SHORT individuale** per ciascuna delle quattro resistenze di sensing. Il risultato atteso per il massimo VIN 48V idealizzato è che **qualsiasi singolo guasto OPEN/SHORT** sul sensing mantenga il nodo VIN_SENSE al massimo intorno a **2,3V**, inferiore al limite common-mode operativo circa 3V dell'LM2903P alimentato nominalmente 5V. La singola apertura di una resistenza low non porta più direttamente raw 48V sul pin: la low parallela restante crea percorso. Se top aperta o low in corto, VIN_SENSE ≈0V nominale.

**Attenzione:** rimangono possibili **falsi HIGH** del consenso finestra per alcuni VIN fuori dal range obiettivo quando un top è cortocircuitato o un low è aperto: il rapporto raddoppia e l'elettronica può trattare una tensione di alimentazione troppo bassa come buona. Il test conta esplicitamente i falsi consensi senza nasconderli. Non esiste diagnostica del guasto né shutdown autonomo. **Doppio low OPEN, perdita return comune, transienti/surge, tolleranza delle resistenze a caldo, VCC/REF persi o ingressi negativi** possono comunque sovraccaricare i pin o lasciare il segnale senza significato.

## Limiti TI verificati

Datasheet originale TI [LM2903, SLCS005AH, Apr 2025, §§5.1–5.2](https://www.ti.com/lit/ds/symlink/lm2903.pdf): per **LM2903 non-B**, ingresso absolute max **−0,3…+36V** rispetto a ground, supply raccomandata **2…30V**, ingresso common-mode funzionale **0…VCC−2V** (quindi 0…3V con VCC esterno 5V). **Input sopra VCC non equivale automaticamente a distruzione**: rileva il massimo assoluto e separatamente la non-garanzia funzionale fuori common-mode. L'ipotetico caso 48V raw sopra absolute max era reale per il partitore precedente R2202 OPEN; il partitore ridondante è solo un candidato di mitigazione DC, non una prova hardware.

U2201 viene ancora formalmente alimentato mediante **J2202 con rail esterno 5V/return; non è presente alcuna sorgente 5V regolata**, neanche una source/reference fail-safe o un interruttore serie dedicato. Non si autorizza VIN48V, alcuna fabbricazione, TX, batterie o veicoli.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
