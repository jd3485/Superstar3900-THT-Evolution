# V2.7 — primo banco reale KiCad9 THT: interruttore secondario Q804 a riposo spento

**16 novembre 2026. Candidato ISOLATO, non integrato nel master MAIN V2.6, nessuna autorizzazione ad alimentare hardware.**

## Funzione effettivamente disegnata

Schematic KiCad9: `04_KiCad/V2.7_DRAFT/MAIN_SECONDARY_OVP_Q804_PASSIVE_OFF/MAIN_SECONDARY_OVP_Q804_PASSIVE_OFF_LAB_V2_7_DRAFT.kicad_sch`.

Componenti reali rappresentati con libreria incorporata e footprint THT candidato:

- **Q804** Infineon `IRF9540NPBF`, P-MOS TO-220 3 pin, pin 1 GATE, 2 DRAIN, 3 SOURCE. Fonte OEM https://www.infineon.com/part/IRF9540N, **Active**, VDS −100V, |VGS| massimo 20V, RDSon massimo 117mΩ a |VGS|=10V. Impronta KiCad generica `Package_TO_SOT_THT:TO-220-3_Vertical`: meccanica esatta e pad non campionati.
- **R2101** 47kΩ candidato standard THT fra source e gate, di default porta `VGS=0` **solo se il circuito esterno è ad alta impedenza e nessun guasto forza gate basso**. Dimensione e wattaggio non qualificati.
- **D2101** 1N4742A nominale 12V DO-41, catodo a source e anodo a gate, clamp ideale source-gate per VGS negativo. Tensione reale al punto operativo e transitori **non verificati**, così come energia d'impulso; D2101 aperto/corto non è tollerato come meccanismo di sicurezza certo.
- **J2101**, **J2102**, **J2103**, connettori 2 pin THT di laboratorio: ingresso preprotetto, uscita secondaria, gate driver/return *di un futuro supervisore indipendente non ancora disegnato*. `LAB_RETURN_ONLY` è comune ai tre connettori e non va confuso con SOURCE; il circuito non ha un pilotaggio autonomo.
- Tutte le 13 estremità reali di simboli e 4 reti nominate sono attese nel test nativo KiCad9. Esige ERC0 e pin-net per SOURCE/GATE/DRAIN e le tre porte. È unicamente un controllo CAD.

## Vincoli fail-closed non soddisfatti

Il banco è un **blocco di commutazione**, non una protezione OVP/UVLO completa. Un collegamento esterno del gate a GND può attivare Q804 indipendentemente da VIN/PG; manca l'interblocco hardware. La corrente attraverso il body diode e i guasti drain-source del MOSFET possono bypassare la disconnessione. Indipendenza da primario Q801/U801/U802, filtro VIN, SOA, load dump, limitazione VGS in D2101 OPEN, pilotaggio reale del gate, default durante brownout e temperature restano da qualificare prima della selezione delle reti di potenza.

**L'assenza di limitazioni reali impedisce qualsiasi prova di alimentazione: NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

## Nuovi gate

1. Componente secondario del supervisore: candidato OEM **Texas Instruments LM2903P**, scheda ufficiale https://www.ti.com/product/LM2903/part-details/LM2903P, *ACTIVE*, PDIP-8, −40…+125°C, Vs max 36V, **stock TI non disponibile al momento della consultazione**. Il limite 36V obbliga alimentazione veramente indipendente, protetta e dimostrabile anche con clamp guasto; il solo LM2903P **non risolve la condizione VIN48V**. Si esclude B-version SMD per vincolo THT. Nessun U805 approvato né disegnato.
2. Disegnare secondo supervisore, bias indipendente e driver del gate con progetto contro doppio open Zener/TL431, acquisire modello vendor quando disponibile e test fault/potenza. Non collegare J2103 a un controllo non provato.
3. Verificare orientamento reale dei MOSFET in serie, inclusi body diode e guasti D-S; armonizzare nomi reti e port KiCad9 con master, preservando ogni pin già montato. Solo dopo ERC completo nativo, modello energetico, review safety e hardware proof si potrà valutare integrazione.

Dati OEM Q804: https://www.infineon.com/part/IRF9540N; LM2903P: https://www.ti.com/product/LM2903/part-details/LM2903P. **Questo rapporto non costituisce una release di produzione.**
