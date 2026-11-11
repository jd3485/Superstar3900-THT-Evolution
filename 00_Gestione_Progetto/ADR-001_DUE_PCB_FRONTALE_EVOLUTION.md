# ADR-001 — Due PCB e frontalino Superstar 3900 Evolution

**Data decisione:** 11 novembre 2026 · **Stato:** approvata dall'utente come obiettivo architetturale e di stile, NON come progetto meccanico/elettrico validato.

## Decisione

Il prodotto finale sarà costruito con **due PCB funzionali distinte**, interconnesse con cavi e connettori qualificati, mantenendo al 100% il vincolo **THT** su entrambe (salvo nuova autorizzazione esplicita).

1. **PCB-MAIN / RADIO:** alimentazione e protezioni; sintetizzatore PLL/VCO; RF, mixer/IF e demodulazione; audio e logica centrale; servizi di alimentazione/filtraggio; circuiti eventuali TX solo quando autorizzati progettualmente, mai test di trasmissione impliciti. Privilegiare isolamento RF, ritorni di massa controllati, schermature, accesso manutenzione e dissipazione termica.
2. **PCB-FRONT / CONTROL PANEL:** potenziometri, selettori rotativi, encoder, pulsanti e LED; interfacce display con montaggio THT/through-hole o moduli a piedini passanti verificati; driver e interfaccia **S-meter analogico a lancetta**, retroilluminazione. Manopole e indicatore devono essere meccanicamente allineati al pannello.

**Estetica approvata:** Superstar 3900 immediatamente riconoscibile, ma **Evolution**: frontale classico, comandi fisici tradizionali, non touchscreen, display moderno discreto, S-meter analogico retroilluminato in stile 3900, manopole importanti e proporzioni coerenti con l'originale. Non riprodurre design proprietari o marchi non autorizzati nel materiale destinato alla produzione.

## Requisiti preliminari interfaccia tra le due PCB (non è ancora una pinout)

- Separare segnali analogici sensibili (S-meter, controllo volume e letture potenziometri) dalle linee digitali/commutate dei display e LED. Definire filtraggio, riferimento di massa, ritorni di corrente, protezione ESD e possibili interferenze RF nel cavo.
- Alimentazioni e ritorni connettore dimensionati per correnti massime, disturbi, hot-plug e guasti; nessun trasferimento di rail non qualificati al frontalino. Le tensioni ammesse devono essere validate nella progettazione specifica.
- Preferire controllo display e logica locale sul PCB-FRONT solo se la disponibilità THT e i limiti EMI lo consentono; non scegliere oggi un controller, un protocollo o un modulo non verificato.
- S-meter a lancetta: candidato movimento analogico con driver calibrabile, limitazione corrente e protezione strumento. **Nessuna specifica di fondo scala, precisione, bobina o MPN ancora approvata.** RX S-meter prioritario; ulteriori funzioni di lettura potenza/modulazione sono opzionali e dipendono dalla futura catena autorizzata.
- Connettori polarizzati, accessibili, preferibilmente robusti a vibrazioni; definire numerazione pin, massa/chassis, schermatura e cablaggi in un **documento interfaccia** e nei veri schemi KiCad prima del PCB layout.
- Evitare che guasti della scheda frontale attivino involontariamente funzioni radio critiche; mute e protezioni devono restare indipendenti.

## Decisioni che restano aperte

Dimensioni effettive chassis/frontalino, allineamento ai fori e quote CAD; marca/modello S-meter THT; risoluzione, tecnologia e disponibilità display; disposizione finale di tutti i comandi; eventuale spazio per microfono e connettori; alimentazioni e bus; dimensione e fissaggi delle PCB, connettori, BOM/MPN e assemblabilità 100% THT.

## Impatto sul progetto esistente

- Gli **attuali sette fogli KiCad V2.6** continuano a rappresentare soltanto la baseline **PCB-MAIN RX parziale**, senza aggiunte o migrazioni artificiali di reti in questa decisione.
- La scelta sostituisce l'obiettivo storico scritto come 'PCB unica'. **Non cambia** la proibizione di fabbricare, realizzare Gerber di produzione, ordinare PCB o trasmettere. I due PCB richiedono DRC e review indipendenti **su entrambe** e una verifica d'integrazione dei cablaggi.
- Separare schemi/moduli e BOM per MAIN e FRONT preservando tutte le revisioni storiche. Prima di routing: interfaccia formalizzata, ERC/netlist/pin↔pad, qualifica RF, alimentazioni, ESD, termica e geometria frontale.

**NO FAB / NO TX / NO BATTERIA / VEICOLO**. Decisione architetturale e di stile, non completamento elettrico o qualifica hardware.
