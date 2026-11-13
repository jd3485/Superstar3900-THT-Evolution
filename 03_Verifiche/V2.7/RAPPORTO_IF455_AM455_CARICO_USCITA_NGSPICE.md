# V2.7 DRAFT — interfaccia IF455 → AM455 e impedenza del carico

**13 novembre 2026.** Verifica intermedia del collegamento dal filtro LC IF455 al rivelatore AM455. È un passo verso la catena ricevente AM, **non** un collegamento definitivo su PCB-MAIN e non sostituisce mixer, guadagno IF, AGC, filtro di canale o adattamento d'impedenza. I due progetti KiCad9 THT restano separati e non hanno né PCB né cavo fisico fabbricabile.

## Stato effettivo dell'interfaccia e scelta di evitare CI duplicate

Il contratto **pin J1602→J1501** è stato introdotto e verificato indipendentemente nella [PR #89](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/89), **MERGED** sul main `214e063a7c016613ae4c28f77f79ff01f3a4d2b3`, con un gate KiCad9 nativo dedicato `verify_if455_am455_interface_native.py` già incluso in FULL. La PR #88, basata su uno SHA precedente e con un controllo equivalente, è stata **chiusa senza merge** per evitare conflitti e verifiche duplicate. Questa revisione trasferisce **solo** il test ngspice nuovo di sensibilità al carico, senza replicare un secondo controllo identico e senza creare un job GitHub Actions addizionale.

---

## Contratto elettrico verificato con due netlist KiCad9 native

| Uscita filtro IF455 | Rete locale filtro | Ingresso rivelatore AM455 | Rete locale AM |
|---|---|---|---|
| **J1602 pin 1** | `IF455_FILTER_OUT` (C1604 pin2, R1602 pin1) | **J1501 pin 1** | `IF455_BENCH_IN` (**D1501 anodo pin2**) |
| **J1602 pin 2** | `IF_BENCH_GND` (ritorno 455k) | **J1501 pin 2** | `IF_BENCH_GND` |

Script già integrato in PR #89 `03_Verifiche/V2.7/verify_if455_am455_interface_native.py`: esegue **due esportazioni KiCad9** `kicad-cli sch export netlist`, richiede i nodi e i pin della bobina, dei condensatori, del connettore e del diodo, verifica separatamente che il catodo D1501 pin1 sia sul nodo di rivelazione AM e che il suo anodo pin2 sia sul pin1 IF in ingresso. Rifiuta commistioni con rail audio/PLL, TX e alimentazioni. Un'identità di nomi non dimostra che esista un cavo: servono connettori femmina, schermatura, protezioni, orientamento pin1, test continuità e percorso di massa RF.

## Esito nativo confermato — PR #92 MERGED

La [PR #92](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/92) è **integrata** (merge `a965d3bc585e4a0cfe9ded4edea59086c6bcf7cf`), workflow [#43442916740](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43442916740) **FAST + FULL + required GATE 3/3 PASS**, final HEAD `ede2503195a25abd15ec77f0f64a1b4302c8f44f`. Test ngspice reale `PASS_NGSPICE_IF455_DETECTOR_LOAD_SENSITIVITY_SURROGATES_NOT_DIODE_NO_FAB`, 101 righe AC. A **455kHz** il modulo di trasferimento del solo modello era:

| Carico uscita (R1602=100kΩ sempre presente) | |Vout/Vin| modellato | Variazione vs riferimento |
|---|---:|---:|
| Nessun carico aggiuntivo | **0,835056** | riferimento |
| +10kΩ paralleli (surrogato) | **0,180772** | circa **−78,35%** |
| +1kΩ paralleli (surrogato) | **0,022074** | circa **−97,36%** |

I trasferimenti sono moduli di tensione **ad una singola frequenza**, non livelli RMS audio o guadagni in dB della radio, e non sono un dato reale di 1N4148. Il risultato quantifica la dipendenza dal carico e impone di valutare uno stadio di adattamento/buffer **dopo aver caratterizzato il diodo e le impedenze IF**. Non dimostra che il buffer sia già scelto o necessario in ogni architettura.

---

## Perché non possiamo collegarli direttamente come blocco di ricezione approvato

La porta di ingresso AM455 non è una resistenza costante: **D1501 è un diodo 1N4148 non polarizzato** e presenta impedenza non lineare dipendente dall'ampiezza istantanea, dal punto di polarizzazione, dalla capacità di giunzione, dalla frequenza e dal carico a valle. Non conosciamo ancora il livello IF fornito dal mixer/amplificatore, né la sua impedenza. Le precedenti scansioni ngspice del tank usavano il solo `R1602=100kΩ` in uscita, senza il rivelatore.

Nuova netlist `03_Verifiche/V2.7/spice/if455_downstream_input_load_ac.cir`: tre circuiti paralleli con L=1mH, C1602=82pF, C1603 posto **ipoteticamente** a 30pF, C ingresso/uscita 10pF, source 50Ω, Rcoil 16,5Ω **assunta come perdita RF e non OEM**, R1601 47kΩ e R1602 100kΩ. Confronta (a) **nessuna resistenza aggiuntiva**, (b) **10kΩ aggiuntivi** in uscita e (c) **1kΩ aggiuntivi**. La scansione AC native ngspice fra 450 e 460kHz legge i tre moduli di trasferimento a 455kHz e impone che il carico riduca la tensione, senza fingere che 10kΩ o 1kΩ siano l'impedenza reale del diodo.

Lo script `verify_if455_downstream_load_native.py` esegue veramente `ngspice -b`, legge `wrdata` e richiede una riduzione importante con i carichi. Sono **surrogati puramente resistivi**; il test non è un macromodello di D1501 e non prova sensibilità, SINAD, risposta di inviluppo, banda IF, Q, reiezione di canale adiacente, potenza audio o condizioni elettriche peggiori.

## Gate aperti prima di saldare o integrare le due sezioni

1. Qualificare **livello e impedenza del generatore IF455**, impedenza di ingresso dinamica del rivelatore 1N4148 e guadagno eventuale prima/dopo il filtro, con simulazione non lineare e misure di banco.
2. Definire elemento di **adattamento/buffer THT** e filtri/trasformatori IF compatibili con la catena AM/FM. Evitare di caricare un singolo tank ad alta Q con il diodo direttamente.
3. Qualificare i datasheet e i **footprint** dei componenti OEM L1601 Delevan (ancora PROVISIONAL) e C1603 GKG50015 (quote pad 5mm da OEM ma layout, rotore/assemblea e fabbricabilità non finali). Nessuna selettività finale o banda di canale approvata.
4. Completare mixer 10,695→455, IF AM/FM, separato percorso 10,695 SSB, discriminatore FM, BFO/rivelatore SSB, AGC, S-meter analogico, alimentazione RF, sicurezza e PCB a due schede.

**Verifiche nel job FULL esistente**, senza ulteriore job GitHub Actions. Il nuovo test ngspice è aggiunto alla FULL già esistente: FAST+FULL+required devono passare sul HEAD finale prima del merge. Master MAIN V2.6 sette fogli/138 refs invariato; stima complessiva ~20%, layout/routing **0%**. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
