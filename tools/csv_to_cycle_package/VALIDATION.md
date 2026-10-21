# Validation record

Checked on 12 October 2026 against the publication companion snapshot.

Environment: Python 3.14.6, jsonschema 4.26.0, Windows.

## Converter behaviour

All **31 tests passed**, with no skipped tests:

```sh
python -m unittest discover -s tools/csv_to_cycle_package -p "test_*.py" -v
```

The tests cover synthetic single- and multi-cycle inputs, expected CSV outputs, schema checks, input preservation and rejection of the specified malformed or inconsistent inputs. They also check optional future deprecation and canonical holding-time names. Single-cycle context preserves an externally supplied Boolean/null quality label; repeating a static label across cycles, passing a string as the Boolean label and supplying other Representative values are rejected.

## Catalogue and package checks

The 214-definition catalogue validates with 113 Core, 54 Draft and 47 Experimental entries. Catalogue names and IDs, asset codes, internal references and generated instance headers were checked. The 102 mapping groups and 529 assignments validate and resolve to existing target definitions; no dataset conversion was performed. Both example manifests, resource paths, CSV names, unit rows, value types and increasing time axes were checked. The publication catalogue contains no development aliases.

These are structural and synthetic behaviour checks. They do not validate measurement accuracy, the confidential acquisition or preparation of measured cycle 96184, source timing, unit-code equivalence, or the scientific equivalence of third-party mappings. The Draft expert review and Experimental derivations remain separate tasks.

## Inputs

Paths are relative to the repository root.

| File | SHA-256 |
| --- | --- |
| `parameterDefinition.json` | `cef8a02fda6f3f7f508e2321ff7923c875f10db15932646fb5c9d0918ae9415a` |
| `parameterDefinition.schema.json` | `5e3bd2d8a3640de6d285cd6102f4aa35b930a515982f8e9a450098ff1f5664e7` |
| `manifest.schema.json` | `3014b70364404f8a131afee555c8d17edc7ad27c1bc8d556850f3308fbbdfe32` |
| `tools/csv_to_cycle_package/csv_to_cycle_package.py` | `fd462e853d5b94d5a664b7a1535e58ac1800ce146101eab509cebecdb361a4d7` |
| `tools/csv_to_cycle_package/test_csv_to_cycle_package.py` | `5005202bbb7700e92b20362ccdb7ee38c4f409c50589e95e1fbbae860e455a68` |

The results apply to the inputs identified above. Changes to executable code or specification files require corresponding revalidation.
