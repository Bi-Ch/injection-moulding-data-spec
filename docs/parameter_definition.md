# Choosing and interpreting parameters

Version `1.0` of the [catalogue](../parameterDefinition.json) contains 220 parameter definitions: 134 Core, 39 Draft and 47 Experimental. Its `specification` object identifies the catalogue version, and its `parameters` array defines the available quantities. The definition describes what a value means; the observations themselves are stored in cycle packages.

Match source data by quantity, role, measurement basis, unit, representation and instance. A similar column name alone is insufficient. If the source meaning is unknown, retain the source data and the uncertainty instead of assigning a more specific meaning.

## Names, roles and representations

Use the exact, case-sensitive `variableName` or a concrete header generated from its declared instance pattern. Descriptions and `semanticAliases` help readers find a quantity; they are not alternative output headers. `canonicalId` identifies the definition within this catalogue and is not a separately resolving persistent URL.

| `valueRole` | Meaning |
| --- | --- |
| `set` | Configured setting or target. |
| `actual` | Machine or process observation. |
| `measured` | Additional measured or inspected value, including quality. |
| `nominal` | Nominal property or reference value. |
| `description` | Textual description. |
| `timestamp` | Time coordinate. |

`dataRepresentation` is a separate distinction: `cycleValue` describes a cycle-related value; `timeSeries` describes sampled values. For example, `timeseriesPressureInjection` is a trajectory, while `actualPressureInjectionMaximum` is the machine-reported maximum during injection. Taking the last sample of the trajectory does not calculate that maximum.

Follow the [resource layout](data_structure.md) when storing values. A setting, a reported cycle result and a sampled signal keep their different roles even if they use the same unit.

## Fields needed to interpret a value

| Field | What to check |
| --- | --- |
| `descriptionEnglish`, `descriptionGerman` | Quantity, phase, reference basis and any stated limitations. |
| `dataType` | Logical type: `float`, `int`, `boolean`, `string` or `object`. |
| `allowedValues` | Canonical spellings of the permitted parameter values, where declared. |
| `allowedValuesCaseSensitive` | Whether matching against `allowedValues` distinguishes case; defaults to `true` when absent. |
| `unit`, `unitSemantics` | Target unit or the reason no unit is assigned. |
| `releaseProfile`, `curation` | Maturity and unresolved interpretation or review issues. |
| `assetAssignment` | Possible providing assets and affected assets. |
| `measurementLocation` | Declared location or explicit lack of location information. |
| `instances` | Whether repeated entities are supported and how their headers are formed. |
| `profileSegments` | Links between profile values, durations, internal breakpoints or segment end positions, force limits and interpolation settings. Explicit metadata may declare a ramp's starting value or an omitted final endpoint. |
| `representativeValue` | Whether the parameter represents other observations and what derivation documentation is required. |
| `alternativeRepresentationOf`, `derivableFrom` | Related representations and inputs needed for a derivation. |
| `standardReferences` | Qualified relations to external standard terms. |

`float` means a finite number, not a guaranteed storage width or measurement precision. `int` has no fractional part. Retain native Boolean and numeric types in JSON. The supported wide-CSV examples do not define an encoding for object-valued parameters.

For example, the four profile-interpolation settings declare `Steps` and `Ramps` in `allowedValues` and set `allowedValuesCaseSensitive` to `false`. They also accept `steps`, `ramps`, uppercase and mixed-case spellings. This applies to parameter values; parameter names, headers and controlled asset codes remain case-sensitive. A missing setting does not choose either value. Their [profile-specific meanings](instances_and_representative_values.md#profile-interpolation) distinguish holding-pressure targets at segment ends from velocity ramps between successive segment values.

Ejector profiles instead declare fixed `Steps` behaviour. Their endpoint coordinates and force limits align with the velocity segment index; only an omitted final backward endpoint has the explicit default of 0 mm. This exception does not turn other missing values into zero. See the [ejector profile rules](instances_and_representative_values.md#ejector-profiles).

Asset codes such as `InjectionMoldingMachine` and `TemperatureControlDevice` identify classes. They do not identify a particular physical machine, device or sensor. Record those associations in dataset context. The [asset vocabulary](assetVocabulary.json) defines the available codes; each controlled instance dimension may permit only a subset.

## Units and missing information

For a defined unit, copy `unit.displayName` exactly into the CSV unit cell, for example `bar`, `°C` or `ccm`. The `unEceRec20` and `iecTs62720` codes identify units for machine processing. They do not convert source values.

When `unit` is null, the catalogue supplies one of these `unitSemantics` values:

| Token | Meaning |
| --- | --- |
| `dimensionless` | A quantity without a physical unit, such as a count. |
| `notApplicable` | A unit does not apply, for example to a Boolean observation. |
| `unknown` | The unit or assessment scale is unresolved. |

Use that token in the unit cell. These states describe the definition, not whether an observation is missing. An unknown unit is not dimensionless. Convert differing source units explicitly and document the conversion before writing canonical values.

The documented unit-code editions are UNECE Recommendation 20, Revision 17 (2021), and DIN IEC/TS 62720 / DIN SPEC 42720:2018-04, adopting IEC/TS 62720:2017. DIN EN 61360-1:2018-07 supplies property-definition principles rather than another unit-code list.

## Definition maturity

| `releaseProfile` | Interpretation |
| --- | --- |
| `core` | Definitions within the authors' practical expertise and stated scope. |
| `draft` | Definitions requiring specialist review of their measurement basis, signal meaning or context. |
| `experimental` | Definitions requiring application-specific methods, including numeric defect intensities and dedicated Representative values. |

All profiles use the same file rules. Core status does not certify the measurement, and a past `curation.reviewStatus` does not override the release profile. Read the entry's limitations before using a Draft or Experimental parameter. The Core cycle-quality field remains an application-specific assessment with documented criteria.

## Standards references

Each structured reference records `sourceStandard`, `release`, `term`, `relation` and `explanation`; `aliasStandards` retains corresponding designations. Read the explanation with the relation:

| Relation | Meaning |
| --- | --- |
| `exactMatch` | The reviewed concepts are equivalent. |
| `closeMatch` | A strong candidate correspondence with remaining contextual qualifications. |
| `related` | A relevant concept that is not interchangeable. |
| `broaderTerm` | The referenced standard term is broader than the local parameter. |
| `narrowerTerm` | The referenced standard term is narrower than the local parameter. |

These references are informative. They do not establish interface conformance or supply machine-specific NodeIds. The separate [dataset correspondence register](dataset_parameter_mappings.md) describes source fields using `closeMatch` and `related`. Its relation vocabulary is separate from the standards-reference relations above.

## Extensions and versioning

Retain the catalogue version used by each dataset. Published keys and identifiers remain stable; changed meanings require a documented version transition. The schema supports `legacyAliases`, `deprecated` and `replacedBy` for version migrations; catalogue version `1.0` does not use them. Renaming cannot resolve a changed physical meaning or representation.

For an additional quantity, provide an explicit definition in a versioned extended catalogue and point the manifest to it. Keep unrelated source columns as supplementary data until their meaning is established. Describe required reader support; an application supporting only the published catalogue may not understand extensions. Multiple injection units and multi-component moulding are outside the scope of version `1.0`.
