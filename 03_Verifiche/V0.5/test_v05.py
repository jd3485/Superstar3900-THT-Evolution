"""V0.5: bench VCO mathematical checks, pin-net candidate and safe RX controller.
NOT SPICE execution, NOT KiCad ERC/DRC, NOT physical radio qualification.
"""
import csv,json,math,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'02_Piano_Frequenze/V0.5'))
sys.path.insert(0,str(ROOT/'08_Firmware_Prototipi/V0.5'))
from vco_dualvar_model_v05 import (
    L_NH,C_FIXED_PF_ASSUMED,M_FIT,CJO_FIT_PF,c_single_pf,effective_dual_varicap_pf,
    frequency_hz,required_vtune_v,all_channel_biases,passive_b_type_response_hz,
    two_rc_response_hz,magnitude_db,bjt_bias_estimate,safety_model)
from rx_controller_reference_v05 import RxController
CFG=ROOT/'01_Specifiche/CONFIGURAZIONE_CORRENTE.json'
PINS=ROOT/'01_Specifiche/V0.5/RETI_VCO_CANDIDATE_V0.5.csv'
SPICE=ROOT/'03_Verifiche/V0.5/VCO_COLPITTS_CANDIDATE_V0.5.cir'
class V05(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
    cls.cfg=json.loads(CFG.read_text(encoding='utf-8'))
    with PINS.open(newline='',encoding='utf-8') as f:cls.pins=list(csv.DictReader(f))
    cls.pinmap={(p['reference'],int(p['pin'])):p for p in cls.pins}
    cls.deck=SPICE.read_text(encoding='utf-8')
 def test_01_revision(self):self.assertEqual(self.cfg['revision'],'V0.5')
 def test_02_baseline_v04_frozen(self):
    self.assertEqual(json.loads((ROOT/'01_Specifiche/CONFIGURAZIONE_V0.4.json').read_text())['revision'],'V0.4')
 def test_03_bands_270(self):self.assertEqual(len(all_channel_biases()),270)
 def test_04_model_nominal_vtune_range(self):
    vv=[x['vtune_v_model'] for x in all_channel_biases()]
    self.assertGreater(min(vv),3.)
    self.assertLess(max(vv),8.)
 def test_05_vtune_roundtrip_all(self):
    for x in all_channel_biases():
      self.assertAlmostEqual(frequency_hz(x['vtune_v_model']),x['lo1_hz'],delta=.1)
 def test_06_tx_never_allowed_on_channels(self):
    self.assertTrue(all(not x['tx_permitted'] for x in all_channel_biases()))
 def test_07_dualvar_two_pieces(self):
    self.assertAlmostEqual(effective_dual_varicap_pf(3),1000*(2*36.5)/(1000+2*36.5),places=6)
 def test_08_anchor_c3_and_c30(self):
    self.assertAlmostEqual(c_single_pf(3),36.5,places=4)
    self.assertAlmostEqual(c_single_pf(30),14,places=4)
 def test_09_fit_exponent(self):self.assertTrue(0.4<M_FIT<0.5)
 def test_10_inductor_and_effective_fixed(self):
    self.assertEqual((L_NH,C_FIXED_PF_ASSUMED),(150.,61.))
 def test_11_bad_varicap_range(self):
    for x in (0.,2.9,30.1):
      with self.assertRaises(ValueError):c_single_pf(x)
 def test_12_input_filter_old_spur(self):
    db=magnitude_db(passive_b_type_response_hz(5000))
    self.assertAlmostEqual(db,-1.7257539239557629,places=5)
 def test_13_tworc_spur(self):
    self.assertAlmostEqual(magnitude_db(two_rc_response_hz(5000)),-41.4292144991,places=4)
 def test_14_candidate_is_not_stability_claim(self):
    self.assertIn('NOT SPICE',(ROOT/'03_Verifiche/V0.5/test_v05.py').read_text())
 def test_15_bjt_bias_order(self):
    b=bjt_bias_estimate()
    self.assertGreater(b['base_v_ideal'],2.)
    self.assertTrue(0.003<b['emitter_current_a_ideal']<0.005)
 def test_16_d501_three_physical_pins(self):
    self.assertEqual({int(p['pin']) for p in self.pins if p['reference']=='D501'},{1,2,3})
 def test_17_d501_both_anodes_parallel(self):
    self.assertEqual(self.pinmap['D501',1]['net'],'VAR_A')
    self.assertEqual(self.pinmap['D501',3]['net'],'VAR_A')
    self.assertEqual(self.pinmap['D501',2]['net'],'VTUNE_RAIL')
 def test_18_q501_three_pins(self):
    self.assertEqual({i:self.pinmap['Q501',i]['pin_name'] for i in range(1,4)},{1:'E',2:'B',3:'C'})
 def test_19_q502_three_pins(self):
    self.assertEqual({i:self.pinmap['Q502',i]['pin_name'] for i in range(1,4)},{1:'E',2:'B',3:'C'})
 def test_20_pins_unique(self):self.assertEqual(len(self.pinmap),len(self.pins))
 def test_21_spice_deck_contains_components(self):
    for x in ('Q501 TANK BASE1 EMIT1','Q502 V9 BASE2 EMIT2','D501A VAR_A VTUNE_RAIL','D501B VAR_A VTUNE_RAIL','L501 V9 TANK 150n'):
      self.assertIn(x,self.deck)
 def test_22_spice_is_not_claimed_vendor_model(self):
    self.assertIn('NOT an official MCC device model',self.deck)
    self.assertIn('not',self.deck.lower())
 def test_23_select_ch9(self):
    c=RxController(qualify_ticks=3)
    self.assertTrue(c.request('F',40,mode='USB',ch9=True))
    self.assertEqual((c.state.band,c.state.channel,c.state.mode,c.state.code_n),('D',9,'AM',3776))
 def test_24_select_270(self):
    c=RxController(qualify_ticks=2)
    for d in all_channel_biases():
      b=d['banda'];t=d['canale'];a=t.endswith('A')
      self.assertTrue(c.request(b,int(t.rstrip('A')),alpha=a))
      self.assertEqual(c.state.code_n,d['n'])
 def test_25_initial_muted(self):self.assertTrue(RxController().state.muted)
 def test_26_request_immediate_mute(self):
    c=RxController(qualify_ticks=2);c.request('D',9)
    c.tick(power_good=True,ref_ok=True,pll_lock=True,code_bus_stable=True)
    c.tick(power_good=True,ref_ok=True,pll_lock=True,code_bus_stable=True)
    self.assertFalse(c.state.muted)
    c.request('D',10)
    self.assertTrue(c.state.muted)
 def test_27_qualify_continuous_only(self):
    c=RxController(qualify_ticks=3);c.request('D',9)
    for i in range(2):self.assertFalse(c.tick(power_good=True,ref_ok=True,pll_lock=True,code_bus_stable=True))
    self.assertTrue(c.tick(power_good=True,ref_ok=True,pll_lock=True,code_bus_stable=True))
 def test_28_lock_loss_mutes_immediately(self):
    c=RxController(qualify_ticks=1);c.request('D',9)
    self.assertTrue(c.tick(power_good=True,ref_ok=True,pll_lock=True,code_bus_stable=True))
    self.assertFalse(c.tick(power_good=True,ref_ok=True,pll_lock=False,code_bus_stable=True))
 def test_29_invalid_channel_always_mute(self):
    c=RxController(qualify_ticks=1)
    self.assertFalse(c.request('Z',1))
    self.assertFalse(c.tick(power_good=True,ref_ok=True,pll_lock=True,code_bus_stable=True))
 def test_30_reset_forces_mute(self):
    c=RxController(qualify_ticks=1);c.request('D',9);c.reset()
    self.assertTrue(c.state.muted);self.assertIsNone(c.state.code_n)
 def test_31_no_tx_control(self):
    c=RxController(qualify_ticks=1);c.request('D',9)
    c.tick(power_good=True,ref_ok=True,pll_lock=True,code_bus_stable=True)
    self.assertFalse(c.state.tx_enabled)
    self.assertFalse(safety_model(all_stable=True,pll_lock=True)['rf_tx_enable'])
 def test_32_tht_supply_constraints(self):
    self.assertEqual(self.cfg['build']['technology'],'THT_ONLY')
    self.assertFalse(self.cfg['radio']['tx_authorized'])
    self.assertFalse(self.cfg['radio']['fabrication_authorized'])
 def test_33_spice_and_erc_not_qualified(self):
    self.assertEqual(self.cfg['validation']['kicad_erc'],'NOT_RUN')
    self.assertEqual(self.cfg['validation']['rf_lab'],'NOT_RUN')
 def test_34_report_and_handoff(self):
    self.assertIn('V0.5',(ROOT/'RIPRENDI_IN_UNA_NUOVA_CHAT.md').read_text()[:250])
    self.assertTrue((ROOT/'03_Verifiche/V0.5/RAPPORTO_TECNICO_V0.5.md').is_file())
if __name__=='__main__':unittest.main()
