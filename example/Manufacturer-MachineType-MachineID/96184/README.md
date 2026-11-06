# Prepared measured cycle 96184

This example contains process data acquired by the authors on a physical Arburg injection-moulding machine. It demonstrates the parameter names, file roles and cycle-package structure described by the specification.

The package contains:

- `manifest.json`: cycle identity, available context and resource inventory.
- `actual_set_parameters/set_96184.csv`: prepared settings.
- `actual_set_parameters/actual_96184.csv`: prepared cycle-level actual values.
- `timeseries/timeseries_96184.csv`: prepared time-resolved machine values.
- This README, inventoried as `supplementary` documentation.

The CSV files retain the existing prepared values. Their first row contains canonical headers and their second row contains units. The distributed files preserve the prepared observations and cycle assignment. The original derivation of the time axis and configured sampling interval is not documented in the distributed materials. The manifest records the preparation policy `first_set_last_actual`; the original acquisition and preparation implementation is not included.

Raw source exports exposing Arburg-specific OPC UA node names have been excluded from publication. The acquisition software and detailed industrial interface mappings are not distributed because of the industrial research confidentiality constraints described by the authors. This prepared package illustrates the resulting storage representation; it does not reproduce the complete machine-to-package processing chain. The optional `raw/` folder is therefore absent.

The separate converter in `tools/csv_to_cycle_package/` did not generate this measured example.

This package contains no detailed quality file, and `measuredQualityCycleIsGood` is `null`. No quality label, inspection result or acceptance criterion should be inferred for this cycle. The separate fictional package `000001` illustrates the Quality-Long layout with invented values.

Machine-reported pressure, clamping force and other signals retain the manufacturer's measurement or calculation basis. A common name and unit do not establish equivalence across manufacturers, machine designs or individual machines. Document available source meaning and acquisition conditions when reusing the data, and treat unavailable internal calculations or sensor details as unknown.
