# V2.7 — IF455 → AM455 non lineare → FRONT volume → ingresso LM386: carico reale passivo, diodo generico

**15 novembre 2026.** Revisione tecnica della catena RX AM di banco dopo PR #232 (75 test AC/KCL senza generazione IF) e PR #233 (300 scenari Rsource lineari). La nuova prova esegue realmente un filtro IF 455 kHz pilotato con portante AM da generatore ideale, diodo **DGENERIC non OEM**, rete di inviluppo AM455 e carico del potenziometro/frontale/ingresso LM386. **Non** è una simulazione OEM e non caratterizza una radio sensibile e selettiva.

## Deck e topologia

`03_Verifiche/V2.7/spice/if455_am455_front_lm386_loaded_generic_diode.cir` conserva integralmente il ramo baseline IF455→D1501→AF con terminazione R1502=100 kΩ, più riferimento diretto storico; aggiunge un **secondo ramo indipendente e identico** generatore 455 kHz, tank, Rcoil 16,5Ω ipotizzata, trimmer 30pF, diodo generico con identici parametri, RC R1501=47 kΩ/C1501=1 nF e uscita C1502=100 nF/R1502=100 kΩ. Il secondo ramo incorpora la rete di carico dei **veri valori schematici** FRONT RV1301=10 kΩ, condensatore C1201=100 nF, resistenza R1201=10 kΩ e ingresso LM386 **Rin tipica 50kΩ modellata come pura resistenza**. La sorgente ideale e il riferimento equipotenziale 0 sono **ipotesi di laboratorio**, non connessioni approvate del master.

Sono eseguiti nove esperimenti indipendenti (**ampiezza picco sorgente 0,5/1/2 V × posizione wiper 10/50/90%**), 455 kHz AM al 50% e 1 kHz audio, transienti `.tran 0.2u 12m 0 0.2u`, estrazione pp nell'intervallo stabile 8–11 ms. A ogni test vengono confrontati AFpp su terminazione standalone a 100kΩ, AFpp sul ramo caricato e ampiezza pp al pin 3 di U1201 idealizzato. Gate su misure finite positive, attenuazione passiva, andamento in ingresso e monotonia di volume *nel solo modello*, senza soglie di sensibilità artificiose. Il test invoca le esportazioni KiCad9 native per validare il mapping J1502→RV1301→J1202→U1201, impedendo deriva silenziosa fra esperimento e circuito.

## Limiti e criteri di accettazione

Questa prova **non** dimostra alcun miglioramento o accettabilità di ricezione AM. D1501 è 1N4148 candidato nella BOM ma il deck utilizza esclusivamente `DGENERIC(Is=2.5n N=1.9 Rs=0.6 Cjo=4p Vj=0.75 Tt=4n)`, che **non è un macromodello 1N4148 OEM**. Ampiezza/sorgente 50Ω e Rcoil sono fittizie, in assenza di RF/mixer/IF/AGC reali. Mancano distorsione d'inviluppo, modello attivo LM386, speaker, THD, noise/SINAD, PVT, cavo, ritorni/chassis, ESD/EMI, FM/SSB. La posizione RV1301 è trattata come frazione resistiva, non legge acustica finale. Un risultato FULL verde testimonia solo la riproducibilità numerica e la conformità al contratto schematico, mai qualifica di fabbricazione.

**Stato iniziale:** branch in CI da verificare sullo SHA finale, risultati non ancora attribuiti. Master MAIN KiCad9 166 componenti **immutato**, nessuna PCB radio e nessun DRC di prodotto. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
