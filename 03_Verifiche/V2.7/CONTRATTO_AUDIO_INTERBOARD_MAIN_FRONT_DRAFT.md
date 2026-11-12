# CONTRATTO ELETTRICO AUDIO MAIN ↔ FRONT, bozza V2.7 (12/11/2026)

## Stato e perimetro
Definizione **logica e verificabile mediante netlist native KiCad9** della tratta audio tra le due PCB previste da ADR-001. I due schemi restano **DRAFT standalone**, non sono connessi in una gerarchia unica, non esiste la PCB, non esiste un cablaggio fisico validato, nessun connettore OEM definitamente selezionato. Non è un test della qualità audio né un'autorizzazione di fabbricazione.

## Mappa provvisoria cablaggio FRONT → MAIN

| Scheda | Connettore | Pin | Rete/uso | Destinazione dichiarata |
|---|---|---:|---|---|
| FRONT | J1301 | 1 | DEMOD_AUDIO, ingresso AF dal futuro demodulatore | RV1301 pin 1 |
| FRONT | J1301 | 2 | AF_GND | RV1301 pin 3 / massa del segnale |
| FRONT | RV1301 | 1 | TRACK_HIGH / DEMOD_AUDIO | J1301 pin 1 |
| FRONT | RV1301 | 2 | VOL_WIPER_TO_AMP | J1302 pin 1 |
| FRONT | RV1301 | 3 | TRACK_LOW / AF_GND | J1301 pin 2 e J1302 pin 2 |
| FRONT | J1302 | **1** | segnale regolato | **MAIN J1202 pin 1** |
| FRONT | J1302 | **2** | massa audio | **MAIN J1202 pin 2** |
| MAIN audio RX | J1202 | 1 | AUDIO_IN | C1201 → R1201 → LM386 U1201 pin 3 |
| MAIN audio RX | J1202 | 2 | GND | GND LM386 pin 4 |

Il cablaggio logico richiede **2 conduttori**: segnale AF e ritorno AF. Non attraversa il cavo alcun rail +5V, PA power o linea TX. La sorgente audio demodulata e l'instradamento fisico della massa restano da progettare. La rete GND locale del foglio audio MAIN sarà da coordinare con la strategia di massa e schermatura della radio, non da unire indiscriminatamente a tutte le masse.

## Alimentazione audio separata
Il pilot MAIN audio contiene **J1201 +5 V da banco**, con rail `AUDIO_5V` distinto dalla `+5V` RF/PLL. Per la radio integrata deve essere valutata una sorgente audio propria: margine di corrente LM386 per speaker nominale, dissipazione, stabilità, transitori, isolamento ripple RF, ground return, cavi di massa e armoniche. L'attuale PSU da laboratorio non è soluzione di produzione. Nessun collegamento alla batteria o al veicolo autorizzato.

## Criticità ancora aperte
- **Compatibilità connettori:** i disegni assegnano footprint THT generico `PinHeader_1x02` a entrambe le estremità, quindi **due pin header maschi NON sono una coppia ad innesto diretto**. Per creare il cablaggio reale serviranno appropriati contatti femmina crimpati e corpi isolanti, oppure una coppia maschio-femmina qualificata; bisogna verificare orientamento pin 1, passo, blocco, corrente, guaina, lunghezza e protezione contro inserimento errato. Non ordinare la PCB sulla base di questa sola tabella.
- **Potenziometro 10 kΩ lineare:** legge volume (probabile necessità di taper audio), impedenza vista dal demodulatore, rumore del cursore, forma albero/frontale e footprint a tre pad PROVVISORIO richiedono qualifica OEM prima del layout finale. Il `R1201=10k` del MAIN audio è ancora in serie; calcolare il carico reale e curva di regolazione.
- **Demod RX assente:** J1301 è una porta aperta di segnale, non un collegamento fatto al ricevitore completo.
- **Vincolo ADR-002:** MPN esatto dei passivi standard non necessario per disegnare nuovi schemi indipendenti; BOM finale deve comunque certificare i pezzi montati. Per U401/L501/RF e protezioni valgono gate dedicati.

## Gate software aggiunto
`03_Verifiche/V2.7/verify_interboard_audio_contract_native.py` esporta entrambe le netlist reali mediante `kicad-cli sch export netlist`, esamina l'appartenenza **pin-per-pin** alle reti per J1301, RV1301, J1302, J1202, C1201 e U1201, e confronta il contratto 1→1, 2→2. Se cambiano in modo incompatibile pin, net o referenze, fallisce. Viene eseguito dal gate FULL in `ci/full_regressions.py`, oltre a ERC dei due fogli, e non disabilita alcun controllo preesistente. **L'esito reale sarà confermato dalla CI sul commit finale**, non presunto da questo rapporto.

## Completamento progetto: stima, non misura
Alla data 12/11/2026, la stima gestionale complessiva delle due PCB dalla progettazione degli schemi fino ai Gerber verificati è **circa 20%**, con ampio margine d'incertezza, perché NON esistono layout o netlist integrate MAIN+FRONT. Progresso del routing fisico PCB: **0%**. Questo valore NON deriva da `6/138 MPN ACTIVE`, che riguarda esclusivamente il gate fabbricazione della BOM V2.6. La presente PR può aumentare la maturità dei contratti senza implicare una variazione percentuale misurabile.

**STOP FAB / NO GERBER / NO TX / NO BATTERIA-VEICOLO**. Master MAIN V2.6 intatto; le DRAFT standalone non ampliano implicitamente il denominatore BOM 138 posizioni.
