# Schema a blocchi V0.1 — non circuitale

```mermaid
flowchart TD
    ANT[Connettore antenna] --> SW[Commutazione e protezione RX]
    SW --> PRE[Preselettore THT]
    PRE --> RX1[Mixer RF / FI1 candidata]
    PLL[PLL classico + VCO/divisori THT] --> RX1
    RX1 --> IF[FI, filtri, AGC, LO2 e BFO]
    IF --> DEM[Demod AM/FM/USB/LSB/CW]
    DEM --> AF[Squelch + audio analogico]
    AF --> SPK[Amplificatore THT e altoparlante]
    MIC[Microfono] --> TX[Modulatore/driver/PA TX - STUDIO BLOCCATO]
    TX -. NESSUN COLLEGAMENTO FISICO .-> TUNE[Tuner LC manuale + BYPASS]
    TUNE -. TX NON AUTORIZZATA .-> ANT
```

I tratteggi TX indicano **assenza di collegamento elettrico autorizzato**, non fili da implementare. L'architettura è candidato funzionale, non uno schema KiCad.
