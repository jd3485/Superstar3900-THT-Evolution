## Risultato finale validato e integrato (12 novembre 2026)

**La PR #52 è stata integrata**: merge `78f077a9132a2067d50330d8a5bcbdc62ba4b3f3`; test su final head `7e07cc47b7421048ccaa1670e75daebe088f6c5a`, [Actions #43254795252](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43254795252), **3/3 PASS**. Esito nativo documentato nei log: `Found 0 violations`, `ERC messages: 0 Errors 0 Warnings`, `PASS_KICAD9_AUDIO_DRAFT_ERC0_NETLIST_12_THT`, eseguite 22 suite legacy + il nuovo pilot. Nessun DRC perché nessuna PCB audio fisica è stata disegnata.

Questa conferma di corretta connettività/sintassi KiCad **non è una certificazione** della stabilità, THD, potenza, sicurezza, budget dei 5 V, compatibilità elettrica con il resto del ricevitore o disponibilità dei passivi. Il foglio è DRAFT standalone, non collegato alla gerarchia MAIN V2.6 e non alimentabile da veicolo.

# V2.7 DRAFT — Sezione audio RX THT isolata, non integrata al master

**12 novembre 2026.** Prima modifica KiCad di un sottosistema indipendente dopo ADR-002. Non è l'intera V2.7, né un ricevitore funzionante, né il progetto PCB. Il master MAIN V2.6 (7 fogli, 138 posizioni) e i suoi generatori sono lasciati **bit-for-bit immutati**.

## Nuovo schematico nativo
`04_KiCad/V2.7_DRAFT/AUDIO_RX_MONO_LM386_V2_7_DRAFT.kicad_sch` contiene **12 dispositivi fisici THT**:

- J1202 e J1203: connettori THT a due vie per ingresso AF e uscita speaker, rispettivamente. Segnale e ritorno GND espliciti; connettori solo per laboratorio, da sostituire/rivedere nel sistema completo.
- J1201: connettore THT a 2 vie **solo per alimentazione da banco +5V regolata**; nella libreria custom, pin 1/2 sono modellati come uscite di potenza dell'alimentatore esterno, **non** come capacità della 5V del master radio. Non è un'alimentazione interna da montare sulla radio finale e non autorizza batterie/veicolo.
- U1201: amplificatore Texas Instruments **LM386N-1/NOPB** (PDIP-8, 0..70 °C) marcato **ACTIVE** dal produttore al controllo del 12/11/2026; *non provata acquistabilità immediata*: pagina ufficiale indica «Out of stock». OEM: https://www.ti.com/product/LM386/part-details/LM386N-1/NOPB . Datasheet: https://www.ti.com/lit/ds/symlink/lm386.pdf .
- C1201 100 nF ingresso; R1201 10 kΩ in serie dall'ingresso al pin 3 (limita/ripartisce insieme all'impedenza interna, **non** sostituisce regolazione volume); guadagno interno 20 (pin 1/8 lasciati NC espressamente).
- C1202 220 µF / 16 V accoppiamento altoparlante (terminale **positivo** verso l'uscita LM386 polarizzata a ~metà Vcc); C1203 47 nF / 50 V e R1202 10 Ω rete Zobel serie; C1204 10 µF / 16 V dal pin BYPASS a GND.
- C1205 100 nF / 25 V e C1206 100 µF / 16 V bypass locale del rail +5V (alimentazione **NON** connessa al master V2.6). R, C e footprint passivi sono **candidati generici THT**, da qualificare per tensione, ESR/ripple, dimensioni e performance prima del layout/release.

I dodici simboli hanno footprint THT valorizzati; la libreria è embedded per preservare significato dei pin; riferimenti U1201/R1201/R1202/C1201..C1206/J1201/J1202/J1203. La libreria custom `TH_AUDIO.kicad_sym` è registrata da `sym-lib-table` della cartella pilot. Interfacce preliminari: `AUDIO_IN`, `AUDIO_5V`, `GND`, `SPK_HOT`; altri nodi sono interni. La connessione all'uscita del demodulatore, volume sul frontalino PCB-FRONT e schema speaker/altoparlante sono **ancora assenti**.

## Fonte e dimensionamento preliminare
TI, LM386 datasheet SNAS545D, §9.2.1, indica uso di 10k potenziometro in ingresso, gain 20, 250µF di uscita, Zobel 50nF + 10Ω e alimentazione 5–12V per LM386N-1. Questo pilot usa **220µF** per un valore THT comune: il suo polo RC con 8Ω ideale sarebbe `1/(2*pi*8*220e-6)=90.4 Hz`, **solo** stima ideale e non misura di risposta reale. L'ingresso usa R da 10k anziché un potenziometro; guadagno e livelli di ingresso effettivi sono da progettare dopo verifica demod e desiderata escursione del volume. La rete Zobel 47nF differisce da 50nF nello schema tipico: da convalidare con stabilità al carico reale.

**Attenzione energia 5V:** non basta avere una rail 5V del PLL per alimentarci l'amplificatore. **Il rail +5V già esistente NON viene collegato per impostazione predefinita**: corrente di picco, rumore di audio, dissipazione U601 7805, compatibilità RF e ciclo di massa da valutare prima di integrare al MAIN. Il design definitivo può richiedere un'alimentazione dedicata e separata dai circuiti RF/PLL. Il limite ambientale OEM 0..70°C deve essere coerente con l'applicazione finale.

## Gate effettivo proposto
`03_Verifiche/V2.7/verify_audio_draft_native.py` deve essere eseguito dalla CI FULL (aggiornato `ci/full_regressions.py`) per fare **vero** `kicad-cli sch erc --exit-code-violations`, esportare la netlist KiCad9 e controllare dodici refs e reti. Se il gate non passa, **NON fondere** la PR; correggere l'errore nei file schematici o validatore e ripetere test su SHA finale. Verifiche passate storiche V2.6 non costituiscono un ERC del pilot.

## Non approvato / passi successivi
- ERC/netlist native e connessioni pin-net fino a CI finale verde;
- specifica audio RX, collegamento al demod AM/FM, guadagno/volume e NF, speaker/FRONT;
- carico reale 8 Ω, distorsione a 5 V, dissipazione e transienti; simulazione elettrica vendor o banco (non eseguiti);
- riferimento di massa, alimentazione ad alta corrente separata e isolamento dai rail sensibili;
- conformità THT passivi (MPN OEM finale), compatibilità fabbricazione PCB e sicurezza.

**NO FAB / NO GERBER / NO TX / NO VEICOLO / NO BATTERIA.** Il gate globale BOM rimane bloccato sui 138 del master V2.6 e si estenderà ai nuovi riferimenti quando si integrerà il sottosistema.

## Correzione dopo primo ERC KiCad9 (run #43253022016)
La prima prova nativa del foglio isolato ha dato **48 segnalazioni: 8 errori / 40 warning** (source: https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43253022016). Diagnosi dettagliata: etichette gerarchiche sul root senza parent, alimentazione +5V e GND non dichiarata, coordinate off-grid e libreria custom non registrata. Correzioni CAD: sostituite solo etichette root con locali, tutte le coordinate di collegamento allineate a 1.27mm, registrata la libreria locale, esplicitato con J1201 il banco di prova 5V + GND (solo nel pilot). **Nessun waiver ERC o mancata verifica intenzionale**. Un nuovo test KiCad nativo su HEAD finale deve dimostrare i risultati: la descrizione delle correzioni NON è una dichiarazione anticipata di ERC=0.

## Secondo rapporto ERC e modifica di interfacce (run #43254009373)
La revisione con coordinate sulla griglia e alimentazione da banco ha ridotto le segnalazioni da **48 a 12**, cioè da 8 errori a **2 errori**, rimasti su due etichette locali terminali non terminate, e 10 warning sulla libreria custom TH_AUDIO non vista come configurata. Azioni: inseriti **connettori fisici THT J1202 (AF-IN) e J1203 (SPK-OUT)** con segnale e ritorno a GND per evitare label libere e per stabilire un contratto d'interfaccia verificabile. Aggiunto file progetto **.kicad_pro** alla cartella con simbologia specifica e `sym-lib-table`, per caricare la tabella librerie locali KiCad. **La prova nativa va ripetuta**: non dichiarare ERC0 sulla base della sola correzione proposta.
