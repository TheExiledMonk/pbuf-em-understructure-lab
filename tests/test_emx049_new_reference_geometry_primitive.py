import json, unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"runs"/"emx049"
def j(n): return json.loads((P/n).read_text())
class T(unittest.TestCase):
 def test_frozen_new_family_separation(self):
  c=j("frozen_new_reference_geometry_primitive_contract.json"); self.assertTrue(c["FROZEN_BEFORE_RESULTS"]); self.assertIn("not historical DEV167 provenance",c["provenance_separation"]); self.assertTrue(j("provenance_separation_statement.json")["emx047_emx048_preserved_unchanged"])
 def test_all_shape_comparisons_and_controls(self): self.assertEqual(len(j("cell_registry_and_results.json")["comparison_cells"]),8); self.assertTrue(all(x["classification"] in j("frozen_new_reference_geometry_primitive_contract.json")["classification_vocabulary"] for x in j("cell_registry_and_results.json")["comparison_cells"]))
 def test_rest_is_finite(self): self.assertEqual(j("cell_registry_and_results.json")["controls"]["rest_force"]["classification"],"COMPATIBLE_NONUNIQUE")
if __name__=="__main__": unittest.main()
