# Prima ingegnerizzazione pin-to-net PLL — V0.3

**Questi file sono un PRECURSORE di schema KiCad, non uno schematico .kicad_sch né una PCB certificata.** Non sono Gerber né un file pronto da produrre. Si stanno già definendo pin fisici e reti vere: U401 28/28 pin, U402 14/14 pin, quarzo e primi componenti THT.

- `PLL_U401_U402_PINNET_V0.3.csv`: mapping pin-number certificato da screenshot dei datasheet Lansdale e Toshiba, e proposta di funzione/rete. Reti in stato CANDIDATO non diventano collegamenti approvati automaticamente.
- `PLL_PASSIVI_NETS_DA_CHIUDERE_V0.3.csv`: primi passivi, interfacce da chiudere e rischi elettrici. Contiene esplicitamente connessioni ancora da integrare, non va interpretato come netlist finale.
- `01_Specifiche/V0.3/PLL_CORE_CIRCUITO_V0.3.md`: topologia, valori candidati, sequenza di completamento.
- In **V0.4** costruire uno schematico KiCad nativo con simboli MPN/footprint, unione reti completa e validazione ERC, qualora le scelte di componenti e pin siano approvate.

**Non affermare ERC/DRC PASS**. Riferimenti a `N_CODE` sono solo RX; non esiste una porta di TX o percorso autorizzato. Il reset RC non sostituisce interblocchi hardware o supervisori di alimentazione.

Il file `PLL_PASSIVI_NETS_DA_CHIUDERE` è deliberatamente incompleto: alcune reti hanno sigle intermedie distinte e devono essere collegate correttamente in KiCad, senza presumerne la continuità. Conservare questo limite nel rapporto.
