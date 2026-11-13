# V2.7 — trade-off resistenze di carico e rumore RF IF455, 30 AC nativi

**13 novembre 2026. Screening del solo filtro IF455 passivo; non approvazione di guadagno/sensibilità radio.**

## Motivo del test

La [PR #113](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/113) (MERGED `276918b93ae6a26540abee83f22711a10ae4e88d`) ha quantificato a 290K nel solo modello i contributi termici: alla porta con R1601=47kΩ, R1602=100kΩ, rumore RF `23,17706 nV/√Hz` a 455kHz (2,063867µV RMS su banda RF 451–459k), e input-referred al generatore ideale `27,75511 nV/√Hz`. Con ingresso gate JFET surrogato passivo 10p/1M/7p: `18,59163 nV/√Hz`, `1,654389µV RMS`, `27,94949 nV/√Hz` input-referred. **Il rumore riferito alla sorgente quasi non cambia se si abbassa semplicemente il trasferimento**. Contributi dominanti nel riferimento: R1601 damping 47k (~17,051nV/√Hz) e R1602 load 100k (~14,775nV/√Hz), non RGEN 50Ω (~0,747nV/√Hz).

## Esperimento sostanziale su componenti reali del circuito

Nuovo script `03_Verifiche/V2.7/verify_if455_passive_resistor_noise_load_tradeoff_native.py` e runner FULL: **3 valori dello smorzamento R1601 (47k / 100k / 220k)** × **2 valori del carico R1602 (100k / 220k)** = sei configurazioni, ciascuna misurata con cinque ngspice AC nativi (sorgente utile e rumore equivalente indipendente dei quattro resistori RGEN/RCOIL/RDAMP/RLOAD) = **30 esecuzioni**. Rete IF455 altrimenti identica: L1mH, C82p + Ctrim30p, C ingresso/uscita10p, Rcoil=16,5Ω RF assunto, generatore 50Ω, temperatura290K, RF 451–459kHz passo100Hz.

Per ogni combinazione sono riportati il vero `|H(455k)|` del generatore al port, il rumore a 455kHz [nV/√Hz], il rumore integrato nella finestra RF 8kHz [µV rms], il rumore diviso per `|H(455k)|` **riferito alla sorgente idealizzata**, e i singoli contributi di rumore. I test verificano la riproduzione della PR #113 per R47k/R100k e la reciprocità del trasferimento della sorgente termica serie del generatore RGEN rispetto alla sorgente ideale. L'ordinamento per rumore minimo input-referred è **solo matematico e non elegge alcun valore definitivo**.

## Vincoli di decisione

- Rimuovere damping o aumentare Rload può migliorare l'ampiezza o ridurre alcune sorgenti di rumore **ma cambia Q, banda, selettività e accordo**, perciò nessun 'ottimo' sarà accettato prima di un criterio multi-banda e dell'identificazione della rete mixer/IF reale.
- Rcoil=16,5Ω come ESR AC non è qualificata a 455kHz; non sono rappresentati rumore dei dispositivi attivi, temperature, alimentazioni, leakage di diodo, rumore AGC, banda e guadagno del mixer. Il noise-referred a una sorgente `VSIGNAL` di banco **non è noise figure e non è sensibilità d'antenna/SINAD**.
- Test limitato a **una frequenza IF** e un intervallo RF di 8kHz convenzionale; non è la ricostruzione del rumore audio dopo un demodulatore non lineare, né un modello di ricevitore AM/FM/SSB. Il fatto di ridurre RMS non prova l'assenza di interferenti o la selettività.
- I componenti resistivi R/C standard sono ammissibili allo **stadio schematico** secondo ADR-002, ma nessuno di questi sei accoppiamenti è stato approvato per la PCB; non esiste un PCB reale da sottoporre a DRC. Il master KiCad V2.6 resta intatto.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
