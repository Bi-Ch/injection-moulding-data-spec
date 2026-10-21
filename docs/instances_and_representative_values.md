# Instances, profiles and representative values

An instance distinguishes repeated entities such as heating zones, cavities, devices or profile segments. Read the parameter's `instances` object before forming a header. All numeric dimensions start at `1`; the order and meaning of the dimensions come from `headerPattern` and `dimensions`.

## Forming an instance header

| Quantity | Valid example | Association to document |
| --- | --- | --- |
| Barrel-zone setpoint | `setTemperatureBarrel_1` | Physical interior heating zone. |
| Barrel-zone actual value | `actualTemperatureBarrel_1` | Same zone and the cycle-value selection method. |
| Hot-runner temperature | `actualTemperatureHotRunner_1` | Hot-runner zone. |
| Cavity temperature signal | `timeseriesTemperatureCavity_1_1` | Cavity 1 and sensor position 1 within it. |
| Device power consumption | `timeseriesPowerConsumption_TemperatureControlDevice_1` | Physical device 1 of that asset class and its metering boundary. |
| Cavity description | `descriptionMouldCavity_1` | Cavity corresponding to this description. |

For a controlled-code dimension, such as `providingAssetCode`, use the entry's `allowedValues`. A valid asset code in the vocabulary is not necessarily permitted for every parameter.

When `supported` is false, use the canonical name without adding indices. For instance-capable parameters, `unsuffixedValuePolicy` governs the bare name. `singleOrUnspecifiedInstance` permits one instance or an unspecified instance; it does not denote an average and does not prove that no profile or additional physical instance exists. `singleOnly` restricts use to a single instance, and `notAllowed` requires the declared suffix. In this catalogue, cavity descriptions and profile breakpoints require their indices.

## Heating zones and temperature-control devices

Barrel indices cover interior heating zones only. The flange and nozzle use separate scalar parameters:

| Location | Setting | Actual cycle value |
| --- | --- | --- |
| Interior zone 1 | `setTemperatureBarrel_1` | `actualTemperatureBarrel_1` |
| Barrel flange | `setTemperatureBarrelFlange` | `actualTemperatureBarrelFlange` |
| Nozzle | `setTemperatureNozzle` | `actualTemperatureNozzle` |

Record zone order and location; do not infer flange or nozzle from the first or last zone number. These actual temperatures are cycle values, while `timeseriesTemperatureCavity` retains a sampled trajectory.

Temperature-control-device indices identify devices, not mould sides. For example, `actualTemperatureHoseMouldInlet_1` and `_2` preserve separate device-associated supply temperatures. Document each device and circuit. Several independently observed circuits within one device require a documented extension to the current instance model.

## Holding-pressure profiles

Pair `setPressureHolding_<profileSegmentIndex>` with `setTimeHolding_<profileSegmentIndex>`. Equal indices identify one segment's pressure in bar and duration in seconds. Durations are not cumulative breakpoints. `setTimeHoldingCumulative` separately records the total set holding duration.

This column excerpt is taken from the [fictional settings file](../example/FictionalManufacturer-FictionalMachineType-FictionalMachineID/000001/actual_set_parameters/set_000001.csv):

```csv
setPressureHolding_1,setTimeHolding_1,setPressureHolding_2,setTimeHolding_2,setTimeHoldingCumulative
bar,s,bar,s,s
400.0,1.0,350.0,2.0,3.0
```

## Velocity profiles

Profile values and internal boundaries use separate canonical parameters in the settings file:

| Profile | Internal-breakpoint parameter | Boundary coordinate |
| --- | --- | --- |
| `setVelocityScrewInjection` | `setVelocityScrewInjectionProfileBreakpoint` | Screw position, mm. |
| `setVelocityScrewInjectionVolume` | `setVelocityScrewInjectionVolumeProfileBreakpoint` | Injection volume, ccm. |
| `setVelocityMouldOpen` | `setVelocityMouldOpenProfileBreakpoint` | Mould position, mm. |
| `setVelocityMouldClose` | `setVelocityMouldCloseProfileBreakpoint` | Mould position, mm. |

Use `profileSegmentIndex` for segment values and `profileBreakpointIndex` for boundaries. A complete profile with `N` segments has `N - 1` internal breakpoints. Breakpoint `i` separates segments `i` and `i + 1`. Indices are contiguous from `1`, and each breakpoint has an explicit suffix even when there is only one.

The last injection-velocity segment ends at the injection-to-holding switchover event. Its criterion can use a different quantity from the internal breakpoint coordinate; a time-based switchover does not become a volume breakpoint. No additional final internal breakpoint is stored. `setPressureInjection` is a scalar pressure-control setpoint and does not define a segmented profile.

## Representative values

Use only Representative parameters already defined in the catalogue. Their `representativeValue` metadata identifies the source parameter and required documentation: `representationMethod`, `sourceParameter` and `sourceInstances`. This metadata describes the relationship; it does not contain the observed result.

Document the selected instances, process interval, aggregation or weighting, and any normalisation in accompanying provenance. Retain the underlying values. For example, `actualTemperatureBarrelRepresentative` represents documented interior barrel zones and excludes flange and nozzle. Similar summary values can hide different zone distributions or profile shapes.

Dedicated parameters ending in `Representative` are Experimental because their derivation is application-specific. The Core field `measuredQualityCycleIsGood` has a separate role as an overall assessment of part-level quality; its [inspection criteria](quality_inspection_template.md) must still be documented.
