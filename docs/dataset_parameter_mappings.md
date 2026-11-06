# Using published dataset correspondences

The optional [correspondence register](../mappings/datasetParameterMappings.json) connects catalogue parameters to names in published datasets. It can guide a source-specific conversion, but it is not an executable mapping and is not consumed by the example CSV converter.

Version `1.0` of the register contains 12 sources, 100 canonical parameter groups and 520 assignments. A group represents one distinct catalogue `variableName`; an assignment is one `publishedNamings` entry within a group. The source datasets themselves are not included in this repository.

| Relation | Assignments |
| --- | ---: |
| `closeMatch` | 368 |
| `related` | 152 |
| **Total** | **520** |

The mapped groups and their assignments cover these catalogue maturity profiles:

| Catalogue profile | Parameter groups | Assignments |
| --- | ---: | ---: |
| Core | 71 | 434 |
| Draft | 24 | 52 |
| Experimental | 5 | 34 |
| **Total** | **100** | **520** |

Pressure-controlled injection is outside the intended current catalogue scope. Correspondences for this control mode are excluded from the active register; they are not assigned to an injection-pressure limit or holding-pressure parameter.

## Read an assignment

Select the catalogue `variableName` in `mappings`, then read its `publishedNamings` entries. Each entry identifies:

| Fields | Interpretation |
| --- | --- |
| `sourceId` | Resolves to a source in `sources`, including available version and citation information. |
| `publishedId`, `publishedLabel` | Exact source identifier and available descriptive label. Case, punctuation and meaningful whitespace matter. |
| `publishedUnit`, `publishedDtype` | Reported source metadata; null does not supply a target unit or inferred datatype. |
| `canonicalInstanceHeader` | Concrete target instance where established; otherwise null. |
| `sourceFiles` | Paths relative to the original dataset, identifying data or supporting name definitions. |
| `relation`, `note` | Correspondence strength, interpretation and unresolved differences. |
| `curation` | Author review, source-author confirmation and conversion-validation status. |

Read the exact source version and file before applying an assignment. A listed file may be a dictionary or description rather than data ready for import. The target unit, role and representation come from the referenced parameter catalogue.

## Interpret the relation

| Relation | Meaning |
| --- | --- |
| `closeMatch` | The public source evidence establishes a close match for the parameter concept. Source-specific phase, aggregation, sensor position or instance semantics may still differ. This is a source-name mapping and does not assert conformance with an external standard. |
| `related` | The source field is relevant to the canonical parameter but differs in role, aggregation, scope, unit or specificity and is not directly interchangeable. |

The retained curation records identify reviews by the specification author and record `sourceAuthorConfirmation: "notObtained"` and `conversionValidation: "notPerformed"`. Review status and relation are separate: review can retain an unresolved question. The `reviewDate` fields identify the recorded source reviews: 391 assignments are dated 2026-08-18 and 129 are dated 2026-10-09.

The twelve `MldHt20mA101TmpAct` through `MldHt20mA112TmpAct` fields in `proBayesDataset2023` are listed under `actualTemperatureHoseMouldInlet`, with `relation: "related"` and no assigned `canonicalInstanceHeader`. Their source labels identify temperature-control devices, but do not establish the supply-line measurement location, cycle-value selection or canonical device instance. Establish these before converting them to this parameter.

For example, `MET_JobCycleID` in source `proBayesDataset2022V2` is assigned to `actualCountCycleArticle` with `closeMatch`. The entry explains that the job counter restarts for each experiment day. Preserve that scope; it is not a lifetime machine counter.

## Prepare a conversion

1. Confirm the actual source column and version, including whether values are physical, normalised or simulated.
2. Check quantity, unit, measurement basis, time representation, aggregation and instances against the target definition.
3. Implement required unit conversions, time alignment, cycle assignment and label interpretation explicitly. Preserve source-to-target provenance.
4. Validate the resulting package and compare its values with the source. Keep this conversion check separate from the register's conceptual relation.

For prepared, aligned CSV input, use an application-specific configuration for the [converter](../tools/csv_to_cycle_package/README.md). Its configuration has a different structure from this register.

The [mapping schema](../mappings/datasetParameterMappings.schema.json) checks record structure. Cross-file checks must also resolve source IDs, catalogue names and instance headers, and identify duplicate assignments. Retrieval and screening records are available in [research/](../research/); they describe the evidence search rather than a validation of every dataset value.
