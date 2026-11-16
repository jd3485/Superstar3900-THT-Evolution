# V2.7 — due riferimenti esterni THT separati, guasti correlati simultanei

16 novembre 2026 — modello DC ipotetico su netlist KiCad9 reale; **NON prova di sicurezza**.

## Stato precedente

PR [#317](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/317) **MERGED** su main SHA `4db05caea15203d155d0e75c26301f4907db868d`; run [#43863682723](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43863682723) FAST/FULL/Required **3/3 SUCCESS**, **KiCad9 ERC 0 errori/0 warning**, 60 pin fisici/14 reti/24 componenti THT, **33.792** corner VREF singolo guasto: zero falsi consensi VIN fuori 9–16 V e **1.536 falsi spegnimenti nominali a 13,8 V**. Due ingressi di riferimento fisici distinti J2203 e J2205; nessun generatore 2,5V indipendente realmente disegnato.

## Nuova regressione comune causa

`03_Verifiche/V2.7/verify_dual_lm2903p_split_vref_double_fault_native.py` in FULL riesporta la vera netlist THT, verifica due reti separate VREF_A/VREF_B (J2203/J2205) e il **rail 5 V e ritorno comuni** a U2201/U2202. Percorre **101.376 corner** sintetici: 256 vettori ±1% sulle otto resistenze base × 11 VIN teoriche 0–48 V × 6 tensioni VREF_A × 6 VREF_B, tutte combinazioni inclusi guasti di riferimento simultanei e valori nominali.

Nel modello, **1.028 casi di consenso falso** per VIN fuori 9–16V riemergono quando **entrambe le VREF scendono a 1,25V** (512 scenari) o salgono a **5V** (516). Questo non implica un guasto reale probabile o indipendente, ma dimostra formalmente che **due connettori separati non eliminano difetti correlati di alimentazione o riferimento**. Le tensioni sono stimoli sintetici, non curve OEM.

## Vincoli prima di sicurezza/PCB

Occorre scegliere OEM THT per riferimento 2,5V e alimentatore 5V, verificare riferimento indipendente da VCC comune, overcurrent/fail-short, clamp ingressi per doppi guasti, offset e common-mode del comparatore nei transienti, and/or separate wire fault, oltre a **due switch realmente in serie e controllo OFF che non si possa bypassare col corto Q806 C–E**. Ancora nessuna sezione MAIN V2.6 integrata, nessuna vera PCB, ERC della scheda finale non disponibile. Il raw VIN48V è un'ipotesi di guasto **NON consentita per energizzazione**. Issue #27 rimane aperta.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
