# V2.7 DRAFT — Sezione audio RX THT isolata, non integrata al master

**12 novembre 2026.** Prima modifica KiCad di un sottosistema indipendente dopo ADR-002. Non è l'intera V2.7, né un ricevitore funzionante, né il progetto PCB. Il master MAIN V2.6 (7 fogli, 138 posizioni) e i suoi generatori sono lasciati **bit-for-bit immutati**.

## Nuovo schematico nativo
`04_KiCad/V2.7_DRAFT/AUDIO_RX_MONO_LM386_V2_7_DRAFT.kicad_sch` contiene **9 dispositivi fisici THT**:

- U1201: amplificatore Texas Instruments **LM386N-1/NOPB** (PDIP-8, 0..70 °C) marcato **ACTIVE** dal produttore al controllo del 12/11/2026; *non provata acquistabilità immediata*: pagina ufficiale indica «Out of stock». OEM: https://www.ti.com/product/LM386/part-details/LM386N-1/NOPB . Datasheet: https://www.ti.com/lit/ds/symlink/lm386.pdf .
- C1201 100 nF ingresso; R1201 10 kΩ in serie dall'ingresso al pin 3 (limita/ripartisce insieme all'impedenza interna, **non** sostituisce regolazione volume); guadagno interno 20 (pin 1/8 lasciati NC espressamente).
- C1202 220 µF / 16 V accoppiamento altoparlante (terminale **positivo** verso l'uscita LM386 polarizzata a ~metà Vcc); C1203 47 nF / 50 V e R1202 10 Ω rete Zobel serie; C1204 10 µF / 16 V dal pin BYPASS a GND.
- C1205 100 nF / 25 V e C1206 100 µF / 16 V bypass locale del rail +5V (alimentazione **NON** connessa al master V2.6). R, C e footprint passivi sono **candidati generici THT**, da qualificare per tensione, ESR/ripple, dimensioni e performance prima del layout/release.

I nove simboli hanno footprint THT valorizzati; la libreria è embedded per preservare significato dei pin; riferimenti U1201/R1201/R1202/C1201..C1206. Interfacce preliminari: `AUDIO_IN`, `AUDIO_5V`, `GND`, `SPK_HOT`; altri nodi sono interni. La connessione all'uscita del demodulatore, volume sul frontalino PCB-FRONT e schema speaker/altoparlante sono **ancora assenti**.

## Fonte e dimensionamento preliminare
TI, LM386 datasheet SNAS545D, §9.2.1, indica uso di 10k potenziometro in ingresso, gain 20, 250µF di uscita, Zobel 50nF + 10Ω e alimentazione 5–12V per LM386N-1. Questo pilot usa **220µF** per un valore THT comune: il suo polo RC con 8Ω ideale sarebbe `1/(2*pi*8*220e-6)=90.4 Hz`, **solo** stima ideale e non misura di risposta reale. L'ingresso usa R da 10k anziché un potenziometro; guadagno e livelli di ingresso effettivi sono da progettare dopo verifica demod e desiderata escursione del volume. La rete Zobel 47nF differisce da 50nF nello schema tipico: da convalidare con stabilità al carico reale.

**Attenzione energia 5V:** non basta avere una rail 5V del PLL per alimentarci l'amplificatore. **Il rail +5V già esistente NON viene collegato per impostazione predefinita**: corrente di picco, rumore di audio, dissipazione U601 7805, compatibilità RF e ciclo di massa da valutare prima di integrare al MAIN. Il design definitivo può richiedere un'alimentazione dedicata e separata dai circuiti RF/PLL. Il limite ambientale OEM 0..70°C deve essere coerente con l'applicazione finale.

## Gate effettivo proposto
`03_Verifiche/V2.7/verify_audio_draft_native.py` deve essere eseguito dalla CI FULL (aggiornato `ci/full_regressions.py`) per fare **vero** `kicad-cli sch erc --exit-code-violations`, esportare la netlist KiCad9 e controllare nove refs e reti. Se il gate non passa, **NON fondere** la PR; correggere l'errore nei file schematici o validatore e ripetere test su SHA finale. Verifiche passate storiche V2.6 non costituiscono un ERC del pilot.

## Non approvato / passi successivi
- ERC/netlist native e connessioni pin-net fino a CI finale verde;
- specifica audio RX, collegamento al demod AM/FM, guadagno/volume e NF, speaker/FRONT;
- carico reale 8 Ω, distorsione a 5 V, dissipazione e transienti; simulazione elettrica vendor o banco (non eseguiti);
- riferimento di massa, alimentazione ad alta corrente separata e isolamento dai rail sensibili;
- conformità THT passivi (MPN OEM finale), compatibilità fabbricazione PCB e sicurezza.

**NO FAB / NO GERBER / NO TX / NO VEICOLO / NO BATTERIA.** Il gate globale BOM rimane bloccato sui 138 del master V2.6 e si estenderà ai nuovi riferimenti quando si integrerà il sottosistema.
