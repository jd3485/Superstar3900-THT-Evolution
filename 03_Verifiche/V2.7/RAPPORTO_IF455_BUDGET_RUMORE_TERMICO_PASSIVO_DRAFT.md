# V2.7 — IF455: budget termico dei resistori della porta RF passiva (DRAFT)

**13 novembre 2026 — prima analisi quantitativa di rumore del sottosistema IF455, NON del ricevitore completo.**

## Motivazione e obiettivo

I test [PR #110](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/110) e [PR #111](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/111) hanno quantificato l'impedenza complessa di carico, la banda e il disaccordo del tank IF455. Manca tuttora il budget di rumore all'interfaccia. Qui si affronta **la sola componente Johnson–Nyquist dei resistori del modello passivo**, con una tecnica lineare controllabile e quantitativa anziché inventare un noise figure o una sensibilità della radio.

## Metodo fisico

Per ciascuna resistenza reale rappresentata nel deck del banco si inserisce una **sorgente di prova AC ideale 1V in serie** (solo in analisi SPICE, non componente fisico). Con tutti gli altri generatori AC spenti, ngspice determina il trasferimento complesso di tale sorgente fino al port `out` per 81 frequenze **451–459kHz**, passo 100Hz. Il contributo termico indipendente è

```
S_v,source(f) = 4 * k_B * T * R  [V^2/Hz]
S_v,out,total(f) = sum_R(4*k_B*T*R*|H_R(f)|^2)
v_out,rms(451..459kHz) = sqrt(integral S_v,out,total df)
v_source_referred,455 = sqrt(S_v,out,total(455kHz)) / |H_SIGNAL(455kHz)|
```

Temperatura assunta **290K**, `k_B=1,380649e-23 J/K`. Integrare su 8kHz del **dominio RF** è un'ipotesi di test esplicita e non deriva da una maschera reale né definisce la larghezza di banda del rumore demodulato. I resistori sono modellati come termicamente indipendenti e ideali, nulla è detto sulle tolleranze, fluttuazioni 1/f, capacità parassite OEM o correlazioni introdotte dagli stadi attivi.

## Esecuzioni native e port misurato

Verificatore `03_Verifiche/V2.7/verify_if455_passive_resistor_noise_budget_native.py` collegato alla FULL:
- **Caso 1: R100k di uscita**, con rumore di `RGEN=50Ω`, `RCOIL=16,5Ω`, `RDAMP=47kΩ`, `RLOAD=100kΩ`, 5 trasferimenti ngspice (segnale + quattro resistori);
- **Caso 2: porta con surrogato passivo gate JFET**, aggiungendo `C_GIN=10pF`, `R_GATE=1MΩ` e `C_GPAR=7pF`; 6 trasferimenti ngspice (segnale + cinque resistori).

La rete di base è `L1601=1mH`, `C1602=82pF`, `Ctrim=30pF`, `C1601=C1604=10pF`, bobina `RCOIL=16,5Ω` solo assunto dalla DCR, `R1601=47kΩ`, `R1602=100kΩ` con ingresso sorgente 50Ω. Si riproducono con vincolo <1% i due rapporti di trasferimento `|H455|` del PR110 **0,835055562** e **0,665186786**. Il test controlla sorgenti complesse, 81 campioni, PSD positive e quadratura statistica della somma dei rumori RMS. Il rumore condivide la porta di uscita del bench; non rappresenta le condizioni elettriche di un rivelatore a diodo non lineare.

## Vincoli e prossimi requisiti

1. Non convertire il rumore **a RF** ottenuto in **SNR audio**: la demodulazione AM non lineare con modello OEM reale, il guadagno IF, la banda utile e il rumore 1/f degli stadi attivi sono tuttora mancanti. Non esiste un `SINAD` misurato.
2. Il rumore del mixer, delle reti di alimentazione, del preselettore/antenna, dell'eventuale AGC e del buffer J113/KSP10BU **non è incluso**. Il valore `V_source_referred` si riferisce esclusivamente al generatore artificiale posizionato **prima del condensatore d'ingresso** del modello, non al connettore antenna.
3. Rcoil=16,5Ω è una sostituzione della DCR per ESR AC a 455kHz **NON validata**; variazioni delle perdite RF o della selettività altereranno anche questo budget.
4. Il filtro IF455 nativo standalone può essere ulteriormente verificato, ma **non esiste ancora una catena mixer→IF→demod validata nel master V2.6**. Non approvare MPN, fabbricazione, test veicolo/batteria o TX in base a questo screening.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.** Master KiCad V2.6 7 fogli/138 refs e le due PCB MAIN/FRONT restano invariati; nessun DRC fisico.
