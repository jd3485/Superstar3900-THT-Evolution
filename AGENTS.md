# AGENTS.md — protocollo permanente ChatGPT Work, Superstar 3900 THT Evolution

> **LEGGERE ALL'INIZIO DI OGNI CHAT, PRIMA DI MODIFICARE FILE.** Questa procedura risiede su GitHub: non presuppone memoria di conversazioni precedenti.
>
> **Repository unico THT:** https://github.com/jd3485/Superstar3900-THT-Evolution · ramo canonico: **main**.
>
> **Checkpoint operativo sempre aggiornato:** [00_Gestione_Progetto/WORK_STATO_CORRENTE.md](00_Gestione_Progetto/WORK_STATO_CORRENTE.md). Non dedurre la revisione corrente dal numero o dalla data di questo AGENTS.

## Mandato permanente, ambito e autonomia

Obiettivo: completare **una PCB unica Superstar 3900 THT Evolution**, con schemi KiCad reali, componenti e impronte esclusivamente **through-hole (THT)**, pin↔pad↔net verificati, layout RF/IF/alimentazioni correttamente ingegnerizzato, nessun errore elettrico, ERC o DRC **noto**. Nessun processo software può garantire zero difetti hardware; prove fisiche e review indipendenti rimangono obbligatorie.

L'utente delega priorità, MPN/valori ordinari giustificati, alternative tecniche, divisione in revisioni, branch/PR e integrazione delle modifiche ordinarie **quando i gate richiesti sono superati e i permessi lo consentono**. Non interrompere una sessione dopo ogni revisione e non chiedere «continua». Passare autonomamente a più revisioni consecutive reali, finché la sessione e gli strumenti lo consentono.

**Limite fondamentale:** questa è un'istruzione per le sessioni avviate dall'utente, **non** un'autorizzazione a lavorare in background né una promessa di proseguire dopo che Work termina. Le nuove chat devono essere avviate dall'utente.

**Separazione assoluta:** NON modificare e NON fondere con jd3485/Superstar3900-SMD-Evolution. Non trasportare vincoli specifici SMD (codec, SAI, EP33, SG48, etc.) nel progetto THT: ricavare i requisiti THT dalle sue fonti e dal suo repository.

## Bootstrap obbligatorio a ogni nuova sessione

1. Consultare live GitHub per ottenere l'ultimo **HEAD SHA di main**. **Leggere da main AGENTS.md e 00_Gestione_Progetto/WORK_STATO_CORRENTE.md**. Poi leggere il rapporto tecnico pertinente, il master KiCad attuale, 00_Gestione_Progetto/STATO_PROGETTO.md, RIPRENDI_IN_UNA_NUOVA_CHAT.md, PR/issue aperte e le GitHub Actions pertinenti.
2. Trattare il checkpoint come un **indice**: verificarne date, commit, PR merged, stato PR, workflow e artefatti. La fonte decisiva è il **merge realmente avvenuto su main**. Non scambiare una PR open/draft o un branch per una revisione integrata.
3. Ricercare prima i lavori già avviati: recuperare la PR valida esistente, controllare se il suo base è ancora HEAD o è diventato obsoleto dopo merge concorrenti. **Non creare una PR duplicata** né sovrascrivere altri avanzamenti; se il master cambia, riconciliare il branch con main conservando tutte le partizioni elettriche.
4. Pianificare il lavoro ingegneristico **su più revisioni sostanziali**, ordinando i blocchi per rischio tecnico e dipendenze. Ogni revisione deve produrre una modifica vera quando serve: file KiCad nativi, librerie, test, MPN qualificati e rapporto; non soltanto nuove etichette di versione o documenti.
5. Consultare datasheet originali dei produttori, oltre alle fonti di supporto; distinguere componenti candidati da qualificati. Controllare pinout reale, footprint, package, tensioni assolute, corrente/energia, derating termico, tolleranze PVT, test EMI/RF, startup/brownout, percorso di massa, rumore e condizioni di guasto.
6. Verificare il CAD con **KiCad 9 nativo**: ERC di tutta la gerarchia, esportazione netlist reale, verifica di tutte le partizioni pin↔net e di ogni modifica intenzionale. DRC e netlist↔PCB **solo quando esiste una vera PCB**; non affermare DRC=0 sulla base di un ERC=0 o di una PCB fittizia. Preferire verifiche indipendenti e simulazioni vendor, distinguendole da modelli comportamentali e prove di banco.
7. Per ogni cambiamento tecnico ordinario: **branch dedicato → modifiche versionate → verifica → PR → CI su HEAD finale → merge su main soltanto se tutti i gate richiesti sono verdi e le autorizzazioni consentono il merge**. Nessun waiver ERC/DRC fittizio, test nascosto, CI fallita classificata come successo, né integrità elettrica presunta.
8. Se CI non parte (p.es. runner non assegnato), test fallisce, GitHub non è accessibile, il componente non è reperibile o una qualifica manca, **non dichiarare completato il gate e non forzare il merge tecnico**. Lasciare PR draft/bloccata, un issue con evidenze e il prossimo passo eseguibile. Distinguere nettamente errore CAD, difetto di test e problema infrastrutturale.
9. **Dopo ogni merge** e **prima di chiudere la sessione**, aggiornare 00_Gestione_Progetto/WORK_STATO_CORRENTE.md con ultima revisione integrata, HEAD SHA vero, PR, run IDs, ERC/DRC, differenze nei file reali, rischi e prossimo blocker. Aggiornare anche l'handoff storico quando utile. Se il checkpoint non può essere unito a main per CI/permessi, pubblicarne la bozza sul branch e l'esatto stato nella PR/issue, dichiarando esplicitamente che main non è ancora aggiornato.
10. Dopo un merge valido, se restano capacità e strumenti, **procedere con il successivo problema concreto senza aspettare una nuova richiesta**. In una nuova chat ripartire dal checkpoint, non dalla memoria o dall'ultima frase dell'assistente.

**Anti-loop:** non creare microrevisioni di soli report per simulare progresso; non attribuire percentuali PCB a test di script o footprint; niente false simulazioni vendor e niente layout dimostrativo presentato come radio completa.

## Vincoli non negoziabili

- **NO FAB / NO GERBER DI PRODUZIONE / NO ORDINI PCB / NO TX** fino a distinta autorizzazione esplicita dell'utente. Non collegare a veicolo, batteria o antenna per test di trasmissione senza autorizzazioni e qualifica di sicurezza. Non attivare o collegare una catena TX per soddisfare ERC/DRC.
- **THT al 100%**, compresi componenti reali, simbologia e impronte; evitare SMD salvo nuova autorizzazione esplicita dell'utente.
- Preservare la baseline V0.9 e tutte le revisioni storiche. Ogni nuovo master deve dimostrare che le connessioni legacy restano intatte, a eccezione delle modifiche intenzionali documentate e controllate.
- Non introdurre PWR_FLAG arbitrari per occultare errori, non scavalcare la protezione fusibile/TVS/diodi, non cortocircuitare rail o masse non qualificate.
- **I limiti di alimentazione restano aperti:** LM393 su rail a monte con massimo 36 V, reverse fault, energia F701/D702, soglie OVP, rumore/termica 5 V e 20 V. ERC0 non significa protezione o regolazione qualificate.
- Il VCO RX e il boost non sono ancora qualificati dal punto di vista RF/hardware; il completamento di RF/IF/demodulazione/audio/controlli e di una vera PCB è ancora lontano.
- La fabbricazione richiede schemi completi e riesaminati, BOM/MPN/impronte qualificate, DRC0 su PCB realmente sbrogliata, ritorni di corrente RF/IF, revisione indipendente, prototipo e prove di laboratorio. L'autorizzazione NO FAB / NO TX non è delegata.

## Punto di partenza storico alla creazione del protocollo (11 novembre 2026)

**Non trattare questo paragrafo come checkpoint aggiornato.** Quando è stato scritto, main aveva **V2.0 a sette fogli**, [PR #17 integrata](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/17), commit di merge **284bd3641d7a0f905d14dc4c9f36ee9da84bbc93**. Il master era 04_KiCad/V2.0/PLL_RX_HIERARCHICAL_MASTER_V2.0.kicad_sch; 72 reti KiCad native, ERC0 nell'ultima CI nota, 7 fogli e VTUNE20 MC34063/LM317 collegato al PLL. **Nessuna PCB completa** e nessuna DRC scheda.

La [PR #20, V2.1](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/20) era **draft e non integrata**: assegnazione preliminare delle impronte THT F701/D702 senza modifiche alle 72 connessioni, proveniente dal V2.0 a sette fogli. Tutti i 19 workflow su quell'HEAD fallivano **prima** di avviare un job (nessun runner, 0 step): non sono prove di regressione elettrica, ma **non costituiscono CI verde**. [Issue #22](https://github.com/jd3485/Superstar3900-THT-Evolution/issues/22). Altri blocchi reali: [L501 VCO, issue #19](https://github.com/jd3485/Superstar3900-THT-Evolution/issues/19) e [L920 boost, issue #21](https://github.com/jd3485/Superstar3900-THT-Evolution/issues/21). **Rileggere main e il checkpoint prima di riprendere!**

## Ripresa dopo il limite della chat

Dentro un Progetto ChatGPT con le istruzioni condivise predisposte, è sufficiente scrivere **«Riprendi.»** nella nuova chat Work. La sessione deve leggere questi due documenti da GitHub, verificare PR/CI e procedere. Se il Progetto non ha le istruzioni, utilizzare la frase autosufficiente:

> Riprendi il progetto THT jd3485/Superstar3900-THT-Evolution. Leggi AGENTS.md e 00_Gestione_Progetto/WORK_STATO_CORRENTE.md dal ramo main; verifica PR e CI aggiornate. Procedi in autonomia con più revisioni vere KiCad, verifiche e PR, merge soltanto dopo gate verdi, e aggiorna l'handoff. NO FAB / NO TX.

Non inventare di aver letto GitHub se non è disponibile.

## Politica permanente per ottimizzazione GitHub Actions (11 novembre 2026)

**ChatGPT diagnostica, progetta e corregge; GitHub conserva; Actions verifica.**
Eseguire prima verifiche locali quando gli strumenti sono realmente disponibili,
senza dichiarare un test non eseguito. **Non usare Actions per ripetere la
stessa installazione nativa in decine di job paralleli**.

La CI ufficiale è `.github/workflows/ci_optimized.yml`: dieci suite
unitarie storiche Python veloci su ogni PR, comprese le modifiche ai documenti;
per ogni modifica elettrica, KiCad, BOM, test, workflow, o file non riconosciuto,
un'unica esecuzione FULL nel container KiCad9 ufficiale immobilizzato a digest
deve eseguire tutti i 21 workflow storici originali (step di test reali).
I 22 workflow legacy (21 nativi/SPICE + 1 Python) rimangono disponibili con `workflow_dispatch` per
diagnosi indipendente, ma non partono più automaticamente per PR/push.
La CI FULL salta **solo** installazioni duplicate e upload/checkout già
centralizzati: non ERC, pin-net, footprint, ngspice, script né regressioni.
Ogni merge tecnico richiede gate `Required CI gate` verde sullo SHA finale
e audit di log/evidenze; `skipped` è valido per FULL **solo** su diff
esclusivamente documentale rilevato dal controllo scope.
Nuovi workflow non inventariati bloccano la FULL. La suite manuale V2.5 e ora inclusa nel manifest; conta i workflow nel file ci/full_regressions.py, non usare numeri storici come baseline elettrica.

Documentazione operativa: [ci/CI_COST_OPTIMIZATION.md](ci/CI_COST_OPTIMIZATION.md).
Nessun accesso al budget, fatturazione o regole di branch-protection viene
modificato senza consenso esplicito; in caso di status required legacy
irraggiungibile, non forzare merge. Nessun downgrade KiCad9 e nessun ERC waiver.
Il contenuto di questa sezione non costituisce una prova di release hardware.
**NO FAB / NO TX / no batteria/veicolo**.
