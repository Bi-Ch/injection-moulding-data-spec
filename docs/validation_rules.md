# Checking a dataset

Check the catalogue and manifests, then the referenced files, then their meaning against the source. JSON Schema validation covers structure and declared constraints; it does not inspect CSV contents or establish measurement accuracy.

## 1. Validate JSON structures

Use a JSON Schema Draft 2020-12 validator for these pairs:

| Data | Schema |
| --- | --- |
| `parameterDefinition.json` | `parameterDefinition.schema.json` |
| Each cycle's `manifest.json` | `manifest.schema.json` |
| `mappings/datasetParameterMappings.json` | `mappings/datasetParameterMappings.schema.json` |

Enable date/time format checking. This Python example checks the repository catalogue, correspondence register and example manifests. Run it from the repository root with `jsonschema` installed; the dependency is listed in the converter's [test requirements](../tools/csv_to_cycle_package/requirements-test.txt).

```python
import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))

checks = [
    (Path("parameterDefinition.json"), Path("parameterDefinition.schema.json")),
    (Path("mappings/datasetParameterMappings.json"),
     Path("mappings/datasetParameterMappings.schema.json")),
]
checks.extend(
    (path, Path("manifest.schema.json"))
    for path in sorted(Path("example").rglob("manifest.json"))
)
for data_path, schema_path in checks:
    schema = read_json(schema_path)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    validator.validate(read_json(data_path))
    print(f"Valid: {data_path}")
```

For another dataset, apply the manifest check to its cycle directories and the catalogue it references. A successful run establishes only the JSON checks above.

## 2. Check references and resources

- Resolve the catalogue pointer and use that catalogue version for all subsequent checks.
- Require unique catalogue names and identifiers. Resolve definition relationships and check asset codes against [assetVocabulary.json](assetVocabulary.json) and the schema enum.
- Match `cycleId` to its cycle folder and any cycle suffix used in filenames.
- Require existing resource files, unique inventory paths, permitted roles and paths confined to the cycle package. A shared catalogue pointer may traverse to a parent directory; resource paths may not.
- Check parameter-backed manifest keys against the catalogue, including instance rules and value types. The manifest schema permits additional properties, so schema acceptance alone does not validate them.
- Keep process settings and actual values in their CSV resources. Only documented context belongs in the manifest; detailed quality is a resource rather than a nested `measuredQualities` object.

## 3. Check observations

| Check | Expected result |
| --- | --- |
| Wide CSV structure | Unique headers, one matching unit cell per column, consistent row widths and values of the declared type. |
| Units | Exact catalogue display units or unit-semantics tokens; any source conversion is documented. |
| File role | Settings, cycle actuals, time series and non-quality measurements match their catalogue roles and representations. |
| Instance headers | Declared patterns, numeric indices from 1, permitted controlled codes and documented physical associations. |
| Profiles | Paired holding pressures and durations; contiguous velocity segments with exactly `N - 1` matching internal breakpoints. |
| Time series | Documented cycle origin, ordered observation times and explained gaps or transformations; no assumption of regularity from a nominal interval alone. |
| Quality-Long | Six columns, no unit row, exactly one typed value per observation and distinguishing times for repeated parameter-instance pairs. |
| Cavity descriptions | Non-empty indexed descriptions, with indices within the stated cavity count when available. |
| Derived or representative values | Source observations and method are retained, including required geometry, selection and weighting. |

For a derived screw peripheral velocity, the catalogue relates `timeseriesRevolutionsScrew` in r/min and positive `nominalDiameterScrew` in mm through `v = pi * d * n / 60`, yielding mm/s. Check alignment and documented rounding. This circumferential velocity is distinct from the axial `timeseriesVelocityScrew`, even though both use mm/s.

Supplementary raw files retain their original format. Validate their inventory and provenance without applying canonical CSV rules to their contents.

## 4. Compare with the source

Review cycle assignment, units, measurement basis, time transformations and quality polarity against the source documentation and observations. Sample exported values across cycles and instances. Record missing context and the scope of the checks with the dataset. Schema validity cannot resolve an ambiguous sensor location, verify calibration or justify a statistical summary.

The [CSV converter tests](../tools/csv_to_cycle_package/README.md#checks-and-tests) exercise the converter's supported input and output. They are not a complete dataset validator and do not validate the industrial acquisition behind measured cycle 96184. The [reading guide](reading_data.md) identifies context needed to judge reuse.
