# Reading and assessing data

Begin with the cycle's `manifest.json`, the referenced parameter catalogue and the package documentation. These establish which files belong together and what their values represent. Data can be structurally valid while still lacking the context needed for a particular analysis.

## Read a package

1. Resolve `parameterDefinition` relative to the manifest and check the catalogue version.
2. Identify the source machine and the scope of `cycleId`. Preserve leading zeroes and distinguish it from a resettable job counter.
3. Select files by their resource `role`. Optional observations may be absent; an absent quality file does not indicate a good part.
4. For wide CSV files, read the names and unit row before parsing observations. Resolve indexed headers through the catalogue's `instances` definitions. Quality-Long has units per observation and no second header row.
5. Read acquisition, transformation and inspection context before comparing values.

The [package layout](data_structure.md), [parameter guide](parameter_definition.md) and [quality guide](quality_long_draft.md) describe these steps in detail.

## Decide whether values are comparable

| Question | Information to establish |
| --- | --- |
| What was observed? | Setting, sampled signal, reported cycle result, additional measurement or assessment; measured and simulated values remain distinguishable. |
| Where and how? | Source device, measurement location, pressure or coordinate basis, calculation or aggregation method, and available calibration information. |
| When? | Cycle assignment, time origin, sampling intervals, missing samples, alignment and any resampling. |
| Which instance? | Physical zone, cavity, device or sensor corresponding to each index, including changes between runs. |
| In which process context? | Machine configuration, mould, material and operating conditions relevant to the comparison. |
| Which preparation? | Source fields, unit conversions, selection rules, derived values and retained raw data. |
| Which assessment? | Inspection method, acceptance criteria, label polarity and handling of uninspected parts. |

Record unavailable information as unknown. A common name and unit do not establish equivalent sensors, calculations or operating conditions across machines. `measurementLocation.kind: "machineInternalUnspecified"`, for example, does not identify a physical sensor.

An `actualTemperatureBarrel_1` value represents one documented cycle value for an indexed interior heating zone. Its index does not establish the same physical location on another machine, and its definition requires the source-specific sampling or aggregation method. The [instance guide](instances_and_representative_values.md) explains zone association and summaries across instances.

For time series, use `relativeTimestampCycle` and the stated cycle origin. `actualTimestepSizeIMM` records a nominal configured interval; it does not prove regular sampling or synchronisation between sources. File creation time is not acquisition time.

## Quality and representative values

`measuredQualityCycleIsGood` is an assessment under a dataset's own criteria. `true` means good and `false` means bad; `null` means no assessment. For an `IsPresent` defect observation, `true` means the defect was observed. These polarities must remain distinct.

Reassessment against another tolerance is possible only when the relevant observation and its part or cycle association were retained. A binary label alone cannot reconstruct a measurement. Numeric defect intensities and Representative values need their documented scales or derivation methods before they can be compared.

## Preserve enough context for reuse

Keep the catalogue, manifests, resources and supplementary documentation together. Record the acquisition source and available version, mapping from source fields, unit and time transformations, instance associations and cycle-selection rules. A shared method can be documented once in a stable, versioned dataset document referenced by cycle documentation. Files inventoried directly by a cycle manifest must remain inside that cycle package.

Review the example packages with their stated scope: [cycle 000001](../example/FictionalManufacturer-FictionalMachineType-FictionalMachineID/000001/README.md) is fictional; [cycle 96184](../example/Manufacturer-MachineType-MachineID/96184/README.md) is a prepared measured example whose raw exports and acquisition implementation are not distributed. Neither supplies a general validation of measurements from other machines.
