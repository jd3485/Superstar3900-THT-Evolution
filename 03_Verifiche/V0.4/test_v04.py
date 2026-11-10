"""V0.4: simulazione MATEMATICA di un tank e controlli statici KiCad. NON ERC, NON RF SPICE.
Esecuzione: python3 -B -m unittest discover -s 03_Verifiche/V0.4 -p 'test_*.py' -v
"""
import csv,json,math,re,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'02_Piano_Frequenze/V0.4'))
from vco_tuning_v04 import (
 L_CANDIDATE_H,C_FIXED_EFFECTIVE_PF,F_LO_MIN,F_LO_MAX,
 C3_LOW_PF,C3_HIGH_PF,C30_TYP_PF,F_PFD,
 tank_ceq_pf,nominal_lo_hz,tuning_exponent,interpolated_varactor_pf,
 interpolated_voltage_v,sweep_all_channels,filter_pole_zero_hz,gate_rx)
SCH=ROOT/'04_KiCad/V0.4/PLL_PRESCALER_RX_V0.4.kicad_sch'
LIB=ROOT/'04_KiCad/V0.4/THT_V04.kicad_sym'
TABLE=ROOT/'04_KiCad/V0.4/sym-lib-table'
CFG=ROOT/'01_Specifiche/CONFIGURAZIONE_V0.4.json'
def balanced(text):
    depth=0;quoted=False;esc=False
    for char in text:
        if esc:esc=False;continue
        if quoted and char=='\\':esc=True;continue
        if char=='"':quoted=not quoted;continue
        if not quoted:
            if char=='(':depth+=1
            elif char==')':
                depth-=1
                if depth<0:return False
    return depth==0 and not quoted
class V04(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
    cls.sch=SCH.read_text(encoding='utf-8')
    cls.lib=LIB.read_text(encoding='utf-8')
    cls.cfg=json.loads(CFG.read_text(encoding='utf-8'))
    with (ROOT/'07_Componenti/BOM_VCO_PLL_CANDIDATI_V0.4.csv').open(newline='',encoding='utf-8') as f:
        cls.bom=list(csv.DictReader(f))
 def test_01_revision_current(self): self.assertEqual(self.cfg['revision'],'V0.4')
 def test_02_previous_v03_immutable(self):self.assertEqual(json.loads((ROOT/'01_Specifiche/CONFIGURAZIONE_V0.3.json').read_text())['revision'],'V0.3')
 def test_03_previous_v02_immutable(self):self.assertEqual(json.loads((ROOT/'01_Specifiche/CONFIGURAZIONE_V0.2.json').read_text())['revision'],'V0.2')
 def test_04_270_rx(self):self.assertEqual(len(sweep_all_channels()),270)
 def test_05_tune_all_model_channels(self):
    for line in sweep_all_channels():
        self.assertGreaterEqual(line['vtune_v_assumed'],3)
        self.assertLessEqual(line['vtune_v_assumed'],30)
        self.assertFalse(line['tx_permitted'])
 def test_06_ceff_low(self):self.assertAlmostEqual(tank_ceq_pf(F_LO_MIN),87.330326658,places=4)
 def test_07_ceff_high(self):self.assertAlmostEqual(tank_ceq_pf(F_LO_MAX),75.698690785,places=4)
 def test_08_required_varicap(self):
    self.assertAlmostEqual(tank_ceq_pf(F_LO_MIN)-C_FIXED_EFFECTIVE_PF,29.830326658,places=3)
    self.assertAlmostEqual(tank_ceq_pf(F_LO_MAX)-C_FIXED_EFFECTIVE_PF,18.198690785,places=3)
 def test_09_3v_cap_variability(self):
    self.assertEqual((C3_LOW_PF,C3_HIGH_PF,C30_TYP_PF),(34.,39.,14.))
 def test_10_cap_at_low_3v_cover_in_ideal(self):self.assertLess(nominal_lo_hz(C3_LOW_PF),F_LO_MIN)
 def test_11_cap_30v_typ_only_cover_in_ideal(self):self.assertGreater(nominal_lo_hz(C30_TYP_PF),F_LO_MAX)
 def test_12_power_law_anchor(self):
    self.assertAlmostEqual(interpolated_varactor_pf(3),36.5,places=6)
    self.assertAlmostEqual(interpolated_varactor_pf(30),14.0,places=6)
 def test_13_gamma_range(self):self.assertTrue(0.4<tuning_exponent()<0.5)
 def test_14_interpolated_voltages(self):
    self.assertAlmostEqual(interpolated_voltage_v(F_LO_MIN),4.871901835,places=4)
    self.assertAlmostEqual(interpolated_voltage_v(F_LO_MAX),15.97358953,places=4)
 def test_15_roundtrip_270_math_only(self):
    for row in sweep_all_channels():
        self.assertAlmostEqual(nominal_lo_hz(interpolated_varactor_pf(row['vtune_v_assumed'])),row['lo1_hz'],delta=0.01)
 def test_16_outside_voltage_raises(self):
    for v in (1,31):
        with self.assertRaises(ValueError):interpolated_varactor_pf(v)
 def test_17_bad_lc_raises(self):
    with self.assertRaises(ValueError):tank_ceq_pf(0)
    with self.assertRaises(ValueError):nominal_lo_hz(-1)
 def test_18_filter_pole_and_zero(self):
    f=filter_pole_zero_hz()
    self.assertAlmostEqual(f['pole_hz'],130.454,delta=0.2)
    self.assertAlmostEqual(f['zero_hz'],159.155,delta=0.2)
 def test_19_filter_below_pfd(self):
    f=filter_pole_zero_hz();self.assertTrue(0<f['pole_hz']<f['zero_hz']<F_PFD)
 def test_20_filter_not_claim_closed_loop(self):self.assertFalse(filter_pole_zero_hz()['closed_loop_stable_verified'])
 def test_21_gate_all_false_tx(self):
    for pll in (True,False):
      for rail in (True,False):
        d=gate_rx(pll_lock=pll,valid_n=True,ref_ok=True,rail_ok=rail,retune_complete=True)
        self.assertFalse(d['rf_tx_enable']);self.assertFalse(d['fab_authorized'])
 def test_22_missing_power_mutes(self):
    r=gate_rx(pll_lock=True,valid_n=True,ref_ok=True,rail_ok=False,retune_complete=True)
    self.assertFalse(r['rx_unmute_candidate'])
 def test_23_schematic_exists_and_signature(self):
    self.assertIn('(kicad_sch',self.sch)
    self.assertIn('PLL_PRESCALER_RX_V0.4',self.sch)
 def test_24_schematic_balanced(self):self.assertTrue(balanced(self.sch))
 def test_25_custom_symbols_balanced(self):self.assertTrue(balanced(self.lib))
 def test_26_footprints_tht_only(self):
    self.assertIn('Package_DIP:DIP-14_W7.62mm',self.sch)
    self.assertIn('Connector_PinHeader_2.54mm:PinHeader_1x02',self.sch)
    self.assertNotIn('Package_SO',self.sch)
    self.assertNotIn('Resistor_SMD:',self.sch)
 def test_27_local_symbol_table(self):
    self.assertIn('THT_V04.kicad_sym',TABLE.read_text())
    self.assertIn('(symbol "TC74AC74P"',self.lib)
 def test_28_five_schematic_instances(self):
    self.assertEqual(self.sch.count('(symbol (lib_id '),5)
 def test_29_two_no_connect(self):
    self.assertEqual(self.sch.count('(no_connect '),2)
 def test_30_correct_nets(self):
    for n in ('DIV2_QBAR','PRESCALER_RESET_N','PLL_FB_18M','LO1_CMOS_BUFFERED','+5V_PLL','GND'):
        self.assertIn('(label "'+n+'"',self.sch)
 def test_31_bom_is_tht_and_candidate_only(self):
    self.assertEqual(len(self.bom),9)
    self.assertTrue(all(('DIP' in r['contenitore_tht'] or 'TO-92' in r['contenitore_tht'] or 'THT' in r['contenitore_tht']) for r in self.bom))
    self.assertTrue(all('APPROVATO' not in r['stato_funzionale'] for r in self.bom))
 def test_32_no_pcb_and_no_erc(self):
    self.assertFalse(list((ROOT/'04_KiCad').rglob('*.kicad_pcb')))
    self.assertEqual(self.cfg['validation']['kicad_erc'],'NOT_RUN')
 def test_33_handoff_and_technical_report(self):
    self.assertIn('V0.4',(ROOT/'RIPRENDI_IN_UNA_NUOVA_CHAT.md').read_text()[:200])
    self.assertTrue((ROOT/'03_Verifiche/V0.4/RAPPORTO_TECNICO_V0.4.md').exists())
 def test_34_strict_project_constraints(self):
    b=self.cfg['build'];self.assertEqual((b['technology'],b['board_order_type'],b['assembly']),('THT_ONLY','BARE_PCB_ONLY','IN_HOUSE'))
    self.assertFalse(self.cfg['radio']['tx_authorized']);self.assertFalse(self.cfg['radio']['fabrication_authorized'])
if __name__=='__main__':unittest.main()
