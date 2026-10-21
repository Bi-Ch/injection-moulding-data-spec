# Injection moulding process data

This specification describes how to store injection-moulding process data so that it can be understood and reused independently of the original acquisition software. A parameter catalogue defines quantities, units and instance names. A folder for each machine cycle brings together settings, cycle results, time series, quality observations and their context through a manifest.

The scope is conventional thermoplastic injection moulding with one injection unit. The current catalogue is version `0.1.0-draft.1`, with release status `publicDraft`. It contains 214 parameter definitions: 113 Core, 54 Draft and 47 Experimental. Documentation is in English; parameter descriptions are available in English and German.

## Use the specification

1. **Understand the source data.** Establish the machine, cycle boundaries, reported quantities, units and acquisition times. Keep the available source documentation with the dataset.
2. **Choose matching definitions.** Find each quantity in [parameterDefinition.json](parameterDefinition.json). Check its meaning, role, representation, unit and maturity using the [parameter guide](docs/parameter_definition.md). Use the declared [instance patterns](docs/instances_and_representative_values.md) for zones, cavities, devices and profile segments.
3. **Assign values to cycles.** Apply a documented [cycle-value selection](docs/cycle_value_selection.md). Preserve the time origin and any transformations of sampled signals.
4. **Create the package.** Write the CSV files and `manifest.json` according to the [package layout](docs/data_structure.md). Add [quality observations](docs/quality_long_draft.md) and their [inspection context](docs/quality_inspection_template.md) when available.
5. **Check the result.** Follow the [validation guide](docs/validation_rules.md), then compare the exported values and their interpretation with the source.

For an existing dataset, start with [reading and assessing data](docs/reading_data.md). It explains what to check before comparing cycles or combining datasets.

## Examples and conversion

| Material | What it demonstrates |
| --- | --- |
| [Fictional cycle 000001](example/FictionalManufacturer-FictionalMachineType-FictionalMachineID/000001/README.md) | All six resource roles, profiles, heating zones and detailed quality observations. All identifiers and values are invented. |
| [Measured cycle 96184](example/Manufacturer-MachineType-MachineID/96184/README.md) | Prepared data from a physical Arburg machine, with settings, actual values and time series. No detailed quality observations or overall quality assessment are provided. |
| [CSV converter](tools/csv_to_cycle_package/README.md) | A runnable example for converting an already aligned CSV using an explicit column mapping and context configuration. |

The converter requires Python 3.10 or later. Its examples are synthetic, and it did not generate the measured package. Source-specific acquisition, unit conversion and alignment must be completed before using it. The [dataset correspondence register](docs/dataset_parameter_mappings.md) can help interpret published source names; it is separate from the converter's mapping configuration.

## Reference files

| File | Purpose |
| --- | --- |
| [parameterDefinition.json](parameterDefinition.json) | Parameter meanings, units, roles, maturity and instance rules. |
| [parameterDefinition.schema.json](parameterDefinition.schema.json) | Structure of the parameter catalogue. |
| [manifest.schema.json](manifest.schema.json) | Required cycle identity, resource inventory and selected context constraints. |
| [docs/assetVocabulary.json](docs/assetVocabulary.json) | Controlled asset codes used by the catalogue. |
| [mappings/datasetParameterMappings.json](mappings/datasetParameterMappings.json) | Qualified correspondences to published dataset fields. |

Search queries and screening records are retained under [research/](research/). The parameter guide explains the catalogue's informative standards references and versioning rules.

## Status and reuse

Core, Draft and Experimental describe the maturity of a definition, not the accuracy of an observation. Quality-Long remains a design draft without a separate machine-readable schema. Machine-specific measurement methods, representative-value calculations and quality criteria remain part of the dataset documentation.

Keep the exact catalogue used with the data when archiving or exchanging a package. The draft has no assigned licence or completed archival DOI. The repository is intended to accompany the publication; its current status does not establish permission to reuse third-party datasets.
