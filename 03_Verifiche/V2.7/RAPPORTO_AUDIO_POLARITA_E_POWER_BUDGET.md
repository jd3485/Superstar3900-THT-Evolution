# V2.7 DRAFT — Auditing polarità elettrolitici e limiti alimentazione LM386

**Data:** 13 novembre 2026. **Campo:** sottosistema audio RX MAIN THT autonomo, non master V2.7 completo. Riferimento primario [Texas Instruments LM386 datasheet SNAS545D, revisione agosto 2023](https://www.ti.com/lit/ds/symlink/lm386.pdf), §6.5 e §9.

## Modifica CAD effettiva
Il simbolo locale/embedded `TH_AUDIO:CP` usava pin generici `1` e `2`. La nuova revisione nomina **pin 1 `POS_+`** e **pin 2 `NEG_-`** in `TH_AUDIO.kicad_sym` e nel foglio `AUDIO_RX_MONO_LM386_V2_7_DRAFT.kicad_sch`, conservando numerazione, riferimenti e **tutte le reti esistenti**. Il numero 1 è il pad positivo del footprint THT radiale KiCad, da confrontare comunque col datasheet e la serigrafia del componente OEM finale.

| Componente | Terminale positivo, pin 1 | Terminale negativo, pin 2 | Verifica |
|---|---|---|---|
| **C1202**, 220 µF / 16 V | `AMP_OUT` (LM386 uscita a ~Vcc/2 a riposo) | `SPK_HOT` (attraverso speaker verso massa) | Pin positivo verso IC |
| **C1204**, 10 µF / 16 V | `BYPASS` (pin 7 LM386) | `GND` | Nodo bypass e massa, tensione da confermare |
| **C1206**, 100 µF / 16 V | `AUDIO_5V` | `GND` | Disaccoppiamento corretto |

Il test native KiCad9 `03_Verifiche/V2.7/verify_audio_draft_native.py` controlla adesso la concordanza delle due definizioni del simbolo e la **membership pin↔net esportata da KiCad9** per tutti e 3 gli elettrolitici. Un semplice ERC0 non verifica automaticamente il verso elettrolitico: è obbligatorio anche questo contratto. Nessun ERC waiver o sostituzione di MPN.

## Alimentazione audio: prima quantificazione delle limitazioni

Il costruttore indica **LM386N-1**: tensione operativa 4–12 V; corrente a riposo **4 mA tipica / 8 mA massima a 6 V**, ingresso 50 kΩ tipici, guadagno a pin 1/8 aperti 20 V/V. **325 mW tipici e 250 mW minimi su 8 Ω a 6 V con 10% THD**: questi valori **non sono specifiche garantite a 5 V**, e non soddisfano necessariamente il requisito audio di un CB veicolare. Il massimo ambientale nominale è +70 °C: esaminare temperatura interna reale prima di approvare questa scelta. [Pagina OEM del codice esatto LM386N-1/NOPB](https://www.ti.com/product/LM386/part-details/LM386N-1/NOPB).

### Calcoli elementari di riferimento (non misure né worst-case OEM)
Per un altoparlante **8 Ω** trattato come puramente resistivo, a **100 mW RMS**:
- `V_RMS = sqrt(0.1 W × 8 Ω) ≈ 0.894 V`;
- `I_RMS = sqrt(0.1 W / 8 Ω) ≈ 0.112 A`, `I_PEAK ≈ 0.158 A`;
- la corrente d'alimentazione pulsata, il limite stadio di uscita, perdite e corrente al rail **non si ottengono equiparando** la corrente altoparlante alla corrente di riposo. Riserva di corrente, stabilità e dissipazione vanno ottenute dai profili di carico e test reali.

Accoppiamento uscita **C1202 220 µF**: usando modello RC ideale, 8 Ω → `f_c ≈ 90.4 Hz`, 4 Ω → `f_c ≈ 180.9 Hz`; non è una misura sulla radio e dipende dall'impedenza dell'altoparlante, perdita, ESR e tolleranza del condensatore. Non dedurre risposta musicale o THD.

## Decisioni aperte
1. Il bench **+5V del connettore J1201** non deve essere collegato automaticamente al 7805 PLL o ai rail RF. Progettare sorgente dedicata, filtraggio, ritorno audio, soppressione rumore e protezioni con corrente e dissipazione realistiche.
2. Fissare obiettivo acustico (impedenza/dimensione altoparlante, livello sonoro e THD) prima di bloccare LM386 e selezionare la tensione della sezione; la specifica a **6V** non si trasferisce a **5V**.
3. I tre condensatori richiedono MPN THT attivamente prodotti, temperatura, ingombri e vita utile, ESR/ripple e corrispondenza fisica di marcatura **+ e -**. Nessun produttore OEM finale di C1202/1204/1206 selezionato.
4. Per la FRONT, il pot 10k lineare è provvisorio; andamento volume, guadagno effettivo con R1201 da 10k, cavo a due fili e demod RX richiedono ancora un progetto di sistema.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.** Master MAIN V2.6 invariato, scheda non sbrogliata, nessun DRC su PCB reale o SPICE vendor dichiarato. Solo se CI nativa sullo SHA finale è verde il pilot modificato potrà essere integrato.
