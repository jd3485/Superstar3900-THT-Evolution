# V2.7 — doppio guasto del partitore LM2903P THT: 92.160 corner

16 novembre 2026. Analisi sul circuito KiCad9 THT **ISOLATO, NON alimentabile né qualificato**.

## Stato realmente integrato

PR [#313](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/313) MERGED su `main` SHA `cac616c522d82701b9388675ae3d6f8c323571dc`; run [#43857742450](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43857742450) FAST/FULL/Required **3/3 SUCCESS**, KiCad9 ERC **0 errori / 0 warning**, 34 pin THT/9 reti native, 34.560 casi di un singolo resistore OPEN/SHORT. **3.072 casi matematici di falso consenso** per VIN fuori finestra 9–16V; massimo nominale input 2,329649V con VIN ipotetico 48V e un singolo guasto della rete. Questo non è fail-closed.

## Modello reale netlist, coppie di fault

`03_Verifiche/V2.7/verify_lm2903p_redundant_double_fault_native.py` è un NUOVO controllo FULL sul vero file `04_KiCad/V2.7_DRAFT/MAIN_SECONDARY_LM2903P_REDUNDANT_SENSE/MAIN_SECONDARY_LM2903P_REDUNDANT_SENSE_LAB_V2_7_DRAFT.kicad_sch`, con pin/nodi reali **34/9** verificati. Lo screen calcola **92.160 casi** = 256 corner di otto resistori ±1% × sei coppie distinte delle quattro resistenze R2208/R2201 (top serie) e R2202/R2209 (bottom parallelo) × quattro combinazioni OPEN/SHORT × 15 valori di VIN tra 0–48V ipotetici. Modello DC ideale, non vendor transistor/SPICE, neppure tolleranze termiche o pulse.

**Doppia apertura R2202 + R2209** lascia il nodo SENSE flottante verso VIN raw tramite TOP: a 48V può portare il pin U2201 a **48V**. **Doppio corto R2208 + R2201** collega SENSE a VIN raw: stesso rischio. In ciascuno di questi due pattern e per tutti i 256 corner, a VIN48V si supera il massimo assoluto ingresso **36V TI LM2903P**: **512 casi** diretti di stress fuori absolute max. Altre coppie possono superare il limite di **common-mode operativo 3V con VCC5V** o indicare erroneamente GOOD quando l'alimentazione reale è fuori finestra. La conteggiatura numerica dei casi è parte del test, non un claim di robustezza generale.

## Interpretazione, rischio e decisioni

La rete TOP serie / BOTTOM parallela mitiga **alcuni singoli fault della sola rete resistiva**, ma non preserva i pin con guasti doppi o guasti common-cause (masse/supply/reference). Inoltre il falso consenso che si produce con un singolo guasto già blocca la qualifica fail-closed. Priorità: un secondo canale di sensing davvero indipendente, veto hardware con switch serie distinto da Q806, validazione OEM dei riferimenti e rail, protezione in fault OPEN/SHORT, surge, temperatura, condizione VCC assente e revisione indipendente.

Limiti OEM: [TI LM2903 non-B SLCS005AH](https://www.ti.com/lit/ds/symlink/lm2903.pdf): ingresso abs −0,3…+36V, CM funzionale 0…(VCC−2V); il source48V è **solo un caso teorico di guasto NON autorizzato**.

Non è stata aggiunta alcuna PCB, prova fisica, supply 5V/2,5V indipendente, TVS né interruzione load fail-off. Niente implementazione MAIN e FRONT. Issue #27 aperta.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
