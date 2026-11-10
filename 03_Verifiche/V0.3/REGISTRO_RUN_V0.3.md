# Registro di esecuzione V0.3

Questa revisione crea le suite di test Python e il nuovo step del workflow `.github/workflows/verifica_v02.yml`, per un totale previsto di **12 + 24 + 32 = 68 controlli statici/aritmetici**.

I controlli sono predisposti ma la **run CI GitHub deve essere verificata dopo il commit**. Il rapporto tecnico sarà aggiornato con numero run, commit e PASS/FAIL effettivi dopo l'esecuzione.

`python3 -B -m unittest discover -s 03_Verifiche/V0.1 -p 'test_*.py' -v`
`python3 -B -m unittest discover -s 03_Verifiche/V0.2 -p 'test_*.py' -v`
`python3 -B -m unittest discover -s 03_Verifiche/V0.3 -p 'test_*.py' -v`

**Attenzione:** V0.2 ora legge la baseline `01_Specifiche/CONFIGURAZIONE_V0.2.json` anziché la configurazione corrente V0.3. Le altre evidenze V0.2 restano immutate.

**NON ESEGUITI:** KiCad ERC/DRC, netlist verificata, SPICE, EM, taratura e collaudi reali, PCBWay DFM, prove TX. **NO FAB / NO TX**.
