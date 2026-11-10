"""CAD-first policy and KiCad-file structural checks (not a substitute for KiCad ERC)."""
import csv,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
V10=ROOT/"04_KiCad/V1.0"
class CADFirst(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
    cls.s=(V10/"PLL_FILTER_DRIVER_CAD_V1.0.kicad_sch").read_text()
    cls.lib=(V10/"THT_V10.kicad_sym").read_text()
    cls.generator=(V10/"genera_pll_filter_v10.py").read_text()
    cls.policy=(ROOT/"00_Gestione_Progetto/METODO_CAD_FIRST_V1.0.md").read_text()
    with (ROOT/"00_Gestione_Progetto/MATRICE_COPERTURA_CAD_V1.0.csv").open(newline="",encoding="utf-8") as f:
        cls.coverage=list(csv.DictReader(f))
    cls.wf=(ROOT/".github/workflows/cad_native_v10.yml").read_text()
 def test_01_real_kicad_sexpr(self):self.assertTrue(self.s.startswith("(kicad_sch (version 20250114)"))
 def test_02_compatible_symbol_library_version(self):self.assertIn("(kicad_symbol_lib (version 20241209)",self.lib)
 def test_03_generator_compiled(self):
    import ast
    ast.parse(self.generator)
 def test_04_known_native_symbol_instances(self):self.assertEqual(self.s.count("(symbol (lib_id"),13)
 def test_05_u803_analog_driver(self):
    self.assertIn('THT_V10:LM358N_PDIP8',self.s)
    self.assertIn('"U803"',self.s)
 def test_06_real_passive_network(self):
    for ref in ("R901","C901","R803","R804","R805","C805","C803"):
        self.assertIn('"'+ref+'"',self.s)
 def test_07_test_interfaces(self):
    for ref in ("J901","J902","J903"):self.assertIn('"'+ref+'"',self.s)
 def test_08_titled_nets(self):
    for net in ("PLL_PDOUT_3STATE","PD_FILTER","OPA_OUT_A","OPA_FB_A","VANA20_FILT","VTUNE_RAIL","GND"):
        self.assertIn('label "'+net+'"',self.s)
 def test_09_footprints_tht_only(self):
    for x in ("Package_DIP:DIP-8","Resistor_THT:","Capacitor_THT:","Connector_PinHeader_2.54mm:"):
        self.assertIn(x,self.s)
    self.assertNotIn("Package_SO:",self.s)
 def test_10_project_local_lib(self):
    self.assertIn('THT_V10',(V10/"sym-lib-table").read_text())
    self.assertIn('KIPRJMOD',(V10/"sym-lib-table").read_text())
 def test_11_generator_determinism_is_explicit_gate(self):
    self.assertIn('cmp "$RUNNER_TEMP/original.sch"',self.wf)
 def test_12_native_ERC_and_export_in_CI(self):
    for phrase in ("kicad-cli sch erc --exit-code-violations","kicad-cli sch export netlist","kicad-cli sym export svg"):
        self.assertIn(phrase,self.wf)
 def test_13_native_netlist_connectivity_gate(self):
    self.assertIn("verify_kicad_netlist_v10.py",self.wf)
 def test_14_traceable_coverage_matrix(self):
    self.assertEqual(len(self.coverage),14)
    self.assertEqual(self.coverage[0]["block_id"],"CAD-01")
 def test_15_alternative_values_open(self):
    self.assertIn("R901=22k",self.policy)
    self.assertIn("C901=100n",self.policy)
 def test_16_no_layout_or_drill_claim(self):
    self.assertFalse(list(V10.glob("*.kicad_pcb")))
 def test_17_keep_ngspice_tests(self):
    self.assertTrue((ROOT/"03_Verifiche/V0.9/test_v09.py").is_file())
 def test_18_no_fabrication(self):
    import json
    cfg=json.loads((ROOT/"01_Specifiche/CONFIGURAZIONE_CORRENTE.json").read_text())
    self.assertFalse(cfg["radio"]["fabrication_authorized"])
    self.assertFalse(cfg["radio"]["tx_authorized"])
if __name__=="__main__":unittest.main()
