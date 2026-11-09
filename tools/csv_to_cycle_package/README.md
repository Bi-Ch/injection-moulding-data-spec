# CSV to cycle package

The sole purpose of this converter is to provide a basic starting point for parsing existing injection-moulding data according to this repository's parameter catalogue and cycle-package convention.
It maps CSV columns to `set`, `actual` and `timeseries` resources. A separate JSON file supplies material, mould and other manifest context.

The implementation was written against the public specification. It contains no machine connection, industrial acquisition source code, measuring-chart decoder or confidential manufacturer mapping. Every supplied input and mapping is synthetic.
It did **not** generate the measured Arburg example `96184`.

## Run the examples

Python 3.10 or later is required. The converter uses only the standard library; no installation is needed. Run these commands from the **repository root**:

```sh
python tools/csv_to_cycle_package/csv_to_cycle_package.py --input tools/csv_to_cycle_package/examples/multi_cycle.csv --mapping tools/csv_to_cycle_package/examples/mapping.json --context tools/csv_to_cycle_package/examples/context.json --output tools/csv_to_cycle_package/output-demo
```

The input has two consecutive cycle blocks, identified by `cycle`. Leading zeroes in `000001` and `000002` are preserved. Each row is an observation with a relative time, repeated setting, actual temperature and two sampled signals.

For a file already belonging to a single cycle, omit `cycle_column` from the mapping and pass the cycle ID explicitly:

```sh
python tools/csv_to_cycle_package/csv_to_cycle_package.py --input tools/csv_to_cycle_package/examples/single_cycle.csv --mapping tools/csv_to_cycle_package/examples/mapping_single_cycle.json --context tools/csv_to_cycle_package/examples/context.json --cycle-id 000007 --output tools/csv_to_cycle_package/output-single
```

Use a **new output directory** for every run; its parent must already exist. Existing output is never updated or overwritten. Output is assembled in a private temporary directory and moved into place only after all cycles are processed. The inputs and specification files are read only.

## Mapping configuration

The keys within `set`, `actual` and `timeseries` are exact canonical output headers:

```json
{
  "cycle_column": "cycle",
  "set": {
    "setTemperatureBarrel_1": {"column": "barrel_temperature_1_setting", "unit": "°C"}
  },
  "actual": {
    "actualTemperatureBarrel_1": {"column": "barrel_temperature_1_actual", "unit": "°C", "select": "last"}
  },
  "timeseries": {
    "relativeTimestampCycle": {"column": "cycle_time_ms", "unit": "ms"},
    "timeseriesPressureInjection": {"column": "pressure_bar", "unit": "bar"}
  }
}
```

| Option | Meaning |
| --- | --- |
| `cycle_column` | Source grouping field. Each cycle must occupy one contiguous block. Mutually exclusive with `--cycle-id`. |
| `delimiter` | Optional single-character CSV delimiter; default `,`. |
| `has_unit_row` | Optional Boolean; default `false`. When `true`, the second input row is checked against mapped units. |
| `column` | Exact input header, case sensitive. |
| `unit` | Required declaration of the input unit. Must equal the catalogue's `unit.displayName`, or its `unitSemantics` for unitless parameters. |
| `select` | For `set`/`actual` only: `constant` (default), `first` or `last`. |

`constant` requires all observations in the cycle to agree, including missing values. For a declared case-insensitive enumeration, capitalization-only changes still agree. `first` and `last` select the literal first/last observation; they do not skip empty cells. Choose them only when that selection matches the intended parameter definition. In the synthetic example, the last temperature is expressly chosen as the cycle actual value. This is not a universal acquisition rule.

No conversion is inferred from a unit label. Convert other units explicitly before import and document that preprocessing. The parser checks declarations and optional unit rows; it cannot establish the physical correctness of a mapping.

Omit unused resource groups or leave them empty. At least one mapped value is required. Unmapped source columns are ignored. Missing mapped columns and unknown configuration keys are errors. Indexed headers follow the catalogue, including one-based numeric indices and controlled asset codes. Deprecated names and legacy aliases are not accepted as canonical output.

Profile interpolation is an optional scalar setting in the `set` mapping. Use the catalogue's `Steps` or `Ramps` mode and declare its unit as `notApplicable`. The four selectors accept any capitalization, including `steps`, `ramps`, uppercase and mixed case, through `allowedValuesCaseSensitive: false`. The converter preserves the selected input value's spelling. Parameter names, headers and asset codes remain case-sensitive; allowed-value matching is case-sensitive when the flag is absent. An absent selector remains unknown; the converter does not default it to `Steps`.
When a holding-pressure profile is included with `Ramps`, also supply the declared starting-pressure value, `setPressureInjectionLimit`. The [profile guide](../../docs/instances_and_representative_values.md#profile-interpolation) explains why holding-pressure ramps and velocity ramps interpret segment values differently. The converter stores these settings without generating a trajectory.

Ejector profiles have fixed step behaviour and use explicit segment indices such as `setVelocityEjectorForward_1`, `setPositionEjectorForward_1` and `setForceEjectorForward_1`. Every forward segment needs an end position. Backward profiles may omit only the final end-position column; the catalogue then defines that endpoint as 0 mm, without the converter adding a column or value. A recorded position cell cannot be empty. Force limits may be omitted; if a force-limit block is mapped, its indices must cover the velocity segments and any supplied values must be nonnegative. Negative positions and velocities retain their signs. See the [ejector profile rules](../../docs/instances_and_representative_values.md#ejector-profiles).

## Input and cycle boundaries

Input is one UTF-8 CSV file with a unique header, decimal point `.` and one row per observation. All mapped signals must already share that row's time and cycle assignment. Blank cells remain missing; `NaN` and infinities are rejected. Boolean values use `true`/`false`. Object-valued parameters are outside this example's scope. The small implementation loads the input into memory. Very large datasets require an application-specific extension that reads and writes one cycle at a time.

For time series, map `relativeTimestampCycle` in **milliseconds**. It must be nonnegative and strictly increasing within each cycle. Input may start after zero: the parser does not subtract the first sample, invent a cycle start, infer a sampling frequency, sort, resample or interpolate. Absolute timestamps must first be related to a documented cycle origin outside this parser.

Consecutive changes in `cycle_column` delimit cycles. A repeated block, a decrease in numeric cycle IDs, or a case-insensitive ID collision is rejected. Split counter resets or separate acquisition runs explicitly before import and use separate output roots. Nonconsecutive increasing counter values are allowed; missing cycles are not fabricated. A package ID is not automatically also a machine cycle counter.

The tool cannot establish whether the first or last observed cycle is complete, or assign delayed machine results to their correct cycle. Each manifest therefore records `cycleCompleteness: "notAssessed"` inside its provenance. The data provider must verify boundaries, especially in partial exports. If the material or mould changes, split the input into separate runs with appropriate context configs.

## Manifest configuration

See [examples/context.json](examples/context.json). `machine_folder` selects the machine directory. `manifest` supplies canonical `nominal*`/`description*` fields, optional permitted cycle context and `manifestMetadata` for administrative notes. Use native JSON types, for example `25` for screw diameter and `true` for a Boolean. Units of context values are the catalogue units. The config applies to every cycle.

Generated fields (`cycleId`, `resources`, `parameterDefinition`, `$schema`, `manifestVersion`, `measuredTimeCreationFile`) cannot be overridden. Process values belong in their CSV resources. A configured `actualTimeCycleStart` or `actualCountCycleMachine` is permitted only with single-cycle input. The creation timestamp is generated in UTC; no acquisition timestamp is inferred.

## Supplied cycle-quality label

For a single-cycle conversion, manifest context may contain `measuredQualityCycleIsGood` as JSON `true`, `false` or `null`. The converter preserves this externally supplied assessment; it does not compute or verify the acceptance rule. Document that rule and its version in supplementary inspection context. A static cycle-quality label is rejected for multi-cycle input so that one cycle's assessment cannot silently be repeated across different cycles.

## Output

```text
output-demo/
  _definitions/
    parameterDefinition.json
    parameterDefinition.schema.json
    manifest.schema.json
  FictionalManufacturer-FictionalMachineType-FictionalMachineID/
    000001/
      manifest.json
      actual_set_parameters/
        set_000001.csv
        actual_000001.csv
      timeseries/
        timeseries_000001.csv
    000002/
      ...
```

Every CSV has canonical names in row 1, catalogue units in row 2 and data from row 3 onwards. Set/actual files contain one data row per cycle. Only parsed resources are inventoried in the manifest. No empty quality, metadata or raw files are added.
The three specification files are copied unchanged, so relative manifest references remain resolvable when the complete output root is moved or archived.

The manifest records the input filename and SHA-256, mapping snapshot, parser version and source line range under `manifestMetadata.csvToCyclePackage`. It does not copy the original dataset: retain that input to repeat the conversion. Review your own mapping and metadata before publishing output; they appear in the manifest.

If the script is moved outside this repository, use `--specification PATH` to point to the directory containing the catalogue and both schemas. The canonical files are the source of truth, not a duplicate list of parameters in this script.

Reference CSV outputs for the two-cycle example are supplied under [examples/expected](examples/expected). Manifest creation timestamps vary between runs; the CSV outputs do not.

## Recommended cycle selection

For already aligned and complete cycle blocks, the specification recommends explicitly selecting `first` for the setting effective at process start and `last` for the completed-cycle actual result. See [cycle-value selection](../../docs/cycle_value_selection.md), especially for semi-automatic operation and delayed/controller-buffered values. The converter retains its conservative `constant` default: event detection and source-update semantics remain the producer's responsibility.