# V0.2 — Rapporto tecnico: piano RX e PLL THT candidato

**10 novembre 2026.** Fonte tecnica: dati storici CBTricks per le frequenze, datasheet e pagine produttore NXP/TI/Toshiba per i componenti.

## Lavoro nuovo
- Frequenze **270/270 posizioni**, 6 bande × (40 + 5 ALFA), range 25,615..28,305 MHz. 30 posizioni ALFA; priorità CH9 D/9 a 27,065 MHz AM; ordine storico 23, 24, 25 rispettato.
- IF1 candidata 10,695 MHz, LO high-side 36,310..39,000 MHz; immagini RF 47,005..49,695 MHz. Nessun filtro fisico disegnato.
- Identità PLL: quarzo 10,240 MHz /2048 = 5 kHz; divisore /2; N=3631..3900, 14 bit, valido aritmeticamente su tutte le 270 posizioni. Ingresso PLL a 18,155..19,5 MHz.
- Confronto A MC145151P2 (PDIP28 legacy non più prodotto NXP) + SN74AC74N e B CD74HC4046AE + contatori 74AC161 DIP e VCO esterno. Entrambe richiedono ulteriori controlli.
- BOM di soli componenti candidati, contratto logico delle interfacce, sorgente rigenerabile e codice test.

## Verifiche eseguite (software, non simulazioni elettriche)
| Verifica | Esito | Limite |
|---|---|---|
| `python3 -m unittest discover -s 03_Verifiche/V0.2 -p 'test_*.py' -v` | **24 PASS, 0 FAIL, 0 SKIP** nel modello di preparazione | Controllo aritmetico, file e invarianti |
| Regressione V0.1 `python3 -m unittest discover -s 03_Verifiche/V0.1 -p 'test_*.py' -v` | **12 PASS, 0 FAIL, 0 SKIP** | Baseline documentale |
| Matrice RX completa | **270/270** linee generate, **30/30** ALFA, **1/1** CH9 prioritario | Non prova ricevibilità o local oscillator lock |
| Algebre LO/immagini/N | **270/270** coerenti | Non prova rumore, armoniche, reiezione |

**NON ESEGUITI:** KiCad schematici, ERC/DRC, SPICE e simulazioni vendor, dimensionamento VCO/loop filter, S-parameters, hardware e misure reali. Nessuna produzione o TX.

## Rischi aperti
1. MC145151P2 è documentato PDIP, ma NXP lo indica 'No Longer Manufactured': selezionarlo solo dopo accertamenti commerciali e autenticità. Fonte: https://www.nxp.com/products/MC145151_2
2. MC145151 non può ricevere 36–39 MHz direttamente nel `fIN`: necessario /2 THT, verifica livelli e forme d'onda; mantenere `T/R` a livello RX alto per evitare offset interno +856. Fonte: https://www.nxp.com/docs/en/data-sheet/MC145151-2.pdf
3. Alternativa 4046/contatori: 4046 non fornisce direttamente 36–39 MHz; sono da progettare dividers, preload sincrono, drive, filtro fase, schermature e VCO esterno.
4. LO, IF1 e immagine sono relazioni candidate; front-end THT e filtri da sviluppare.

**VERDETTO:** V0.2 = baseline matematica e analisi di fattibilità. **NO FAB / NO TX.**
**Prossima V0.3:** scelta e disegno circuitale THT del PLL con componenti reali/part numbers verificati, senza liberare TX.


## GitHub Actions verificata dopo integrazione
- **Run ID**: [42803142196](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42803142196)
- **Commit testato**: `7da67271bc9c33416b695053c4e9d9ed1f1f60b2` (V0.2).
- **Job `static-regression`**: `success`; verificati i passi `Baseline V0.1 structural tests` e `V0.2 channel plan and candidate PLL arithmetic tests`, entrambi `success`.
- Si tratta **solo** di test Python riproducibili. KiCad, SPICE, hardware e TX rimangono **NON ESEGUITI**.
