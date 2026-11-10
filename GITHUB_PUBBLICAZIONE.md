# Gestione cumulativa V0.5

V0.5 modifica soltanto file nuovi e registri correnti, più la regressione V0.4 ora riferita a una fotografia `CONFIGURAZIONE_V0.4.json` immutabile. Conservare storici, CI e handoff GitHub; **mai rigenerare ZIP completi a ogni revisione**. I test Python NON sono SPICE/ KiCad ERC né prove hardware, e nessun risultato automatico autorizza TX o produzione.

---

# Nota GitHub V0.4

La fonte è `main` cumulativo; si aggiungono i nuovi file V0.4 e si aggiornano solo i registri attivi, la configurazione corrente, la suite regressiva V0.3 (per leggere lo snapshot) e il workflow. Le configurazioni storiche V0.1, V0.2 e V0.3 rimangono immutabili. Nessun ZIP per ogni revisione. Per scaricare l'intero progetto alla V0.4 usare l'archivio del commit `main` verificato; eventuali tag v0.4 devono essere **verificati creati** prima di dichiararli disponibili. Nessun ordine PCB o TX.

---

# Nota cumulativa V0.3

**main è cumulativo**: V0.3 aggiunge i nuovi documenti e modifica solo stato, test/regressioni e handoff; i file V0.1/V0.2 rimangono recuperabili nello storico. Introdotta la baseline `CONFIGURAZIONE_V0.2.json` perché test storici V0.2 continuino a controllare quella revisione anche se `CONFIGURAZIONE_CORRENTE.json` avanza. Non richiedere ZIP ogni volta. I manifest SHA di V0.1 si riferiscono SOLO a V0.1. Nessun tag dichiarato senza verifica. **NO FAB / NO TX.**

---

# Nota cumulativa V0.2

La V0.2 **non rigenera ZIP** né sostituisce la V0.1: il commit su `main` conserva il progetto completo e i file invariati. Per ricostruire la V0.2 usare lo SHA del commit; `MANIFEST_SHA256_V0.1.csv` riguarda esclusivamente la V0.1 e non va applicato al `main` aggiornato. Un tag v0.2 non è dichiarato finché non creato e verificato. A ogni futura revisione aggiungere/modificare soltanto i percorsi necessari.

---

# GitHub — pubblicazione e gestione cumulativa V0.1

**Repository privata:** `jd3485/Superstar3900-THT-Evolution`  
**URL:** https://github.com/jd3485/Superstar3900-THT-Evolution  
**Branch di riferimento:** `main`.

## Regola permanente
GitHub conserva l'intero albero cumulativo a ogni commit. **Non rigenerare e non caricare ZIP completi per ogni revisione.** Aggiungere soltanto file nuovi o modificati; gli altri restano invariati. I commit storici e gli eventuali tag permettono di recuperare le baseline precedenti. Uno ZIP di una revisione, se necessario, si scarica dal suo commit/tag.

## Per ogni revisione «Continua»
1. Controllare HEAD `main`, tag, PR, CI e leggere i file di continuità.
2. Studiare il modulo successivo e produrre documenti, BOM, schemi, calcoli e test pertinenti.
3. Eseguire verifiche reali e registrare PASS/FAIL/SKIP/NON ESEGUITO senza promuovere simulazioni a misure hardware.
4. Aggiornare solo i percorsi nuovi o modificati, incluso rapporto di revisione, README/stato, registro decisioni e `RIPRENDI_IN_UNA_NUOVA_CHAT.md`.
5. Integrare la revisione coerente in `main`; non forzare risultati bloccanti.
6. Non sovrascrivere né spostare tag preesistenti; i manifest SHA-256 delle vecchie baseline valgono solo per la versione a cui si riferiscono.

## Stato V0.1
Baseline documentale, 12/12 test statici; nessuna simulazione circuitale, nessun ERC/DRC o prototipo. NO FAB / NO TX.

## Stato del tag
La presenza di `main` e dei file va verificata su GitHub. Un tag `v0.1` è utile ma non deve essere dichiarato esistente prima della sua effettiva creazione.
