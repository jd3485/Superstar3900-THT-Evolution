# Audit OEM THT — lotto 2, 12 novembre 2026

## Obiettivo e perimetro
Verifica **documentale** di tre candidati commercializzati da TI in montaggio THT e di una dichiarazione compliance Littelfuse. Repository THT, CAD MAIN V2.6 invariato. Il CSV contiene 138 posizioni fisiche: **6 ATTIVO_CONFERMATO, 132 DA_VERIFICARE** anche dopo questo audit. Non attribuire stato ACTIVE a un componente CAD solo perché esiste un equivalente con un altro suffisso o fabbricante.

## Evidenza sul codice commerciale esatto

| Ref | Identificazione attuale nel CAD | MPN candidato / documento | Evidenza ufficiale | Decisione |
|---|---|---|---|---|
| U801 | LM393N_DIP8_DUAL | Texas Instruments **LM393N/NOPB** PDIP8 | OEM: **ACTIVE** nella pagina part-details; datasheet TI LM393-N package option addendum 13-gen-2026: **Active / Production / PDIP P 8**. https://www.ti.com/product/LM393-N/part-details/LM393N/NOPB ; https://www.ti.com/lit/ds/symlink/lm393-n.pdf | Candidato, NON MPN CAD confermato. Da valutare rail 36V massimo, temperature 0..70°C, common mode, fault e pin-net |
| U803 | LM358N | Texas Instruments **LM358N/NOPB** PDIP8 | OEM: **ACTIVE** part-details; datasheet package addendum 16-mag-2026: **Active / Production / PDIP P 8**. https://www.ti.com/product/LM358-N/part-details/LM358N/NOPB ; https://www.ti.com/lit/ds/symlink/lm358-n.pdf | Candidato, NON MPN CAD confermato. Da verificare op-amp/rumore/offset/slew-rate filtro PD, 0..70°C, alimentazione e pin-net |
| U912 | onsemi LM317T | Texas Instruments **LM317T/NOPB** TO-220 | OEM: **ACTIVE** part-details; datasheet TI LM317-N package addendum 05-mar-2026. https://www.ti.com/product/LM317-N/part-details/LM317T/NOPB ; https://www.ti.com/lit/ds/symlink/lm317-n.pdf | **Sostituzione di fabbricante**, non approvata dal solo stato produttivo; verifica pinnatura/tab VOUT, dropout, max delta VIN–VOUT, correnti, ripple, stabilità, compensazione e calcolo SOA/termica |
| F701 | Littelfuse 0251.500MXL | Certificato OEM di conformità su codice esatto | Certificato RoHS **06-feb-2026**, esenzione **7a**: https://www.littelfuse.com/assetdocs/coc-rohs9-0251?assetguid=3f7988e8-898b-4c10-8fc8-25b3c95bdae5 | Evidenza compliance soltanto; **nessuna prova di lifecycle ACTIVE**. Non approvato |

## Verifica minima prima di convertire le candidature in MPN CAD
1. Confrontare scheda tecnica OEM e simbolo KiCad **pin ↔ pad ↔ net** senza alterare reti legacy. Per U912 confermare la linguetta di TO-220 collegata a VOUT. Salvare tabella e rapporto.
2. Verificare assoluti massimi, condizione normale e guasto singolo, tolleranze e temperatura per U801/U803/U912. **U801** resta vulnerabile a potenziali sovratensioni del rail a monte; lifecycle ACTIVE non sana Issue #27.
3. Allineare deliberatamente il **Value/MPN esatto** nel CAD soltanto dopo review e verifica elettrica e termica; fare branch CAD distinto, KiCad 9 ERC/netlist nativa, gate CI sullo SHA finale. Solo a quel punto valutare l'aggiornamento dello stato della relativa posizione di inventario.
4. Per F701 richiedere evidenza di produzione corrente sul codice esatto e qualificare energia fusibile/TVS; RoHS con esenzione richiede revisione di conformità a destinazione d'uso.

## Componenti critici già scrutinati ma senza prova definitiva di produzione
U401 ML145151YP Lansdale; L501 Coilcraft 150-05J08L; L920 Bourns RLB0914-681KL: la documentazione OEM pubblica non basta per dichiarare corrente la fabbricazione di ciascun MPN. Richiedere conferma scritta del produttore, senza sostituire per supposizione. Vedere issue #42.

## Stato di rilascio
**BOM release BLOCKED: 6/138 certificati, 132/138 non verificati; CAD MAIN V2.6 invariato, PCB FRONT non esistente.** Nessuna nuova prova KiCad, SPICE o CI dichiarata in questo audit documentale. Proibiti PCB/Gerber/fabbricazione, TX e alimentazione da batteria/veicolo. Il branch di audit è documentale; il gate FULL potrà essere saltato *solo* dopo corretta classificazione del diff dalla CI ufficiale. Nessun merge senza gate finale verde.
