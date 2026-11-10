# V0.2 — Piano frequenze e confronto PLL tradizionali THT

**SOLO STUDIO RX / ARITMETICA, nessuna produzione o TX.** La tabella `PIANO_RX_PLL_270_V0.2.csv` è derivata dalle tabelle pubblicate del Superstar 3900 e dai canali ALFA a +10 kHz: 6 bande A–F, 40 normali + 5 ALFA (3A, 7A, 11A, 15A, 19A) per banda, per **270 frequenze RX distinte** da **25,615 a 28,305 MHz**. I canali CB 23, 24, 25 conservano l'ordine storico non crescente. Il canale prioritario CH9 è D/9 = 27,065 MHz AM.

**Fonti indipendenti:** https://cbtricks.org/radios/superstar/3900/ss3900_band_chart_a.htm e https://cbtricks.org/radios/superstar/3900/ss3900_band_chart_b.htm . Le tabelle storiche riportano anche frequenze TX, qui riutilizzate **solo come riferimenti per la ricezione**, non come permessi di trasmissione.

## Conversione scelta per lo STUDIO, ancora da confermare

IF1 candidata = **10.695.000 Hz**; high-side injection `LO1 = RF + IF1`, quindi 36.310.000–39.000.000 Hz. Immagine di prima conversione `RF_image = RF + 2×IF1`, 47.005.000–49.695.000 Hz. Questi sono prodotti algebrici, NON attenuazioni misurate. Seconda IF candidata 455 kHz tramite LO2=10,240 MHz; seconda immagine di conversione FI1 a 9,785 MHz, necessità di filtri veri.

## Alternativa A — MC145151-2 in DIP + divisore /2, preferita solo se reperibile

- Quarzo THT candidato **10.240.000 Hz**, divisore interno `R=2048` del MC145151-2: `fPFD=5.000 Hz`.
- VCO RF esterno THT 36,310–39,000 MHz → buffer/limitatore → **SN74AC74N** in PDIP14 usato come divisore fisso /2.
- Ingresso `fIN` del PLL 18,155–19,500 MHz; divisore programmabile `N = fLO / (2×fPFD) = fLO / 10.000`: **N=3631..3900**, tutti interi a 14 bit (vedere CSV).
- **Non** immettere direttamente 36–39 MHz nel PLL: datasheet MC145151 documenta limiti inferiori. Per ingresso CMOS a circa 5 V è riportata una frequenza massima dell'ordine di 22 MHz secondo condizioni specificate: verificare livelli, forme d'onda e temperatura all'interfaccia divisa.
- Sul MC145151 l'ingresso `T/R` **basso** aggiunge offset fisso +856 ai divisori: per RX candidato deve rimanere **alto**; non considerarlo un abilitazione TX.
- Datasheet: https://www.nxp.com/docs/en/data-sheet/MC145151-2.pdf ; stato di produzione: https://www.nxp.com/products/MC145151_2 . NXP indica **No Longer Manufactured**, trasferimento storico a Lansdale. Quindi **disponibilità, autenticità e affidabilità sono un gate aperto**.
- Divisore SN74AC74N: https://www.ti.com/product/SN74AC74/part-details/SN74AC74N ; integrato THT PDIP14 con clock nominale ben oltre i 39 MHz nel product page TI. Resta da progettare e misurare l'interfaccia elettrica.

## Alternativa B — CD74HC4046AE e contatori programmabili THT

- **CD74HC4046AE** in PDIP16 usato come comparatore di fase e non come generatore LO: il suo VCO interno fino a circa 18 MHz *tipici* non costituisce un LO da 36–39 MHz.
- VCO RF esterno THT, divisore /2 (SN74AC74N), confronto fPFD 5 kHz da quarzo e contatore programmabile `N=3631..3900` con più stadi **74AC161 DIP** (es. Toshiba TC74AC161P).
- Non è stata dimostrata la temporizzazione delle catene a 18–19,5 MHz; servono schema sincrono di conteggio, preset, carry e analisi glitch. L'impiego diretto di `SN74HC161N` multistadio senza verifica non è accettato, dato l'avviso TI sui limiti/glitch della catena HC161.
- Fonti: https://www.ti.com/product/CD74HC4046A ; https://toshiba.semicon-storage.com/us/semiconductor/product/general-purpose-logic-ics/detail.TC74AC161P.html ; https://www.ti.com/product/SN74HC161 .

## Decisione provvisoria e criticità aperte

| Criterio | A MC145151P2 | B CD74HC4046AE + AC161 |
|---|---|---|
| THT | Documentato PDIP28, ma legacy | PDIP16 + DIP14/16 candidati |
| 270 posizioni RX con N intero | Matematicamente SÌ | Matematicamente SÌ |
| Reperibilità | **CRITICA** | Verificare componenti e alternative |
| Programmazione di N | 14 linee parallele, controller da studiare | Caricamento/contatore sincrono ancora da progettare |
| Circuito / timing / VCO / loop | **NON VALIDATI** | **NON VALIDATI** |
| KiCad/SPICE/EM/hardware | **NON ESEGUITI** | **NON ESEGUITI** |

**Nessun circuito o componente è approvato all'acquisto.** In V0.3: reperibilità verificata, pinout, margini temporali, alimentazioni e loop/VCO reali; nessun collegamento al TX.
