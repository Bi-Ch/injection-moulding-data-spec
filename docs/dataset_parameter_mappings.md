# Using published dataset correspondences

The optional [correspondence register](../mappings/datasetParameterMappings.json) connects catalogue parameters to names in published datasets. It can guide a source-specific conversion, but it is not an executable mapping and is not consumed by the example CSV converter.

The current register contains 12 sources, 102 canonical parameter groups and 529 assignments. The source datasets themselves are not included in this repository.

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
| `exactMatch` | Reviewed source evidence supports the same concept and a compatible unit. |
| `closeMatch` | Strong correspondence with remaining questions about phase, aggregation, location or instances. |
| `related` | Relevant quantity with a different role, representation, scope or scale; direct substitution is not justified. |
| `needsCuration` | Plausible target with unresolved ambiguity or missing evidence. |

All current assignments have been reviewed by the specification author. The register records `sourceAuthorConfirmation: "notObtained"` and `conversionValidation: "notPerformed"`. Review status and relation are separate: review can retain an unresolved question.

For example, `MET_JobCycleID` in source `proBayesDataset2022V2` is assigned to `actualCountCycleArticle` with `exactMatch`. The entry explains that the job counter restarts for each experiment day. Preserve that scope; it is not a lifetime machine counter.

## Prepare a conversion

1. Confirm the actual source column and version, including whether values are physical, normalised or simulated.
2. Check quantity, unit, measurement basis, time representation, aggregation and instances against the target definition.
3. Implement required unit conversions, time alignment, cycle assignment and label interpretation explicitly. Preserve source-to-target provenance.
4. Validate the resulting package and compare its values with the source. Keep this conversion check separate from the register's conceptual relation.

For prepared, aligned CSV input, use an application-specific configuration for the [converter](../tools/csv_to_cycle_package/README.md). Its configuration has a different structure from this register.

The [mapping schema](../mappings/datasetParameterMappings.schema.json) checks record structure. Cross-file checks must also resolve source IDs, catalogue names and instance headers, and identify duplicate assignments. Retrieval and screening records are available in [research/](../research/); they describe the evidence search rather than a validation of every dataset value.
