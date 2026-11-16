# V2.7 — doppio LM2903P THT: guasto di riferimento condiviso

16 novembre 2026 — circuito KiCad9 isolato, test comportamento ideale DC, **NON** hardware qualificato.

## Eredità ed evidenze

La PR [#315](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/315) contiene due comparatori veri U2201/U2202 TI LM2903P THT DIP8, due gruppi di partitori sensing da 2×100kΩ serie e 2×10kΩ parallelo, due partitori di soglia passiva UVLO/OVP e un'uscita open-collector in comune. L'intera netlist nativa è 58 pin / 13 reti se confermata dal KiCad9. I due canali condividono ancora **VIN_RAW, GND, rail5V e riferimento esterno 2,5V**. Lo schema non contiene interruttore serie né rail di sicurezza indipendenti.

## Test su vera netlist KiCad9

`03_Verifiche/V2.7/verify_dual_lm2903p_common_reference_fault_native.py` esporta il netlist KiCad9 e impone che entrambe le soglie del canale A (R2203/R2205) e B (R2214/R2216) usino lo **stesso ingresso J2203 EXTERNAL_VREF_2V5_UNQUALIFIED**; entrambe le alimentazioni comparatori (pin8 U2201/U2202), il pullup R2207 e il connettore J2202 sono sullo **stesso rail5V non realizzato**.

**16.896 scenari ideali** = 256 corner resistivi ±1% ×11 VIN sintetiche (0, 6, 7, 8, 10, 13,8, 16, 20, 24, 30, 48V) ×6 VREF esterne ipotizzate (0, 1,25, 2,475, 2,5, 2,525, 5V). Risultato pre-analizzato: 1.028 corner di consenso FALSE-GOOD per VIN fuori 9–16V, di cui 512 quando VREF dimezzata a1,25V e 516 quando VREF raddoppia a5V. Con VREF 2,5V e VIN13,8V tutti i 256 corner di modello sono GOOD. Il guasto comune del riferimento sposta contemporaneamente UVLO/OVP dei due canali e **non è neutralizzato dal secondo LM2903P**.

I riferimenti ipotizzati a 0/1,25/5V **non equivalgono al comportamento reale di un MPN TL431, LM4040, ecc.**: nessun produttore di riferimento reale è stato selezionato o simulato con I/V o brownout. 48V sono un caso teorico di guasto, **non una tensione approvata**; non è stato qualificato offset del comparatore, rail assente, surges o errori correlati.

## Conseguenze

Per isolare realmente una catena devono essere progettati un riferimento e una supply secondaria protetti/autonomi, un veto hardware con switch in serie non bypassabile da Q806 C–E SHORT, protezione input/supply ESD/TVS/fault, test PVT e validazione delle aree di rame/footprint THT. Non confondere un nodo OC condiviso con due uscite indipendenti fail-safe. Il master MAIN V2.6 e FRONT sono invariati. Issue #27 resta aperta.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
