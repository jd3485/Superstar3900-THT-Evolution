# V2.7 — misura reale IF455 a due porte: contratto Touchstone S2P (draft)

Data: 14 novembre 2026. Questo intervento **non inventa** una rete equivalente OEM. È il primo strumento che può importare un **file S2P misurato** in un banco con terminazioni esplicite, anziché stimare l'impedenza del filtro con la resistenza nominale del catalogo.

## Fonti OEM e limite di identificabilità

Catalogo NextGen FB series (specifiche 10/10/2024), https://www.nextgencomponent.com/uploads/soft/20241011/1-241011155152A8.pdf , pagina 4: schema di prova con **Rg+R1=R2=impedenza nominale ingresso/uscita**; pagina 5: FB455K0000L005 455±1kHz, 6dB bandwidth **±6kHz MIN**, selettività 50dB **±12,5kHz MAX**, ripple **2dB MAX**, insertion loss **5dB MAX**, impedenza terminale **2000Ω**. Le condizioni di carico non equivalgono a `Zin(f)=2000Ω` né forniscono fase/S11/S21/S12/S22 effettivi. Non convertire le specifiche di ampiezza in una funzione di trasferimento complessa unica, perché esistono infinite reti che rispettano gli stessi estremi.

Il precedente banco R||C PR166 è un *surrogato*, non la ceramica. Per avanzare occorre un campione THT con MPN/OEM verificato, fixture con connessioni top/bottom qualificate, VNA calibrato o misure a due porte equivalenti attorno a 455kHz, impedenza di riferimento, piano di calibrazione, temperatura, numero di serie/lotto, sweep e traccia di provenienza. L'integrazione con mixer SBL-1+ pilotato dal LO e KSP10 richiede misure proprie, non una presunzione di 50Ω o di 2kΩ complessi.

## Implementazione verificabile

`03_Verifiche/V2.7/verify_if455_touchstone_twoport_contract.py` importa Touchstone v1 `.s2p` RI/MA/DB con ordine standard S11,S21,S12,S22, frequenze ordinate e `R` di riferimento esplicito/default. Rifiuta formati sconosciuti o dataset troncati; calcola `Gamma_L=(ZL-Z0)/(ZL+Z0)`, `Gamma_in=S11+S12*S21*Gamma_L/(1-S22*Gamma_L)`, `Zin=Z0*(1+Gamma_in)/(1-Gamma_in)` e `Vload/Vsource=S21*(1+Gamma_L)/(2*(1-S22*Gamma_L))` per una **sorgente adattata a Z0** e carico complesso assegnato. La sorgente della radio NON è confermata adattata e questo calcolo non costituisce un model di mixer reale.

Senza `--measurement`, il test FULL controlla **27 casi sintetici** (3 formati × 3 frequenze × 3 carichi, incluso 2000−j350Ω) con un circuito *fittizio* consistente in sola resistenza serie di 100Ω fra porte Z0=2000Ω. Verifica S-parameter, impedanza ingresso `100Ω+Zload` e trasferimento `Zload/(Z0+100Ω+Zload)` mediante algebra di Kirchhoff indipendente. Questi 27 controlli **non** sono simulazioni ngspice, misure OEM né test di filtraggio: sono test di parser/matematica deterministici.

Esempio futuro: `python3 -B 03_Verifiche/V2.7/verify_if455_touchstone_twoport_contract.py --measurement misura_calibrata.s2p --load-real-ohm 2000 --load-imag-ohm 0`. L'output indica esplicitamente che la qualifica richiede ancora audit campione/calibrazione/OEM. Nessun file misurato reale è stato acquisito.

## Gate e decisioni

Registrato nella FULL CI esistente; qualsiasi PR tecnica richiede PASS FAST/FULL/required. Il master KiCad V2.6 non cambia, nessuna footprint THT candidata viene approvata, nessun filtro è elettricamente selezionato. Per issue #141 restano aperte le specifiche multi-mode AM/FM/USB/LSB/CW e i criteri RX; PR #123 e #143 restano draft. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**.

## Estensione V2.7 — impedenza sorgente complessa (PR successiva alla #168)

La sorgente adattata non rappresenta necessariamente il mixer LO-driven. Il verificatore ora espone `source_and_load_terminated_port`, che calcola `Vout/Vs` per impedenza Thevenin `Zs` e carico `ZL` **complessi e passivi** usando `Vout/Vs = [S21(1+Gamma_L)/(1-S22 Gamma_L)(1+Gamma_in)] [Zin/(Zs+Zin)]`. La formula per `Zs=Z0` deve restituire il trasferimento precedente; l'altra forma, `ZL/(Zs+Rserie+ZL)`, verifica indipendentemente il caso sintetico di resistenza serie. Questa implementazione contiene **81 crosscheck** (RI/MA/DB × 445/455/465 kHz × tre carichi × tre sorgenti, incluso `Zs=1000+j400 Ω`), non 81 AC ngspice né dati OEM. `--source-real-ohm` e `--source-imag-ohm` sono opzioni analitiche. Nessuna impedenza effettiva del mixer è nota: necessarie misure al drive LO e in varie condizioni PVT; per la banda RX non si dichiara alcuna qualifica.
