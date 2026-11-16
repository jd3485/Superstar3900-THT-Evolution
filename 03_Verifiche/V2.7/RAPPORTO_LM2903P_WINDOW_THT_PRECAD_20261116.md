# V2.7 — supervisore THT secondario LM2903P: preselezione finestra 10/15 V

**16 novembre 2026 — solo verificatore DC di una rete resistiva ipotetica: NON circuito KiCad, NON supervisore integrato, NON sicurezza certificata.**

## Stato precedente verificato

La [PR #309](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/309) è MERGED su main `c141213b02f9e87b9f36dc3254eb85478c34c33e`, run [#43849944578](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43849944578) FAST/FULL/Required 3/3 SUCCESS. La netlist vera dell'interruttore secondario THT 27 pin/8 reti dimostra **180 condizioni matematiche di accensione involontaria con Q806 C–E corto** in 1080 scenari; non dimostra alcuna sicurezza. **Un secondo comparatore che agisca sullo stesso Q806 non risolve il cortocircuito**: serve un'interruzione ulteriore realmente indipendente.

## Preselezione OEM e domini

Candidato **TI LM2903P (package PDIP8 THT), doppio comparatore open collector**, pin 1 OUT1, 2 IN1−, 3 IN1+, 4 GND, 5 IN2+, 6 IN2−, 7 OUT2, 8 VCC. Origine OEM [TI LM2903P, PDIP(P)](https://www.ti.com/product/LM2903/part-details/LM2903P), supply ammissibile per la famiglia **2–36V** ma **VCC non deve ricevere VIN**. Qualsiasi futuro schema sarà alimentato da un rail 5V **indipendente e protetto, ancora da progettare**, con riferimento di precisione 2,5V indipendente anch'esso **non implementato**. La tensione common mode non è pari all'intero rail e deve essere verificata sul datasheet del singolo suffisso.

Test `03_Verifiche/V2.7/verify_lm2903p_secondary_window_passive.py` in FULL, **128 corner di tolleranze** 1% sui sei resistori più VREF 2,475/2,525V. Proposta rapporto di sola rete passiva:
- Vsense = VIN×5k/(100k+5k) su ramo con source indipendente ancora da definire; a VIN48V **ipotetico** nominale sense ≈2,286V (< limite common mode nominale di un LM2903P su rail 5V, non è una prova di rating assoluto sul fault).
- soglia di riferimento OVP `2,5V×20k/(50k+20k)≈0,714286V`, quindi ingresso OVP nominale **15,0V**.
- soglia UVLO `2,5V×20k/(85k+20k)≈0,476190V`, quindi **10,0V**. L'ordine delle polarità e la logica open collector devono ancora essere progettati fisicamente. I due confronti condividono il sensing e il rail riferimento: **non sono indipendenti fra loro**, non vanno confusi con il supervisore primario U801/U802.
- Il modello con resistori ±1% e riferimento ±1% produce UVLO min/max circa **9,557–10,462V** e OVP **14,363–15,663V**. I valori sono validi unicamente nello screen di partitori privi di correnti di bias e isteresi.

## BLOCCANTE di sicurezza già identificato

**Apertura del resistore inferiore 5k dello sensing porta idealmente il pin di comparatore verso VIN**. Senza uno stadio resistivo/clamper e dimensionamento thermal/surge indipendente, con VIN ipotetico 48V si distruggerebbe potenzialmente il LM2903P nonostante il rapporto nominale sia attenuato. Lo script forza `full_48V_fault_input_electrically_qualified: False` per ogni corner; richiede clamp ingresso con corrente limitata sotto guasto, protezione contro sense top/lower OPEN/SHORT, sovra VCC, riferimento open/short, termica e reverse. Anche un output open-collector non è un vero interlock fail-OFF se 5V/reference scompaiono; occorre reset e seconda catena switch completamente autonoma e realmente sezionante, con gate pull-up source e fail-off dimostrato per short singoli.

Questa PR è uno **screen quantitativo architetturale prima di CAD**; nessun nuovo PCB, nessun DRC, nessun modello vendor SPICE, nessun permesso fabbricazione, alimentazione a 48V o TX. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
