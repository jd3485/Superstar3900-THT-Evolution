# V2.7 DRAFT — Cablaggio THT audio LAB 6 V JST XH, qualificazione parziale

**Data:** 13 novembre 2026. **Ambito:** solo J1402 sul pilot PSU LM317 e J1201 sul pilot amplificatore LM386, entrambi standalone. **Non** riguarda alimentazione veicolare 13,8 V, connettore ingresso J1401, segnali audio FRONT o il master radio V2.6.

## Modifiche CAD effettive

Le istanze e le definizioni di libreria locale/embedded dei **due soli connettori J1402/J1201** sono passate dall'header generico 2,54 mm alla geometria KiCad9 THT:

`Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical`.

Il footprint è per **JST XH B2B-XH-A**, 2 circuiti e **passo 2,50 mm**, con **pad 1 a (0,0)** e **pad 2 a (2,50,0)** nel sistema del footprint. È **sbagliato** sostituirlo con uno 0,1" a 2,54mm senza cambiare progetto, perché i passi non coincidono. Pad 1 = alimentazione LAB +6V su entrambe le schede; pad 2 = ritorno della rispettiva sezione audio. La numerazione esatta deve essere mantenuta anche sulla distinta del cavetto. Gli altri header restano invariati.

## Famiglia di componenti OEM identificata, non BOM finale

La [pagina attuale JST XH](https://www.jst-mfg.com/product/index.php?lang=2&series=277) presenta i codici **B2B-XH-A**, **XHP-2** e **SXH-001T-P0.6** con dati meccanici. Il [catalogo JST XH](https://www.jst.com/wp-content/uploads/2021/01/eXH-new.pdf) indica:
- **2× header THT B2B-XH-A**, uno per scheda (orientamento verticale; passo 2,50 mm).
- **2× housing femmina XHP-2**, uno su ciascuna estremità del **cavo a due fili**, non una coppia maschio/maschio.
- **4× contatti a crimpare SXH-001T-P0.6**, contatti standard per cavo **AWG 28–22**, isolamento Ø **0,9–1,9 mm**. Ipotesi di progetto: cavo flessibile **AWG 26** purché isolamento/die/serraggio siano compatibili; numero di trefoli e materiali da definire.
- I requisiti di famiglia sono **3 A con AWG22**, **250 V**, **−25…+85 °C**, e contatto a **friction lock**, NON un bloccaggio automotive qualificato contro vibrazione. **Non** usare rating 3 A per qualifica del cavo AWG26, né come garanzia di resistenza a vibrazioni, temperatura interna radio o connessione invertita.
- Il fatto che i codici compaiano nel catalogo ufficiale aggiornato è buona evidenza di famiglia attuale, **ma il lifecycle OEM esatto dei codici ordinabili, variazioni LF/SN, marcature e lotti va confermato prima del gate release**; no certificazione MPN finale implicita.

| Estremità | Ref PCB | Pad 1 (positivo) | Pad 2 (ritorno) | Controparte |
|---|---|---|---|---|
| PSU laboratorio | J1402 | `AUDIO_6V_LAB` | `AUDIO_GND` | XHP-2 + 2 contatti |
| Amplificatore | J1201 | `AUDIO_6V_LAB` | `GND` | XHP-2 + 2 contatti |

## Verifica nativa obbligatoria

Il controllo `03_Verifiche/V2.7/verify_audio_6v_supply_contract_native.py` viene già eseguito da `ci/full_regressions.py`. In questa revisione controlla **entrambe le istanze KiCad**, i simboli embedded e le rispettive librerie, e legge **il vero file del footprint installato nel container KiCad9** per confermare pad1/pad2, tipo **through-hole** e passo 2,50 mm. Inoltre esporta entrambe le netlist reali e confronta pin→net PSU↔amplificatore, e mantiene separati i rail RF/PLL. **Nessuna pretesa DRC:** non abbiamo un file PCB fisico. L'esito passa solo quando la CI sullo SHA finale dice PASS.

## Gate aperti per cablaggio e fabbricazione

- **Non approvato un harness fisico:** scegliere lunghezza reale, routing meccanico, supporto anti-strappo, crimpatura specificata e verificata con pull-test, regole di posa RF, ritorno massa, sezioni, resistenza totale andata+ritorno, difesa da corto circuito e inversione pin 1/2.
- **Nessuna protezione anti-inversione:** un housing polarizzato riduce errori di accoppiamento con l'header, ma non impedisce un **crimp nel vano sbagliato** o la connessione di un cavo realizzato al contrario, quindi servono test di continuità e ispezione.
- **Progettazione audio non congelata:** LM317 bench ingresso **10–10,5 V** misurati al pin IN, no input automotive o PSU a 13,8 V; LM386 efficienza/potenza/THD, dissipazione, cavi, ripple e transienti reali non ancora qualificati.
- La simulazione ngspice dei conduttori (PR #70/#71) usa 0,20Ω e 1,50Ω **ipotetici** per ogni filo, non dimostra la resistenza del cavetto JST.
- **Layout/footprint clearance reale da verificare**: orientamento, ingombro del housing, inserimento/estrazione, raggio di curvatura, accessibilità, distanze da dissipatore LM317 caldo e audio RF sensibile.

Questo è un avanzamento **reale degli schematici THT** ma **NON** una selezione industriale definitiva. Il master radio V2.6 rimane 7 fogli/138 ref; PCB-MAIN/PCB-FRONT con piste ancora non esistenti, stima complessiva ~20% e layout 0%. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
