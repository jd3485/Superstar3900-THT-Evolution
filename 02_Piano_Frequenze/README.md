# Piano frequenze — V0.1

Il requisito è **270 posizioni RX**: 6 bande A–F, ciascuna con 40 canali normali e 5 ALFA. Non significa automaticamente 270 frequenze univoche, e non costituisce autorizzazione TX.

Il file `PIANO_FREQUENZE_RX_DA_COMPILARE_V0.2.csv` contiene **solo l'intestazione**: nessuna frequenza è stata inventata.

## Compiti per V0.2
1. Definire l'elenco verificato di frequenze RX, con posizioni e selettore ALFA, riferimenti e criteri per CH9 27,065 MHz AM.
2. Stabilire la prima/seconda FI e gli schemi possibili di conversione (alto/basso) con conseguenti frequenze immagine.
3. Confrontare almeno due soluzioni di sintesi coerenti con **solo THT**: PLL classico programmabile e alternativa tradizionale, includendo datasheet, disponibilità e compromessi su passo/stabilità/spurie.
4. Definire procedure di test automatiche per 270 posizioni, limiti di freq e assenza di TX non autorizzata.
5. Solo dopo: tabella programmabile, assegnazioni pin e selezione concreta MPN.
