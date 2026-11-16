# V2.7 — due ingressi VREF esterni separati per LM2903P THT

16 novembre 2026. **Nuovo schema nativo KiCad9 isolato; nessuna sorgente 2,5 V progettata o qualificata.**

## Evidenza integrata

PR [#316](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/316) MERGED su main `c2dfc8db4279e3df1b3345aea0a3566e4586817e`, run [#43862397171](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43862397171) FAST/FULL/Required **3/3 SUCCESS**. Vera netlist KiCad9 due LM2903P PDIP8 **58 pin/13 reti**, 16.896 corner VREF comune: **1.028 falsi consensi** fuori finestra9–16V con 1,25/5V reference correlata. Nessun fail-closed.

## Modifica elettrica reale nel banco

Nuovo schema `04_KiCad/V2.7_DRAFT/MAIN_DUAL_LM2903P_SPLIT_EXTERNAL_VREF/MAIN_DUAL_LM2903P_SPLIT_EXTERNAL_VREF_LAB_V2_7_DRAFT.kicad_sch`, libreria locale THT, `kicad_pro`, `sym-lib-table`.

Inalterati U2201 e U2202 LM2903P DIP8, R2201–R2217 e J2201..J2204. Aggiunto **J2205 connettore THT a due poli** per una **seconda alimentazione VREF esterna presunta**. Connettere i soli TOP dei partitori di riferimento B R2214/R2216 a `EXTERNAL_VREF_B_2V5_UNQUALIFIED`, mentre A R2203/R2205 resta su `EXTERNAL_VREF_2V5_UNQUALIFIED` da J2203. Il RETURN dei due connettori e il rail 5V dei comparatori rimangono comuni e NON implementati. La modifica crea **60 pin reali/14 reti/24 parti** attesi da export nativo KiCad9 ed ERC0, da verificare in CI senza waiver.

`03_Verifiche/V2.7/verify_dual_lm2903p_split_vref_native.py` in FULL esporta la vera netlist, impone pin A/B riferimenti separati e ingressi/comparatori ancora condivisi su 5V/RETURN/OC, e simula **33.792 casi sintetici** = 256 tolleranze ×11 VIN × 2 scelte di canale con VREF guasta ×6 VREF teoriche 0/1,25/2,475/2,5/2,525/5V. Con **un solo VREF esterno guasto** e il secondo sano, si prevede ZERO falsi consensi con VIN<9V o >16V, pur con possibili arresti ingiustificati a VIN13,8V. Questo non prova l'indipendenza effettiva di due generatori di riferimento né il comportamento con VCC assente.

## Bloccanti

La separazione dei **connettori** non è una realizzazione di due riferimenti indipendenti; restano ignoti l'isolamento dei generatori, il guasto in corto del return comune, la tensione negativa/transienti, errori comparator/OC stuck-high, brownout, VCC5V comune, raw VIN e soprattutto un secondo switch serie non bypassabile da Q806 C–E. **Nessun PCB, DRC o prova hardware**. Restano i divieti: **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.** Issue #27 OPEN.
