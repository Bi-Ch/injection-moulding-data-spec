# Instances, profiles and representative values

An instance distinguishes repeated entities such as heating zones, cavities, devices or profile segments. Read the parameter's `instances` object before forming a header. All numeric dimensions start at `1`; the order and meaning of the dimensions come from `headerPattern` and `dimensions`.

## Forming an instance header

| Quantity | Valid example | Association to document |
| --- | --- | --- |
| Barrel-zone 1 setpoint | `setTemperatureBarrel_1` | Physical interior heating zone. |
| Barrel-zone 1 actual value | `actualTemperatureBarrel_1` | Same zone and the cycle-value selection method. |
| Hot-runner zone 1 temperature | `actualTemperatureHotRunner_1` | Hot-runner zone. |
| Cavity temperature signal | `timeseriesTemperatureCavity_1_1` | Cavity 1 and sensor position 1. |
| Cavity description | `descriptionMouldCavity_1` | Cavity 1 corresponding to this description. |

For a controlled-code dimension, such as `providingAssetCode`, use the entry's `allowedValues`. A valid asset code in the vocabulary is not necessarily permitted for every parameter.

When `supported` is false, use the canonical name without adding indices. For instance-capable parameters, `unsuffixedValuePolicy` governs the bare name. `singleOrUnspecifiedInstance` permits one instance or an unspecified instance; it does not denote an average and does not prove that no profile or additional physical instance exists. `singleOnly` restricts use to a single instance, and `notAllowed` requires the declared suffix. In this catalogue, cavity descriptions and profile breakpoints require their indices.

As an example, `setPressureHolding` alsows permits `singleOrUnspecifiedInstance`, therefore it allows a single entry for a constant holding pressure using either `setPressureHolding` or only `setPressureHolding_1`. However, it also allows instances to describe a profile using multiple settings, such as `setPressureHolding_1` and `setPressureHolding_2`.

## Heating zones and temperature-control devices

Barrel indices cover interior heating zones only. The flange and nozzle use separate scalar parameters:

| Location | Setting | Actual cycle value |
| --- | --- | --- |
| Interior zone 1 | `setTemperatureBarrel_1` | `actualTemperatureBarrel_1` |
| Barrel flange | `setTemperatureBarrelFlange` | `actualTemperatureBarrelFlange` |
| Nozzle | `setTemperatureNozzle` | `actualTemperatureNozzle` |

Record zone order and location; do not infer flange or nozzle from the first or last zone number. These actual temperatures are cycle values, while `timeseriesTemperatureCavity` retains a sampled trajectory.

Temperature-control-device indices identify devices, not mould sides. For example, `actualTemperatureHoseMouldInlet_1` and `_2` preserve separate device-associated supply temperatures. Document each device and circuit. Several independently observed circuits within one device require a documented extension to the current instance model.

`setTemperatureTemperatureControlDevice_<temperatureControlDeviceIndex>` records the device's temperature setpoint. The corresponding observed supply-line temperature towards the mould is `actualTemperatureHoseMouldInlet_<temperatureControlDeviceIndex>`; document the cycle-value sampling or aggregation method.

## Profile interpolation

Holding-pressure, injection-velocity and mould-velocity profiles can declare one scalar interpolation setting for the complete profile:

| Profile | Interpolation parameter |
| --- | --- |
| Holding pressure | `setPressureHoldingProfileInterpolation` |
| Axial or volumetric injection velocity | `setVelocityScrewInjectionProfileInterpolation` |
| Mould opening velocity | `setVelocityMouldOpenProfileInterpolation` |
| Mould closing velocity | `setVelocityMouldCloseProfileInterpolation` |

These parameters are cycle-level string settings with two modes, canonically spelled `Steps` and `Ramps`. Their `allowedValuesCaseSensitive: false` metadata permits any capitalization, including `steps`, `ramps`, `STEPS` and mixed case. Use the exact unsuffixed parameter name and `notApplicable` in the CSV unit cell. The injection-velocity setting is shared by the axial and volumetric representations; when both are present, it applies to both.

An absent or missing interpolation setting means that interpolation is unknown. There is no default to `Steps`, and existing datasets without a selector remain valid. A recorded selector describes intended set-profile behaviour; it does not establish that the measured trajectory followed it. The `profileSegments.interpolationParameterRef` metadata identifies the applicable selector. The meaning of `Ramps` differs between holding pressure and velocity, as described below.

## Holding-pressure profiles

Pair `setPressureHolding_<profileSegmentIndex>` with `setTimeHolding_<profileSegmentIndex>`. Equal indices identify one segment's pressure in bar and duration in seconds. Durations are not cumulative breakpoints. `setTimeHoldingCumulative` separately records the total set holding duration.

This column excerpt is taken from the [fictional settings file](../example/FictionalManufacturer-FictionalMachineType-FictionalMachineID/000001/actual_set_parameters/set_000001.csv):

```csv
setPressureHolding_1,setTimeHolding_1,setPressureHolding_2,setTimeHolding_2,setTimeHoldingCumulative
bar,s,bar,s,s
400.0,1.0,350.0,2.0,3.0
```

This excerpt contains no interpolation selector, so its interpolation remains unspecified.

With `setPressureHoldingProfileInterpolation = Steps`, pressure value `setPressureHolding_i` is held throughout segment `i`. With `Ramps`, the first segment starts at `setPressureInjectionLimit` and reaches `setPressureHolding_1` at the end of its `setTimeHolding_1` duration. Each subsequent segment starts at the preceding target and reaches its own target `setPressureHolding_i` at the end of its duration. Interpolation is linear in elapsed time within each segment. The profile ends at the final target; targets can increase or decrease and need not form a monotonically decreasing sequence. The starting-pressure dependency is declared by `profileSegments.rampStartValueParameterRef`; retain `setPressureInjectionLimit` when recording holding-pressure `Ramps`.

For example, with an injection-pressure limit of 1000 bar, targets of 400 and 350 bar, and segment durations of 1 and 2 s, `Ramps` means 1000 to 400 bar during the first second, then 400 to 350 bar during the following two seconds. With the same targets and durations, `Steps` means 400 bar for the first second and 350 bar for the next two seconds. In both cases the total duration is 3 s; `setTimeHolding_2 = 2 s` remains a segment duration, not a breakpoint measured from the start of holding.

## Injection and mould velocity profiles

Profile values and internal boundaries use separate canonical parameters in the settings file:

| Profile | Internal-breakpoint parameter | Boundary coordinate |
| --- | --- | --- |
| `setVelocityScrewInjection` | `setVelocityScrewInjectionProfileBreakpoint` | Screw position relative to the mechanical zero point, mm. |
| `setVelocityScrewInjectionVolume` | `setVelocityScrewInjectionVolumeProfileBreakpoint` | Volumetric screw position relative to the mechanical zero point, ccm. |
| `setVelocityMouldOpen` | `setVelocityMouldOpenProfileBreakpoint` | Mould position relative to first contact, mm. |
| `setVelocityMouldClose` | `setVelocityMouldCloseProfileBreakpoint` | Mould position relative to first contact, mm. |

Screw-position breakpoints use the same reference as `timeseriesPositionScrew` and `timeseriesPositionScrewVolume`: the mechanically foremost screw position is zero, and values increase as the screw moves backward. Record the screw position or its corresponding volume at the segment transition, not the travel or displaced volume since injection started. Negative screw-position breakpoint values are not permitted. 
Mould-position breakpoints use the first-contact position defined as zero in `timeseriesPositionMould`, not the travel since the opening or closing profile started.

Use `profileSegmentIndex` for segment values and `profileBreakpointIndex` for boundaries. A complete profile with `N` segments has `N - 1` internal breakpoints. Breakpoint `i` separates segments `i` and `i + 1`. Indices are contiguous from `1`, and each breakpoint has an explicit suffix even when there is only one.

With `Steps`, velocity value `setVelocityScrewInjection_i` is held throughout segment `i`. With `Ramps`, the profile starts at `setVelocityScrewInjection_1`; segment `i` changes linearly from `setVelocityScrewInjection_i` to `setVelocityScrewInjection_(i+1)` over its position or volume interval. The last segment holds the last velocity value. Interpolation follows the profile's boundary coordinate, not elapsed time. Document the starting position or volumetric position as well as the internal breakpoints to reconstruct the first ramp. With one segment, the single velocity value is held for the whole profile in either mode.

For example, consider a volumetric injection-velocity profile starting at a volumetric screw position of 20 ccm, with an internal breakpoint at 10 ccm and velocities of 40 and 25 ccm/s. `Ramps` changes the first segment from 40 to 25 ccm/s as the screw-position coordinate decreases from 20 to 10 ccm; the final segment holds 25 ccm/s until switchover. `Steps` holds 40 ccm/s until 10 ccm, then 25 ccm/s until switchover.

The last injection-velocity segment ends at the injection-to-holding switchover event. Its criterion can use a different quantity from the internal breakpoint coordinate; a time-based switchover does not become a volume breakpoint. No additional final internal breakpoint is stored.

## Ejector profiles

Forward and backward movement each have their own step profile:

| Direction | Segment velocity, mm/s | Segment end position, mm | Segment force limit, kN |
| --- | --- | --- | --- |
| Forward | `setVelocityEjectorForward` | `setPositionEjectorForward` | `setForceEjectorForward` |
| Backward | `setVelocityEjectorBackward` | `setPositionEjectorBackward` | `setForceEjectorBackward` |

Use the same one-based `profileSegmentIndex` for the velocity, end position and force limit of a segment. The first segment begins at its configured velocity; each segment holds that velocity until its end position, where the following segment begins. `profileSegments.fixedInterpolation` is `Steps`. The end positions include the final movement endpoint, so they use segment indices rather than a separate internal-breakpoint index.

A forward profile with `N` segments requires `N` end positions, including at least one position for a single segment. A backward profile requires its first `N - 1` end positions; the final one may be omitted and then means `0 mm`. For example, `setVelocityEjectorBackward_1` alone describes one constant-velocity return to zero. An explicitly supplied final position takes precedence over this default. The default concerns an omitted endpoint, not an empty recorded position value, and does not require writing a fabricated position column.

Both directions use the same calibrated retracted zero as `timeseriesPositionEjector`. Positions increase in the ejection direction and are coordinates, not travel from the profile start. Negative positions retain their meaning as positions behind the calibrated zero. In each velocity parameter, positive means motion in its named direction and negative means counter-motion. Thus the generic actual velocity `timeseriesVelocityEjector`, whose positive direction is forward, must be negated when compared with the backward set velocity; do not take an absolute value.

Each segment can carry its own nonnegative force limit. Equal indices associate that limit with the velocity and endpoint. A force limit is a limiting threshold, not a force-control target or an actual force. If limits are unavailable, leave them unspecified; `0 kN` is an explicit value and must not represent missing information. When exporting a force-limit block for a profile, use corresponding indices for all its segments; individual unknown values may remain empty.

For example, a forward profile can use segment 1 at 20 mm/s until 15 mm with a 2 kN limit, then segment 2 at 10 mm/s until 25 mm with a 1 kN limit. A one-segment return at 30 mm/s may omit its end-position setting and end at 0 mm. These conceptual examples illustrate the ejector-profile rules.

The catalogue links these settings through `segmentEndPositionParameterRef` and `segmentForceLimitParameterRef`. Only the backward profile declares `defaultLastSegmentEndPosition: 0`. The generic OPC 40083 references are `related` anchors and do not establish a standardized ejector-profile representation.

## Representative values

`Representative` parameters have been introduced to enable comparable processes to be clustered. They are used solely to compare or label processes without interfering with measurements or introducing false results.
Their `representativeValue` metadata identifies the source parameter and required documentation: `representationMethod`, `sourceParameter` and `sourceInstances`. This metadata describes the relationship; it does not contain the observed result.

Document the selected instances, process interval, aggregation or weighting, and any normalisation in accompanying provenance. Retain the underlying values. For example, the `actualTemperatureBarrelRepresentative` parameter represents the documented interior barrel zones independently of the machine-specific number of zones, and it may offer the clustering of comparable processes.

Dedicated parameters ending in `Representative` are Experimental because their derivation is application-specific. The field `measuredQualityCycleIsGood` has a separate role as an overall assessment of part-level quality; its [inspection criteria](quality_inspection_template.md) must still be documented.
