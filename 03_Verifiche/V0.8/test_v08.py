"""V0.8 engineering/traceability tests — static models only.

These tests do NOT execute vendor opamp, MC34063, LM317 or real PLL simulations.
They exercise mathematical envelopes and consistency of phase-driver candidate.
"""
import csv,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"02_Piano_Frequenze/V0.8"))
from vtune_headroom_v08 import (
 VIN_LEVELS,BOOST_TARGET_V,SWITCH_F_HZ_ASSUMED,L_H_CANDIDATE,
 R_SENSE_OHM_CANDIDATE,SENSE_TRIP_LOW_V_DATASHEET,
 BLEEDER_OHM,BLEEDER_WATT_RATING,LM358_GAIN_NOMINAL,
 BOOST_OUTPUT_CURRENT_DESIGN_A,MIN_LOAD_LM317_MAX_A,
 duty_budget,boost_divider_v,boost_divider_window,lm317_output,
 lm317_window,bleeder_min_load_amps,bleeder_watts_nominal,
 bleeder_watts_max_assumed,rc_ideal_db,vtune_input_for_output,
 minimum_output_high,lm358_dc_point,protection_logic,budget_summary)
def read_csv(rel):
 with (ROOT/rel).open(newline="",encoding="utf-8") as f:return list(csv.DictReader(f))
class V08(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
    cls.cfg=json.loads((ROOT/"01_Specifiche/CONFIGURAZIONE_V0.8.json").read_text())
    cls.v07=json.loads((ROOT/"01_Specifiche/CONFIGURAZIONE_V0.7.json").read_text())
    cls.evidence=json.loads((ROOT/"03_Verifiche/V0.8/MISURE_DRIVER_V0.8.json").read_text())
    cls.pins=read_csv("04_KiCad/V0.8/VTUNE_PINNET_V0.8.csv")
    cls.nets=read_csv("04_KiCad/V0.8/VTUNE_RETI_PASSIVE_V0.8.csv")
    cls.bom=read_csv("07_Componenti/BOM_VTUNE_V0.8.csv")
    cls.deck=(ROOT/"03_Verifiche/V0.8/VTUNE_DRIVER_BEHAVIORAL_V0.8.cir").read_text()
 def test_01_revision_current(self):self.assertEqual(self.cfg["revision"],"V0.8")
 def test_02_prev_config_immutable(self):self.assertEqual(self.v07["revision"],"V0.7")
 def test_03_old_spice_preserved(self):self.assertTrue((ROOT/"03_Verifiche/V0.7/BOOST_THT_BEHAVIORAL_V0.7.cir").is_file())
 def test_04_previous_vco_preserved(self):self.assertTrue((ROOT/"03_Verifiche/V0.6/VCO_COLPITTS_CANDIDATE_B_V0.6.cir").is_file())
 def test_05_pin_count(self):self.assertEqual(len(self.pins),19)
 def test_06_unique_pins(self):self.assertEqual(len({(p["reference"],int(p["pin"])) for p in self.pins}),19)
 def test_07_mc34063_all_8(self):self.assertEqual({int(p["pin"]) for p in self.pins if p["reference"]=="U701"},set(range(1,9)))
 def test_08_lm317_all_3(self):self.assertEqual({int(p["pin"]) for p in self.pins if p["reference"]=="U702"},{1,2,3})
 def test_09_lm358_all_8(self):self.assertEqual({int(p["pin"]) for p in self.pins if p["reference"]=="U803"},set(range(1,9)))
 def test_10_lm358_supply_and_feedback(self):
    m={(p["reference"],int(p["pin"])):p["net"] for p in self.pins}
    self.assertEqual(m["U803",8],"VANA20_FILT")
    self.assertEqual(m["U803",1],"OPA_OUT_A")
    self.assertEqual(m["U803",2],"OPA_FB_A")
    self.assertEqual(m["U803",3],"PD_FILTER")
    self.assertEqual(m["U803",4],"GND")
 def test_11_second_opamp_safe_follower(self):
    m={int(p["pin"]):p["net"] for p in self.pins if p["reference"]=="U803"}
    self.assertEqual(m[5],"GND")
    self.assertEqual(m[6],m[7])
 def test_12_pin_packages_tht(self):
    self.assertEqual({p["package"] for p in self.pins},{"DIP-8","TO-220-3","PDIP-8"})
 def test_13_nets_count(self):self.assertEqual(len(self.nets),22)
 def test_14_bom_complete(self):
    required={x["reference"] for x in self.pins}|{x["ref"] for x in self.nets}
    actual={x["ref"] for x in self.bom}
    self.assertEqual(required,actual);self.assertEqual(len(self.bom),25)
 def test_15_bom_only_tht(self):
    self.assertTrue(all(any(s in x["package_tht"] for s in ("PDIP","TO-220","THT","DO-41")) for x in self.bom))
 def test_16_rails(self):self.assertEqual((BOOST_TARGET_V,MIN_LOAD_LM317_MAX_A),(27.,.010))
 def test_17_worst_case_duty_ratio(self):
    b=duty_budget(11)
    self.assertAlmostEqual(b.on_off_ratio,1.65,places=8)
    self.assertAlmostEqual(b.duty,1.65/2.65,places=8)
 def test_18_worst_case_current_margin_from_zero_only(self):
    b=duty_budget(11)
    self.assertAlmostEqual(b.inductor_current_rise_a,.3311922923,places=5)
    self.assertAlmostEqual(b.minimum_current_limit_a,.25/.47,places=6)
    self.assertTrue(.19<b.current_margin_from_zero_a<.21)
 def test_19_all_input_points(self):
    self.assertEqual(VIN_LEVELS,(11.,13.8,15.5))
    self.assertTrue(all(0<duty_budget(v).duty<.8 for v in VIN_LEVELS))
 def test_20_vboost_divider(self):
    self.assertAlmostEqual(boost_divider_v(),26.9791666667,places=5)
    lo,hi=boost_divider_window()
    self.assertTrue(25.9<lo<26.0 and 28.0<hi<28.1)
 def test_21_lm317_output(self):
    self.assertAlmostEqual(lm317_output(),20.02225,places=5)
 def test_22_lm317_range(self):
    self.assertEqual(lm317_window(),(19.05,20.9945))
 def test_23_regulator_dropout_assumption_budget(self):
    min_boost,_=boost_divider_window();_,max_reg=lm317_window()
    self.assertGreater(min_boost-max_reg,4.9)
    self.assertFalse(budget_summary()["device_models_validated"])
 def test_24_minimum_load_improved(self):
    self.assertEqual(BLEEDER_OHM,2400.)
    self.assertGreater(bleeder_min_load_amps(),MIN_LOAD_LM317_MAX_A)
 def test_25_bleeder_watts(self):
    self.assertLess(bleeder_watts_max_assumed(),BLEEDER_WATT_RATING)
    self.assertTrue(.16<bleeder_watts_nominal()<.18)
 def test_26_filter_ideal_only(self):
    self.assertLess(rc_ideal_db(40_000),-47.9)
    self.assertFalse(budget_summary()["hardware_validated"])
 def test_27_lm358_gain(self):
    self.assertEqual(LM358_GAIN_NOMINAL,4.)
    self.assertEqual((vtune_input_for_output(8),vtune_input_for_output(15)),(2.,3.75))
 def test_28_min_high_output_assumed(self):self.assertAlmostEqual(minimum_output_high(),15.8)
 def test_29_high_headroom_still_blocked(self):
    self.assertLess(minimum_output_high(headroom=4.3),15)
    self.assertLess(lm358_dc_point(3.75,19.05,headroom=4.3),15)
 def test_30_six_ngspice_cases_recorded(self):
    self.assertEqual(len(self.evidence["observations"]),6)
    self.assertEqual(self.evidence["run_id"],42841818820)
 def test_31_ngspice_values_unqualified(self):
    x=self.evidence["observations"]
    self.assertAlmostEqual(x[0]["vtune_avg_v"],7.99792,places=4)
    self.assertAlmostEqual(x[2]["vtune_avg_v"],14.9961,places=4)
    self.assertLess(x[-1]["vtune_avg_v"],15)
    self.assertFalse(self.evidence["lm358_physical_model_present"])
 def test_32_deck_stated_ideal(self):
    self.assertIn("NOT actual ML145151",self.deck)
    self.assertIn("BAMP OPA_DRV",self.deck)
    self.assertNotIn(".SUBCKT LM358",self.deck.upper())
 def test_33_safe_mute_on_missing_supply(self):
    x=dict(vin_ok=True,boost_ok=True,reg20_ok=False,ref_ok=True,pll_lock=True,retune_done=True)
    self.assertFalse(protection_logic(**x)["rx_unmute_candidate"])
    x["reg20_ok"]=True;self.assertTrue(protection_logic(**x)["rx_unmute_candidate"])
 def test_34_no_tx_and_no_fab(self):
    self.assertFalse(self.cfg["radio"]["tx_authorized"])
    self.assertFalse(self.cfg["radio"]["fabrication_authorized"])
    self.assertFalse(self.evidence["pcb_authorized"])
 def test_35_erc_and_drc_not_executed(self):
    self.assertEqual(self.cfg["validation"]["kicad_erc"],"NOT_RUN")
    self.assertEqual(self.cfg["validation"]["kicad_drc"],"NOT_RUN")
 def test_36_report_and_handoff(self):
    self.assertTrue((ROOT/"03_Verifiche/V0.8/RAPPORTO_TECNICO_V0.8.md").is_file())
    self.assertTrue((ROOT/"03_Verifiche/V0.8/MISURE_DRIVER_V0.8.json").is_file())
if __name__=="__main__":unittest.main()
