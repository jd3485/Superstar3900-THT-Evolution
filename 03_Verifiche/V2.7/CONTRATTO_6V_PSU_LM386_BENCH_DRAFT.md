# V2.7 DRAFT — contratto 6 V da PSU LM317 a LM386 RX (13 novembre 2026)

**Tipo di avanzamento:** modifica reale di schema KiCad9 **standalone** dell'amplificatore RX e dei simboli THT, più controllo indipendente delle netlist native di **due** schematici, senza installare cavi, PCB, o power-up.

## Cambio del circuito
- Nel foglio `04_KiCad/V2.7_DRAFT/AUDIO_RX_MONO_LM386_V2_7_DRAFT.kicad_sch`, la rete prima denominata `AUDIO_5V` è rinominata `AUDIO_6V_LAB`. La nuova tensione contrattuale del modulo di laboratorio è ~6 V; il pin 6 di U1201 LM386, C1205 e C1206 restano **alle stesse connessioni fisiche**. `J1201` mantiene footprint header 1x02 THT e pin1 rail +6V, pin2 ritorno GND. Aggiornati il simbolo embedded e `TH_AUDIO.kicad_sym` da `BENCH_5V_CONN` a `BENCH_6V_CONN`, inclusi il nome del pin e la descrizione di laboratorio.
- Il foglio PSU indipendente `04_KiCad/V2.7_DRAFT/AUDIO_PSU_6V/AUDIO_PSU_LM317_6V_LAB_DRAFT.kicad_sch` è **già** sullo stesso nome rail `AUDIO_6V_LAB` e pin di uscita J1402. Il suo ingresso ora è `LAB_VIN_10TO10P5V`, corretto da PR #62; è **solo 10–10,5V stabilizzati al pin IN** dal banco, non 13,8V veicolari.
- I fogli KiCad **non sono ancora connessi fisicamente né gerarchicamente**. Si definisce unicamente il cablaggio logico richiesto.

## Cablaggio logico 2 conduttori, senza cavo reale

| PSU LM317 | Pin | Uscita/ritorno | Amplificatore LM386 | Pin |
|---|---:|---|---|---:|
| J1402 | **1** | AUDIO_6V_LAB | J1201 | **1** |
| J1402 | **2** | AUDIO_GND → GND del modulo LM386 | J1201 | **2** |

Nel PSU, U1401.2 e C1402.1 sono sul rail `AUDIO_6V_LAB`; C1402.2 è a `AUDIO_GND`. Nel LM386, U1201.6, C1205.1 e C1206.1 sono sul rail `AUDIO_6V_LAB`; U1201.4, C1205.2, C1206.2 sono sul `GND` locale. Il nuovo `verify_audio_6v_supply_contract_native.py` riesporta **entrambe** le netlist KiCad9 e impone queste membership e la mappa 1→1 e 2→2. La legge di range LM386N-1 4–12V è rispettata da estremi di riferimento statici ~5,61–6,31V; **non** equivale a qualifica THD, EMI, energia o ripple.

## Aspetti non validati
- **Entrambi i connettori sono header maschi**: non si possono innestare fra loro direttamente. Cavo con due femmine crimpate, fissaggio, polarizzazione meccanica, dimensione e schermatura devono essere scelti e verificati prima di layout finale. Errato inserimento invertirebbe tensione e massa; niente protezione anti-inversione completata.
- **Alimentazione 10–10,5V da banco esterna**: non adatta al VIN 13,8V della radio, né a batteria/veicolo. Da progettare in futuro una vera sorgente autonoma compatibile con transitori d'auto, portata di corrente per LM386 e carico 4/8Ω, ondulazioni, massa RF, filtri e termica.
- **La specifica audio è incompleta:** da misurare/certificare potenza di uscita, THD, rendimento, dissipazione U1201, risposta in frequenza, carico altoparlante e cablaggio fra MAIN e FRONT. La tensione nominale +6V non dimostra potenza audio garantita.
- Il simbolo `BENCH_6V_CONN` espone pin come `power_out` **solo per dichiarare nella bozza una sorgente esterna al foglio ai fini ERC**: non costituisce un regolatore reale sul PCB audio o una garanzia di protezione.
- Il master MAIN V2.6 non viene modificato; la BOM di 138 riferimenti riguarda ancora il solo master. I draft PSU 10 refs, audio LM386 12 refs e volume FRONT 3 refs sono schemi aggiuntivi NON integrati. Non sono layout sbrogliati e non esiste DRC PCB.

**Stato convalida:** i test locali non si dichiarano eseguiti; il passaggio obbligatorio è KiCad9 ERC+netlist nativi su CI della PR nello SHA finale, comprendendo i due schemi e i test storici. Non bypassare gate di produzione. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
