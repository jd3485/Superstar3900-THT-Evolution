# V2.7 — Doppio canale LM2903P THT su due sensori di tensione separati

**16 novembre 2026 — KiCad9 reale isolato, NON prototipo sicuro e NON schema MAIN.**

## Base integrata

PR [#314](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/314) MERGED su main `04667a14426e869070a7c55cf9aaf5186fefda2d`, run [#43859615060](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43859615060) FAST/FULL/Required **3/3 SUCCESS**. 34 pin/9 reti KiCad9, 92.160 corner doppio OPEN/SHORT: 9.216 oltre campo common-mode 3V, 512 oltre limite assoluto ingresso 36V con source 48V ipotetica. **3.072 false finestra GOOD già con un singolo resistore guasto** in PR #313 non eliminati dal modello precedente.

## Nuovo schema realmente disegnato

`04_KiCad/V2.7_DRAFT/MAIN_DUAL_LM2903P_INDEPENDENT_SENSE/MAIN_DUAL_LM2903P_INDEPENDENT_SENSE_LAB_V2_7_DRAFT.kicad_sch`. Copia del banco ridondante A senza modifiche ai componenti originali, con aggiunta di un **secondo TI LM2903P PDIP8 U2202** e 8 resistori THT dedicati **R2210–R2217**. La **misura B** è indipendente dai quattro resistori di sensing A: R2210+R2211 due 100k serie TOP, R2212||R2213 due 10k parallelo BOTTOM; differente net `VIN_SENSE_B` e `SENSE_SERIES_MID_B`. B possiede anche partitori di riferimento autonomi resistivi **R2214/R2215 (OVP 116k/20k)** e **R2216/R2217 (UVLO 185k/20k)**.

U2201 e U2202 uscite open-collector condividono il nodo `WINDOW_GOOD_OC_BIASED_LAB`, col pullup R2207 già presente: se un canale rileva fault, un suo OC può tirare basso il consenso, assumendo due comparator sani e alimentati e uscita senza corti. **Le sorgenti esterne 5V e VREF2,5V sono CONDIVISE, NON progettate**. Anche VIN raw, RETURN e linea OUTPUT sono condivisi: questa non è una catena di sicurezza indipendente e non protegge da fault comuni.

Nuova regressione `03_Verifiche/V2.7/verify_dual_lm2903p_window_native.py` integra FULL native KiCad9, impone ERC0, **58 pin THT/13 reti/23 componenti**, percorre **69.120 casi idealizzati** (256 corner di tolleranze 8 resistenze ±1%, 15 VIN sintetici, singolo guasto su 9 stati di senso in A *oppure* B). Se solo una rete di sensing A/B ha un resistore OPEN/SHORT, il canale B/A sano deve mantenere il veto quando VIN è nettamente fuori dall'intervallo nominale (VIN <9V oppure >16V). Questa ipotesi matematica non equivale al fail-safe hardware.

## Blocker

Doppio guasto della stessa rete (già dimostrato in #314), perdita/corto delle alimentazioni esterne, riferimento comune, guasto dei due comparatori o linea OC SHORT a supply, drift/offset common-mode, separazione delle masse e soprattutto guasto Q806 C–E restano non mitigati. Nessuno switch serie addizionale è integrato, nessun rail protetto, reference OEM, TVS reale, prova analogica o PCB. Nessun permesso di energizzare a 48V. **Issue #27 APERTA. NO FAB/TX/BATTERIA/VEICOLO.**
