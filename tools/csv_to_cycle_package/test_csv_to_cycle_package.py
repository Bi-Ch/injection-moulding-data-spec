"""Behaviour checks for the publication example; run with unittest discover."""

import csv
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

import csv_to_cycle_package as converter


HERE = Path(__file__).resolve().parent
EXAMPLES = HERE / "examples"


class ConversionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="csv-cycle-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "source.csv"
        self.source.write_bytes((EXAMPLES / "multi_cycle.csv").read_bytes())
        self.mapping = json.loads((EXAMPLES / "mapping.json").read_text(encoding="utf-8"))
        self.context = json.loads((EXAMPLES / "context.json").read_text(encoding="utf-8"))
        self.output = self.root / "result"

    def run_conversion(self, cycle_id=None):
        mapping_path = self.root / "mapping.json"
        context_path = self.root / "context.json"
        mapping_path.write_text(json.dumps(self.mapping), encoding="utf-8")
        context_path.write_text(json.dumps(self.context), encoding="utf-8")
        return converter.convert(self.source, mapping_path, context_path, self.output, cycle_id=cycle_id)

    def assert_rejected(self, message):
        with self.assertRaisesRegex(ValueError, message):
            self.run_conversion()
        self.assertFalse(self.output.exists(), "No partial output may be published")
        self.assertEqual([], list(self.root.glob(".cycle-package-*")))

    def test_two_cycles_and_exact_expected_csv(self):
        before = self.source.read_bytes()
        manifests = self.run_conversion()
        self.assertEqual([p.parent.name for p in manifests], ["000001", "000002"])
        for manifest_path in manifests:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["nominalMaterialName"], "FictionalGrade-01")
            self.assertEqual(manifest["nominalDiameterScrew"], 25.0)
            self.assertEqual(len(manifest["resources"]), 3)
            self.assertNotIn("actualCountCycleMachine", manifest)
            self.assertTrue((manifest_path.parent / manifest["parameterDefinition"]).is_file())
            self.assertTrue((manifest_path.parent / manifest["$schema"]).is_file())
            for resource in manifest["resources"]:
                actual = manifest_path.parent / resource["path"]
                expected = EXAMPLES / "expected" / manifest["cycleId"] / actual.name
                self.assertEqual(actual.read_text(encoding="utf-8"), expected.read_text(encoding="utf-8"))
        for name in ("parameterDefinition.json", "parameterDefinition.schema.json", "manifest.schema.json"):
            self.assertEqual((self.output / "_definitions" / name).read_bytes(),
                             (converter.SPECIFICATION / name).read_bytes())
        self.assertEqual(before, self.source.read_bytes())

    @unittest.skipUnless(importlib.util.find_spec("jsonschema"), "Install requirements-test.txt for schema verification")
    def test_output_against_published_json_schemas(self):
        from jsonschema import Draft202012Validator, FormatChecker
        manifests = self.run_conversion()
        for data_name, schema_name in [("parameterDefinition.json", "parameterDefinition.schema.json")]:
            schema = json.loads((converter.SPECIFICATION / schema_name).read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schema)
            Draft202012Validator(schema).validate(json.loads((self.output / "_definitions" / data_name).read_text(encoding="utf-8")))
        schema = json.loads((converter.SPECIFICATION / "manifest.schema.json").read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        for manifest in manifests:
            validator.validate(json.loads(manifest.read_text(encoding="utf-8")))

    def test_already_segmented_cycle(self):
        self.source.write_bytes((EXAMPLES / "single_cycle.csv").read_bytes())
        del self.mapping["cycle_column"]
        paths = self.run_conversion(cycle_id="000007")
        self.assertEqual(paths[0].parent.name, "000007")
        self.assertTrue((paths[0].parent / "timeseries/timeseries_000007.csv").is_file())

    def test_optional_roles_and_missing_values(self):
        del self.mapping["set"]
        del self.mapping["timeseries"]
        self.source.write_text("cycle,barrel_temperature_1_actual\n000001,\n", encoding="utf-8")
        paths = self.run_conversion()
        manifest = json.loads(paths[0].read_text())
        self.assertEqual(manifest["resources"], [{"path": "actual_set_parameters/actual_000001.csv", "role": "actualParameters"}])
        with (paths[0].parent / manifest["resources"][0]["path"]).open(encoding="utf-8", newline="") as handle:
            self.assertEqual(list(csv.reader(handle))[-1], [""])

    def test_input_unit_row_and_delimiter(self):
        self.mapping["delimiter"] = ";"
        self.mapping["has_unit_row"] = True
        lines = self.source.read_text().replace(",", ";").splitlines()
        lines.insert(1, "dimensionless;ms;°C;°C;bar;mm")
        self.source.write_text("\n".join(lines), encoding="utf-8")
        self.assertEqual(len(self.run_conversion()), 2)

    def test_unit_mismatch_does_not_relabel_values(self):
        self.mapping["timeseries"]["timeseriesPressureInjection"]["unit"] = "Pa"
        self.assert_rejected("input unit must be")

    def test_unit_row_mismatch(self):
        self.mapping["has_unit_row"] = True
        lines = self.source.read_text().splitlines()
        lines.insert(1, "dimensionless,ms,°C,°C,Pa,mm")
        self.source.write_text("\n".join(lines), encoding="utf-8")
        self.assert_rejected("unit row disagrees")

    def test_wrong_resource_role(self):
        self.mapping["timeseries"]["actualTemperatureBarrel_1"] = self.mapping["actual"].pop("actualTemperatureBarrel_1")
        self.assert_rejected("not a time series")

    def test_invalid_instance(self):
        self.mapping["set"]["setTemperatureBarrel_0"] = self.mapping["set"].pop("setTemperatureBarrel_1")
        self.assert_rejected("Unknown or ambiguous")

    def test_unknown_key_is_not_silently_ignored(self):
        self.mapping["set"]["setTemperatureBarrel_1"]["scale"] = 10
        self.assert_rejected("Unknown keys")

    def test_set_changes_need_explicit_selection(self):
        self.source.write_text(self.source.read_text().replace("000001,10,200", "000001,10,201"), encoding="utf-8")
        self.assert_rejected("changes within a cycle")
        self.mapping["set"]["setTemperatureBarrel_1"]["select"] = "first"
        self.assertEqual(len(self.run_conversion()), 2)

    def test_repeated_counter_is_rejected(self):
        with self.source.open("a", encoding="utf-8") as handle:
            handle.write("000001,30,200,200,100,10\n")
        self.assert_rejected("Repeated cycle block")

    def test_decreasing_counter_is_rejected(self):
        self.source.write_text(self.source.read_text().replace("000002", "000000"), encoding="utf-8")
        self.assert_rejected("Decreasing/repeated")

    def test_bad_time_in_second_cycle_publishes_nothing(self):
        self.source.write_text(self.source.read_text().replace("000002,20", "000002,5"), encoding="utf-8")
        self.assert_rejected("increase strictly")

    def test_nonfinite_number_is_rejected(self):
        self.source.write_text(self.source.read_text().replace(",250,", ",NaN,"), encoding="utf-8")
        self.assert_rejected("finite")

    def test_incomplete_csv_rows_are_rejected(self):
        self.source.write_text(self.source.read_text().replace("000002,20,210,210,260,21", "000002,20,210"), encoding="utf-8")
        self.assert_rejected("expected 6 cells")

    def test_duplicate_csv_headers_are_rejected(self):
        self.source.write_text(self.source.read_text().replace("pressure_bar,position_screw_mm", "pressure_bar,pressure_bar"), encoding="utf-8")
        self.assert_rejected("unique")

    def test_unclosed_csv_quote_is_rejected(self):
        self.source.write_text('cycle,barrel_temperature_1_actual\n000001,"200', encoding="utf-8")
        del self.mapping["set"]
        del self.mapping["timeseries"]
        with self.assertRaises(csv.Error):
            self.run_conversion()
        self.assertFalse(self.output.exists())

    def test_context_cannot_override_inventory_or_process_files(self):
        self.context["manifest"]["resources"] = []
        self.assert_rejected("Generated field")
        del self.context["manifest"]["resources"]
        self.context["manifest"]["setTemperatureBarrel_1"] = 200
        self.assert_rejected("process values belong")

    def test_context_cavity_range_and_numeric_type(self):
        self.context["manifest"]["descriptionMouldCavity_2"] = "Second cavity"
        self.assert_rejected("exceeds the cavity count")
        del self.context["manifest"]["descriptionMouldCavity_2"]
        self.context["manifest"]["nominalDiameterScrew"] = "25"
        self.assert_rejected("JSON type")

    def test_static_cycle_start_cannot_be_repeated(self):
        self.context["manifest"]["actualTimeCycleStart"] = "2026-01-01T10:00:00Z"
        self.assert_rejected("only for single-cycle")

    def test_supplied_cycle_quality_label_is_preserved(self):
        self.source.write_bytes((EXAMPLES / "single_cycle.csv").read_bytes())
        del self.mapping["cycle_column"]
        for index, value in enumerate((True, False, None)):
            with self.subTest(value=value):
                self.output = self.root / f"label-{index}"
                self.context["manifest"]["measuredQualityCycleIsGood"] = value
                paths = self.run_conversion(cycle_id="000007")
                manifest = json.loads(paths[0].read_text(encoding="utf-8"))
                self.assertIs(manifest["measuredQualityCycleIsGood"], value)

    def test_static_cycle_quality_label_cannot_be_repeated(self):
        self.context["manifest"]["measuredQualityCycleIsGood"] = True
        self.assert_rejected("only for single-cycle")

    def test_representative_parameter_is_not_enabled_by_label_support(self):
        self.context["manifest"]["actualTemperatureBarrelRepresentative"] = 200
        self.assert_rejected("Representative derivations are outside")

    def test_cycle_quality_label_requires_json_boolean_or_null(self):
        self.context["manifest"]["measuredQualityCycleIsGood"] = "true"
        self.assert_rejected("JSON type")

    def test_unsafe_names(self):
        self.context["machine_folder"] = "../escape"
        self.assert_rejected("Unsafe")
        self.context["machine_folder"] = "CON"
        self.assert_rejected("Reserved")

    def test_existing_output_is_untouched(self):
        self.output.mkdir()
        sentinel = self.output / "important.txt"
        sentinel.write_text("keep")
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.run_conversion()
        self.assertEqual(sentinel.read_text(), "keep")

    def test_profile_requires_durations(self):
        self.mapping["set"] = {"setPressureHolding_1": {"column": "pressure_bar", "unit": "bar", "select": "first"}}
        self.assert_rejected("inconsistent companion")

    def test_duplicate_json_keys_are_rejected(self):
        path = self.root / "duplicate.json"
        path.write_text('{"set": {}, "set": {}}')
        with self.assertRaisesRegex(ValueError, "Duplicate JSON key"):
            converter.read_json(path)


class CatalogueCompatibilityTests(unittest.TestCase):
    def test_holding_duration_uses_canonical_name(self):
        catalogue = converter.Catalogue(converter.read_json(converter.SPECIFICATION / "parameterDefinition.json"))
        self.assertEqual(catalogue.resolve("actualTimeHoldingCumulative")["valueRole"], "actual")
        for previous_name in ("actualTimeHolding", "measuredTimeHolding"):
            with self.subTest(header=previous_name):
                with self.assertRaisesRegex(ValueError, "Unknown or ambiguous"):
                    catalogue.resolve(previous_name)

    def test_future_deprecation_is_rejected(self):
        for marker in ({"deprecated": True}, {"definitionStatus": "deprecated"}):
            with self.subTest(marker=marker):
                document = converter.read_json(converter.SPECIFICATION / "parameterDefinition.json")
                definition = next(p for p in document["parameters"]
                                  if p["variableName"] == "actualTimeHoldingCumulative")
                definition.update(marker)
                with self.assertRaisesRegex(ValueError, "Deprecated parameter"):
                    converter.Catalogue(document).resolve("actualTimeHoldingCumulative")


if __name__ == "__main__":
    unittest.main()
