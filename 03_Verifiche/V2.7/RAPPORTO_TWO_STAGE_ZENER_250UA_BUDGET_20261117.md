# V2.7 — budget corrente Zener per due stadi PMOS THT (NON qualificante)

17 novembre 2026. Banco KiCad9 isolato: due stadi anti-serie, 24 componenti/54 pin/14 net. Nuovo controllo aggiunto al verificatore nativo FULL `verify_two_stage_twin_zener_single_open_native.py` già esistente: stessa topologia fisica, quattro diodi 1N4106-1 candidati, Rgs 47k e sink serie 10k per ogni stadio. Verifica regressiva dei valori e delle connessioni già presente; nuova analisi **solo matematica**.

Supponendo **arbitrariamente** 11/12/13V al nodo gate e fonte 0/13,8/20/24/36/48V, resistori ±5% a tre punti, il budget massimo teorico disponibile allo Zener è `max(0, (Vs-Vz)/Rg - Vz/Rgs)`. Per una sola giunzione attiva, 54 su 162 combinazioni non raggiungono 250µA; dividendo **idealmente** e simmetricamente fra due giunzioni, 64 su 162 non raggiungono 250µA *per ramo*. Ogni stadio replica gli stessi 162 casi per ciascuna configurazione. La ripartizione 50/50 è ipotetica; il componente con corrente minore può essere ulteriormente penalizzato.

A Vz assunto 12V e Rgs/Rg nominali 47k/10k, tensione sorgente minima teorica per erogare 250µA ad **un** Zener: **17,053191V**; per **due** Zener a 250µA ciascuno: **19,553191V**. A Vs=13,8V la soluzione ohmica senza conduzione Zener è **11,378947V**: il semplice bilancio nominale non dimostra alcuna disponibilità di corrente di test. Non estendere questi numeri al reale Vz o alle tensioni di gate del MOSFET.

I 250µA sono un punto di prova citato nella precedente verifica per il candidato; **non** sono automaticamente corrente minima di regolazione né indicano da soli la curva completa. Senza I–V OEM garantita su PVT/temperature, stadio driver, impulsi, tempi e derating, né i precedenti 3.888 scenari sintetici né questi 324 corner di budget per stadio autorizzano la conclusione `|Vgs|<20V` in hardware. Mancano alimentazioni e supervisori realmente indipendenti, SOA, carico, PCB, fail-off da cause comuni. Issue #27 aperta.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
