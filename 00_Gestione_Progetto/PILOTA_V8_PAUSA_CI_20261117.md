# Pilota THT V8 — pausa CI temporizzata

**17 novembre 2026.** Migrazione del userscript Tampermonkey V7 fornito dall'utente al V8. La versione consegnata alla chat è un file `.user.js` da installare localmente, non uno script eseguito da GitHub Actions.

## Protocollo canonico

I segnali **terminali** restano quattro: `CONTINUA`, `ATTESA`, `ERRORE`, `FINE`. Durante una run FAST/FULL/Required GitHub **effettivamente pending** e senza altro lavoro autonomo eseguibile, la risposta termina così:

```text
Attività: monitoraggio CI PR #..., commit ..., run ....
Esito: FAST verde; FULL in_progress, Required pending.

PAUSA_CI
ATTESA
```

La parola `PAUSA_CI` compare su **una riga autonoma nel corpo** e `ATTESA` resta l'ultima riga. V8 riconosce tale coppia, avvia una pausa locale di 240 secondi, quindi invia `procedi` una sola volta; la nuova risposta può generare un'altra pausa solo se l'ultimo controllo live GitHub conferma ancora CI pending. V8 supporta anche `PAUSA_CI` come segnale terminale di compatibilità, ma non è il formato da usare nel protocollo THT corrente.

`ATTESA` senza marcatore = arresto con intervento umano. `ERRORE` e `FINE` arrestano. `CONTINUA` continua solo con lavoro successivo concreto identificato; no polling rapido o finti avanzamenti.

## Installazione e limiti

1. Disabilitare **Superstar THT — Pilota V7** in Tampermonkey; installare e abilitare il file userscript V8 consegnato in chat.
2. Ricaricare la pagina progetto THT, verificare il pannello `SUPERSTAR THT AUTO V8`, premere **AVVIA** a editor vuoto.
3. In `PAUSA CI` il pannello indica la ripresa; **FERMA** interrompe anche il timer. V8 non aggiorna il browser, non apre PR, non esegue merge e non opera fuori dalla pagina aperta.
4. Se il browser congela/sospende completamente la scheda, se la pagina viene chiusa o ricaricata, il pilota non garantisce ripresa. Se conversazione/risposta/editor cambiano durante la pausa, il pilota interrompe la ripresa per evitare invii nel contesto errato.
5. Il selettore DOM di ChatGPT può cambiare: l'invio richiede editor ProseMirror e bottone `Invia` come nel V7; in caso di cambiamento lo script si ferma, non presume un invio riuscito.

Il protocollo non modifica i gate FAST/FULL/Required, il vincolo di HEAD finale, il blocco #27 o **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**.
