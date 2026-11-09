# Documenting inspection and assessment context

Quality observations need enough context to identify the inspected object and understand the method and assessment. Store this information in a document under the cycle's `metadata/` directory and inventory it as `supplementary`. A shared procedure may be described once in a stable, versioned document referenced by the cycle documentation.

The accompanying document supplies context for the six-column Quality-Long observations. Record the following information where available:

| Information | Content |
| --- | --- |
| Observation scope | Quality resource, cycle, parameter, instance and observation time where needed to identify repeated inspections. |
| Inspected object | Part, cavity or complete shot, and how it was associated with the production cycle. |
| Method | Inspection procedure and version, equipment, measurement location, conditioning and relevant time after production. |
| Measurement meaning | Recorded quantity, unit, reference basis and any locally defined intensity scale. |
| Acceptance criteria | Applied tolerance or decision rule and version; distinguish the observation from its acceptability. |
| Overall cycle assessment | Rule producing `measuredQualityCycleIsGood`, including combination of cavities and handling of missing inspections. |
| Reassessment | Changed rule and dataset version, with the relationship to the earlier assessment. |
| Known limits | Uninspected characteristics and unavailable measurement or assessment context. |

A missing inspection is neither a negative nor a positive defect observation. A recorded part mass is not automatically a good/bad classification. If no acceptance criterion was applied, state that directly; do not infer one from the presence of a numeric value.

This is a documentation convention, not a prescribed inspection method, tolerance or defect-intensity scale. See the [quality format](quality_long_draft.md) for the observation fields and Boolean polarities.
