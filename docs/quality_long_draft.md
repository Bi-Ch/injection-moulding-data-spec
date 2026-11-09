# Recording quality observations

Quality-Long records detailed quality observations in a six-column layout. Version `1.0` defines the fields and rules below and provides example observations; it does not include a standalone machine-readable schema for this format. Store the file under `metadata/measured_qualities_<cycleId>.csv` and inventory it with resource role `measuredQualities`.

## One observation per row

It is recommended to use these columns in this order:

```csv
qualityParameter,instanceHeader,observedAt,booleanValue,numericValue,unit
```

| Column | Content |
| --- | --- |
| `qualityParameter` | Exact, unsuffixed catalogue name of the quality parameter. |
| `instanceHeader` | Concrete header for the observed instance; equal to `qualityParameter` for a non-instanced parameter. |
| `observedAt` | ISO 8601 observation time, distinct from cycle start and file creation. |
| `booleanValue` | `true` or `false` for a Boolean observation; otherwise empty. |
| `numericValue` | Value for a numeric observation, with a decimal point; otherwise empty. |
| `unit` | Catalogue display unit or its unit-semantics token for this observation. |

Exactly one value column is populated, and it must agree with the parameter's logical type. There is no separate unit row. Do not add empty observation rows to represent missing measurements.

## Instances and repeated inspections

Resolve `instanceHeader` through the definition's instance pattern. For example, `measuredQualityWeightPart_1` refers to the part associated with cavity 1. Keep the cavity-to-part and part-to-cycle relationship in the inspection context.

A single legacy observation may omit `observedAt` only when its cycle association is unambiguous. For new observations, retain a known measurement time. If the same parameter-instance pair occurs more than once, every repeated row requires a non-empty, distinguishing timestamp. Row order is not an observation identifier, and the format has no `sampleIndex` column.

## Existing example

The [fictional quality file](../example/FictionalManufacturer-FictionalMachineType-FictionalMachineID/000001/metadata/measured_qualities_000001.csv) contains:

```csv
qualityParameter,instanceHeader,observedAt,booleanValue,numericValue,unit
measuredQualityWarpageIsPresent,measuredQualityWarpageIsPresent_1,2026-01-01T12:00:14Z,false,,notApplicable
measuredQualityWeightPart,measuredQualityWeightPart_1,2026-01-01T12:00:15Z,,12.5,g
```

Both rows concern cavity 1. The first records that no warpage was observed under the fictional example's unspecified inspection criteria; the second records an invented part mass of 12.5 g. These rows illustrate the layout rather than a validated inspection procedure.

`measuredQualityWeightPart` describes a part mass. `measuredQualityWeightShot` describes the total mass of all moulded parts and the sprue/runner material of one shot. Keep these objects distinct.

## Observations and assessments

For an `IsPresent` parameter, `true` means the defect was observed. The catalogue's Boolean defect-presence definitions are Core, but the inspection method and decision criteria remain application-specific.

The overall assessment `measuredQualityCycleIsGood` belongs in the manifest, not in Quality-Long. Its polarity is different: `true` means good, `false` means bad, and `null` means no assessment is available. Document how observations from multiple cavities and missing inspections affect the cycle label.

Numeric defect-intensity definitions remain Experimental and carry `unitSemantics: "unknown"`. State the local scale, method and interpretation before using them. The parameter name alone does not make intensities comparable across applications.

Keep the [inspection and assessment context](quality_inspection_template.md) alongside the observations. Retaining measured characteristics allows a later application to apply different acceptance criteria; it cannot recover unmeasured characteristics. Version a revised assessment and preserve its relationship to the previous dataset and criteria.
