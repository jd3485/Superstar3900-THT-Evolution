"""V0.3: regressioni aritmetiche e pinout; NESSUN test elettrico/KiCad."""
import csv,json,sys,unittest,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'02_Piano_Frequenze/V0.3'))
from pll_core_model_v03 import (channel_state,crystal_load_pf,tank_ceff_pf,error_hz,gate_model,
 FREF,R,FPFD,PRESCALER,LO_MIN,LO_MAX,N_TO_PIN,FF_CLK_MIN_GUARANTEED_5V,PLL_FIN_DATASHEET_LIMIT_5V_85C_SQUARE)
sys.path.insert(0,str(ROOT/'02_Piano_Frequenze/V0.2'))
from frequency_plan_v02 import all_rows,rx_plan
PINS=ROOT/'04_KiCad/V0.3/PLL_U401_U402_PINNET_V0.3.csv'
BOM=ROOT/'07_Componenti/BOM_PLL_CORE_V0.3.csv'
CURRENT=ROOT/'01_Specifiche/CONFIGURAZIONE_V0.3.json'
class PLLV03(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
    with PINS.open(newline='',encoding='utf-8') as f: cls.pins=list(csv.DictReader(f))
    cls.map={(p['reference'],int(p['pin'])):p for p in cls.pins}
    with BOM.open(newline='',encoding='utf-8') as f: cls.bom=list(csv.DictReader(f))
    cls.cfg=json.loads(CURRENT.read_text(encoding='utf-8'))
 def test_01_u401_28pins(self):self.assertEqual({int(p['pin']) for p in self.pins if p['reference']=='U401'},set(range(1,29)))
 def test_02_u402_14pins(self):self.assertEqual({int(p['pin']) for p in self.pins if p['reference']=='U402'},set(range(1,15)))
 def test_03_no_duplicate_pins(self):self.assertEqual(len(self.pins),len(self.map))
 def test_04_mpns_on_pinmap(self):
    self.assertEqual({p['mpn'] for p in self.pins},{'ML145151YP','TC74AC74P'})
 def test_05_power_u401(self):
    self.assertEqual(self.map['U401',3]['net'],'+5V_PLL')
    self.assertEqual(self.map['U401',2]['net'],'GND')
 def test_06_power_u402(self):
    self.assertEqual(self.map['U402',14]['net'],'+5V_PLL')
    self.assertEqual(self.map['U402',7]['net'],'GND')
 def test_07_ref_2048_code(self):
    self.assertEqual((self.map['U401',7]['net'],self.map['U401',6]['net'],self.map['U401',5]['net']),('+5V_PLL','GND','+5V_PLL'))
    self.assertEqual(channel_state('D',9)['ra2_ra1_ra0'],(1,0,1))
 def test_08_tr_rx_no_offset(self):self.assertEqual(self.map['U401',21]['net'],'TR_RX_BIAS')
 def test_09_n12_n13_hard_low(self):
    self.assertEqual(self.map['U401',22]['net'],'GND')
    self.assertEqual(self.map['U401',23]['net'],'GND')
 def test_10_nbit_mapping(self):
    for b,p in N_TO_PIN.items():
        exp='N_CODE_'+str(b) if b<12 else 'GND'
        self.assertEqual(self.map['U401',p]['net'],exp)
    self.assertEqual(len(set(N_TO_PIN.values())),14)
 def test_11_prescaler_feedback(self):
    self.assertEqual(self.map['U402',2]['net'],self.map['U402',6]['net'])
    self.assertEqual(self.map['U401',1]['net'],self.map['U402',5]['net'])
 def test_12_unused_ff_inputs_defined(self):
    for pin in (10,11,12,13):
        self.assertNotEqual(self.map['U402',pin]['net'],'NC')
    self.assertEqual((self.map['U402',8]['net'],self.map['U402',9]['net']),('NC','NC'))
 def test_13_coded_ch9_n(self):
    ch=channel_state('D',9)
    self.assertEqual(ch['n'],3776)
    self.assertEqual({b for b,v in ch['n_bits'].items() if v},{6,7,9,10,11})
 def test_14_rx_all_270_word_12bits(self):
    rows=all_rows();self.assertEqual(len(rows),270)
    for row in rows:
        band=row['banda'];channel=int(row['canale'].removesuffix('A'));a=bool(row['alfa'])
        ch=channel_state(band,channel,a)
        self.assertTrue(0<=ch['n']<4096)
        self.assertEqual(ch['lo_hz'],row['lo_hz'])
        self.assertFalse(ch['tx_permitted'])
 def test_15_n_ref_all_channels(self):
    for r in all_rows():
        c=channel_state(r['banda'],int(r['canale'].removesuffix('A')),bool(r['alfa']))
        self.assertEqual(c['lo_hz'],c['n']*FPFD*PRESCALER)
 def test_16_math_ref(self):
    self.assertEqual((FREF,R,FPFD,PRESCALER),(10_240_000,2048,5000,2))
 def test_17_ch9_lo_feedback(self):
    c=channel_state('D',9)
    self.assertEqual((c['lo_hz'],c['fin_hz']),(37_760_000,18_880_000))
 def test_18_39mhz_below_ac74_min(self):
    self.assertLess(LO_MAX,FF_CLK_MIN_GUARANTEED_5V)
 def test_19_pll_fin_margin_5v_square(self):
    self.assertLess(LO_MAX//PRESCALER,PLL_FIN_DATASHEET_LIMIT_5V_85C_SQUARE)
 def test_20_crystal_load(self):
    self.assertAlmostEqual(crystal_load_pf(),17.727272727272727,places=5)
 def test_21_crystal_invalid(self):
    with self.assertRaises(ValueError):crystal_load_pf(c1=-1)
 def test_22_error_30ppm(self):
    self.assertEqual(error_hz(LO_MAX,30),1170.)
 def test_23_error_80ppm(self):
    self.assertEqual(error_hz(LO_MAX,80),3120.)
 def test_24_lc_model(self):
    self.assertAlmostEqual(tank_ceff_pf(LO_MIN),87.330326658,places=3)
    self.assertAlmostEqual(tank_ceff_pf(LO_MAX),75.698690785,places=3)
 def test_25_lc_ratio(self):
    self.assertAlmostEqual(tank_ceff_pf(LO_MIN)/tank_ceff_pf(LO_MAX),(LO_MAX/LO_MIN)**2,places=6)
 def test_26_gate_default_false(self):
    for k in ('pll_locked','clock_ok','code_valid','power_ok'):
        v=dict(pll_locked=True,clock_ok=True,code_valid=True,power_ok=True)
        v[k]=False
        self.assertFalse(gate_model(**v)['rx_audio_allowed'])
        self.assertFalse(gate_model(**v)['tx_permitted'])
 def test_27_full_lock_model_never_tx(self):
    a=gate_model(pll_locked=True,clock_ok=True,code_valid=True,power_ok=True)
    self.assertTrue(a['rx_audio_allowed']);self.assertFalse(a['tx_permitted']);self.assertFalse(a['fabrication_authorized'])
 def test_28_tht_selected_parts(self):
    self.assertEqual({r['mpn_o_valore'] for r in self.bom if r['ref'] in ('U401','U402')},{'ML145151YP','TC74AC74P(F)'})
    self.assertEqual({r['package'] for r in self.bom if r['ref'] in ('U401','U402')},{'DIP28','DIP14'})
 def test_29_bom_not_approved(self):
    self.assertEqual(len(self.bom),13)
    self.assertTrue(all('APPROVATO' not in r['stato'] for r in self.bom))
 def test_30_new_config_and_old_unchanged(self):
    self.assertEqual(self.cfg['revision'],'V0.3')
    self.assertEqual(json.loads((ROOT/'01_Specifiche/CONFIGURAZIONE_V0.2.json').read_text())['revision'],'V0.2')
    self.assertEqual(json.loads((ROOT/'01_Specifiche/CONFIGURAZIONE_V0.1.json').read_text())['revision'],'V0.1')
 def test_31_kicad_not_done(self):
    self.assertFalse(self.cfg['validation']['schematic_complete'])
    self.assertEqual(self.cfg['validation']['kicad_erc'],'NOT_RUN')
    self.assertFalse(list((ROOT/'04_KiCad').rglob('*.kicad_pcb')))
 def test_32_handoff_and_report(self):
    self.assertIn('V0.3',(ROOT/'RIPRENDI_IN_UNA_NUOVA_CHAT.md').read_text())
    self.assertTrue((ROOT/'03_Verifiche/V0.3/RAPPORTO_TECNICO_V0.3.md').exists())
if __name__=='__main__': unittest.main()
