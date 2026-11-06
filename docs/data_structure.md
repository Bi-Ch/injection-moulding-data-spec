# Creating a cycle package

A package contains the available observations for one cycle and a `manifest.json` linking its files. Select the parameters needed for the application; the convention does not require a fixed set or column order.

## Folders and resource roles

```text
<Manufacturer-MachineType-MachineID>/
  <cycleId>/
    manifest.json
    actual_set_parameters/
      set_<cycleId>.csv
      actual_<cycleId>.csv
    timeseries/
      timeseries_<cycleId>.csv
    metadata/
      measured_<cycleId>.csv
      measured_qualities_<cycleId>.csv
    raw/
```

The machine folder identifies the source machine. `cycleId` identifies the cycle within its documented scope and remains a string to preserve leading zeroes. The filenames shown are the convention used by the examples; readers resolve files through the manifest. Create only the files and directories needed for the available data.

| Location | Manifest role | Content |
| --- | --- | --- |
| `actual_set_parameters/set_<cycleId>.csv` | `setParameters` | Cycle settings, including profile segments and breakpoints. |
| `actual_set_parameters/actual_<cycleId>.csv` | `actualParameters` | Defined cycle-level actual process values. |
| `timeseries/timeseries_<cycleId>.csv` | `timeSeries` | Sampled signals and their relative time axis. |
| `metadata/measured_<cycleId>.csv` | `measuredMetadata` | Non-quality measured cycle values, such as material measurements. |
| `metadata/measured_qualities_<cycleId>.csv` | `measuredQualities` | Detailed quality observations in the [Quality-Long format](quality_long_draft.md). |
| `metadata/`, package documentation or `raw/` | `supplementary` | Inspection context, provenance, reports or unchanged source files. |

Preserve unchanged source exports under `raw/` when available. Their names, formats and internal layout remain source-specific. They are supplementary resources rather than canonical CSV files.

## CSV layout

Settings, actual values, non-quality measurements and time series use wide CSV files:

- Row 1 contains exact catalogue names or valid instance headers.
- Row 2 contains one unit per column: `unit.displayName`, or `unitSemantics` when the catalogue unit is null.
- Data starts in row 3. Cycle-value files contain one data row for the cycle; time-series rows contain observations on the stated time axis.

Use UTF-8, comma-separated fields, a decimal point and `true`/`false` for Boolean values, as in the supplied examples and converter. Quote CSV fields containing commas, quotes or line breaks. Keep the number of cells consistent with the header. Empty value cells represent missing observations, not zero or `false`; document why data is missing when known. Omit unused parameters rather than fabricating observations.

This excerpt retains the first two columns and both observations of the [fictional time series](../example/FictionalManufacturer-FictionalMachineType-FictionalMachineID/000001/timeseries/timeseries_000001.csv):

```csv
relativeTimestampCycle,timeseriesPressureInjection
ms,bar
0.0,0.0
2.0,12.5
```

`relativeTimestampCycle` expresses milliseconds from the documented cycle start. Preserve the actual observation times and describe any alignment or resampling. The manifest's nominal sampling interval does not replace this axis. Detailed quality files use a different layout, with units in each observation row.

## Manifest

The [manifest schema](../manifest.schema.json) requires four fields:

| Field | Meaning |
| --- | --- |
| `manifestVersion` | `1.0` for this structure. |
| `parameterDefinition` | Relative path to the exact catalogue used. |
| `cycleId` | Non-empty string matching the cycle folder. |
| `resources` | Non-empty array of files, each with `path` and `role`. |

For example, the fictional package inventories its time series as:

```json
{
  "path": "timeseries/timeseries_000001.csv",
  "role": "timeSeries"
}
```

Each resource path is relative to its manifest, uses `/`, names an existing file and occurs once. Resource paths cannot be absolute, contain a URI scheme or backslashes, or traverse a parent directory with `..`. List every included resource, including supplementary documentation and individual raw files. The manifest does not inventory itself or empty directories.

The catalogue pointer may use `..` to reach a shared catalogue. Both supplied examples use `../../../parameterDefinition.json`. Preserve that relationship when moving the package, or update the pointer and include the referenced catalogue. `$schema` may similarly identify the manifest schema.

## Context

Keep material, mould and nominal machine properties in the manifest under their canonical names. The context exceptions `actualCountCycleMachine`, `actualTimeCycleStart`, `actualTimestepSizeIMM` and `measuredTimeCreationFile` also belong there. The cycle-start and file-creation timestamps have different meanings. `actualTimestepSizeIMM` is a nominal interval in milliseconds.

Use `descriptionMouldCavity_1`, `descriptionMouldCavity_2` and further declared instances for cavity descriptions. Relate them to `nominalCountCavitiesMould`. Keep administrative information and provenance in `manifestMetadata` or a supplementary document.

`measuredQualityCycleIsGood` is the overall assessment: `true` means good, `false` means bad, and `null` means no assessment is available. Detailed observations belong in a `measuredQualities` resource, not a nested manifest object. Use native JSON types and only use null where the schema permits it; omit unavailable optional fields that do not permit null.

The [fictional manifest](../example/FictionalManufacturer-FictionalMachineType-FictionalMachineID/000001/manifest.json) provides a complete example. Apply the [validation checks](validation_rules.md) to the manifest and the files it references.
