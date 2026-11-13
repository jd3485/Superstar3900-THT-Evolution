# V2.7 — Transitorio rail audio 6 V, simulazione comportamentale **ngspice reale**

**13 novembre 2026 — PR tecnica in revisione.** Modello dei transitori del **collegamento PSU → amplificatore** già definito dai draft KiCad LM317 / LM386; **non è** un macromodello TI LM317, LM386, PCB e cablaggio fisico, né una misura di laboratorio. Non è adatto alla fabbricazione o all'alimentazione automobilistica.

## Correzione fondamentale: resistenza di ritorno inclusa

La prima revisione approvata nella **PR #70** ipotizzava il ritorno di massa ideale (zero ohm) e misurava la tensione dell'alimentazione rispetto alla massa PSU. Era una simulazione valida **solo per quell'ipotesi**, ma **sottostimava il droop ai pin dell'LM386** se il secondo conduttore reale ha resistenza. Questa revisione aggiunge realmente a ngspice `RRETURN_GOOD` e `RRETURN_BAD`, sostituisce i condensatori e carichi a massa globale con massa locale del lato amplificatore, e misura `V(amp+, amp_gnd)`. Controlla anche lo spostamento della massa audio rispetto alla sorgente a 140 mA:

| Scenario | Resistenza andata | Resistenza ritorno | Droop differenziale atteso | Spostamento GND locale atteso al carico |
|---|---:|---:|---:|---:|
| Bassa R | 0,20 Ω | 0,20 Ω | **78 mV** | **28 mV** |
| Alta R | 1,50 Ω | 1,50 Ω | **390 mV** | **210 mV** |

Questi valori restano **calcoli attesi** fino a esito reale della CI. Non rappresentano resistenze misurate o specifiche del cavo, e la massa locale può influire anche sulla suscettibilità al rumore AF/RF. La scelta di resistenza di anello, guaina, connettori, orientamento e ritorni dovrà essere qualificata prima del layout.

---

## Circuito simulato

Netlist effettiva `03_Verifiche/V2.7/spice/audio_6v_lab_rail_step_behavioral.cir`, eseguita con `ngspice -b` dalla CI nativa.

- Sorgente Thévenin IDEALE a **5,952 V**: rappresenta il punto nominale ipotizzato, **non** comportamento o regolazione dinamica reale del LM317.
- Resistenza equivalente interna IPOTETICA **0,25 Ω**, non specifica OEM del LM317 e **non** da confondere con il suo dropout o con una resistenza piccola segnale.
- **C1402 = 10 µF** vicino all'uscita PSU e **C1206 = 100 µF** vicino all'ingresso LM386, come nei rispettivi schemi KiCad. Capacità ideali, senza tolleranza, ESR, ESL o perdite. Il 100nF C1205 non viene modellato: sui millisecondi lo scopo è stimare il droop lento, non ripple ad alta frequenza.
- Due scenari indipendenti con **ciascun conduttore** di andata e ritorno modellato esplicitamente: **0,20 Ω per conduttore** oppure **1,50 Ω per conduttore**. Sono numeri illustrativi, non misure del cavo previsto. Il ritorno produce spostamento della massa locale dell'amplificatore rispetto alla massa della sorgente.
- Carico di corrente costante per tratti che *assorbe* da +6 V a massa: **20 mA** a riposo, sale artificialmente a **140 mA** a 5 ms, rimane 5 ms, poi torna a 20 mA. Questo **non** simula la corrente non lineare di un LM386 o la sua potenza audio/THD.
- Analisi transitoria da 0 a 18 ms, campionamento differenziale `V(AMP+, AMP_GND)` a 4 ms, 8 ms, 15 ms e della massa locale a 8 ms; le verifiche confrontano i risultati veri di ngspice con i valori stazionari della rete resistiva/capacitiva. Un test passa solo se ngspice termina con codice 0, produce tutte le misure e ogni confronto rientra nella tolleranza di test.

## Risultati attesi dai calcoli: non dichiararli simulati finché CI non è verde

Per la rete ideale a tempo sufficientemente lungo, la variazione di carico è `ΔI=0,12A`; la caduta dovuta alle due resistenze è `ΔV≈ΔI·(R_interna+R_andata+R_ritorno)`:

| Scenario non calibrato | R totale ipotetica | Prima dello step | Durante lo step | Caduta stazionaria attesa |
|---|---:|---:|---:|---:|
| Collegamento a bassa resistenza | 0,25+0,20+0,20=0,65Ω | 5,939V | 5,861V | **78mV** |
| Collegamento più resistivo | 0,25+1,50+1,50=3,25Ω | 5,887V | 5,497V | **390mV** |

La simulazione campiona anche il ripristino dopo il gradino e le misure possono differire leggermente dai valori statici durante il transitorio. Il caso 1,50Ω è **illustrativo**: non indica né un target né un massimo per il cablaggio reale.

## Verifica riproducibile

`03_Verifiche/V2.7/verify_audio_rail_step_ngspice.py` è eseguito **solo nella CI FULL nativa**, che contiene già ngspice e KiCad9 e che non crea un ulteriore job a pagamento. Il test controlla:

1. Presenza di due circuiti con valori di condensatori corrispondenti a C1402/C1206, tensione nominale e resistenze esplicitamente etichettate come scenari.
2. Invocazione ngspice **reale**, con `.meas tran` per i 6 campioni prima/durante/dopo il gradino sui due circuiti.
3. Esito senza errori e confronto di tensioni, cadute e recupero con i calcoli passivi; attesa caduta nel caso ad alta resistenza almeno 4,0× quella a bassa resistenza.
4. Impossibilità di spacciare il test per una qualifica dell'alimentatore: il token di PASS dice chiaramente `BEHAVIORAL`, `NO_VENDOR`, `NO_FAB`. L'ERC e le netlist KiCad dei tre draft restano verificati separatamente dalle loro suite native.

## Condizioni imprescindibili prima della PCB

Mancano: modello TI ufficiale del LM317 compatibile con ngspice e relativa validazione contro datasheet, variazione dinamica dell'assorbimento LM386 con audio e clipping, tolleranze ESR/ESL dei condensatori, lunghezza e tipo del cavo, resistenza del ritorno, EMI/ground loop RF, recupero regolatore, startup a carico alto, fault e reverse input, dissipazione a 60°C e oltre, protezione contro inversione dei connettori, misura tensione al pin 6 dell'LM386 e prove di potenza/THD. Nessun DRC perché non esiste una PCB del modulo e le due PCB MAIN/FRONT non sono sbrogliate.

**Conclusione limitata:** una resistenza di cablaggio maggiore può aumentare il droop in questo modello; la quantità misurata dalla simulazione non costituisce limite progettuale o misura dell'hardware. La sorgente LM317 continua ad essere **solo da banco 10–10,5V**, senza approvazione per ingresso 13,8V, batteria o veicolo.

**NO FAB / NO GERBER DI PRODUZIONE / NO TX / NO BATTERIA / NO VEICOLO.** Master MAIN V2.6 invariato 7 fogli/138 refs; tre pilot audio standalone non integrati; progettazione complessiva ~20% stima, layout/routing 0%.
