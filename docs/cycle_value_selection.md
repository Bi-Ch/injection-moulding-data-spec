# Selecting values and assigning cycles

Cycle-value selection determines which source observation represents a cycle. Establish the parameter's meaning and the source's update behaviour before applying a first- or last-value rule.

## Settings and actual values

| Resource | Recommended selection | Interpretation |
| --- | --- | --- |
| `setParameters` | First setting effective at process start. | Settings used for the cycle being stored. |
| `actualParameters` | Last result attributable to the completed cycle. | Final reported value after the relevant source updates. |

In semi-automatic operation, identify process start rather than the beginning of a preceding waiting period. A controller may apply changed settings to the current or a later cycle; record which behaviour applies. Preserve changes within a cycle through supplementary source histories or a documented extension when they matter to the application.

Receiving a value during a cycle does not prove it belongs to that cycle. Account for delayed updates, buffering and partial exports. If the final result is missing or its assignment is uncertain, retain that uncertainty instead of silently substituting another observation.

The selection rule does not change the quantity. Selecting the last value from a running cycle-maximum field can retain its final maximum; selecting the last instantaneous pressure sample does not calculate a maximum. A barrel temperature stored as `cycleValue` is a documented value for one cycle, not an average over several cycles. Retain the source's sampling or aggregation method.

## Time series

Keep sampled trajectories in the time-series resource with `relativeTimestampCycle` in milliseconds. Zero denotes the documented cycle start. If recording begins later, retain the positive offset rather than redefining the first sample as the cycle start.

Document the time origin, source sampling configuration and any alignment, interpolation or resampling. Preserve observed sample times. `actualTimestepSizeIMM` supplies a nominal interval and does not establish actual regularity or synchronisation. A non-integer interval alone does not establish irregular sampling either.

## Cycle identity

`actualCountCycleMachine` is the absolute, non-resettable count of completed machine cycles. `actualCountCycleArticle` is the separate resettable article/job counter. A counter alone is not unique across machines.

`cycleId` is the package's string identifier; it need not be derived from a machine counter. Document its relationship to source identifiers and the machine. Handle controller replacement, counter discontinuities and separate acquisition runs explicitly so that identifiers are not silently reused.

## Record the selection

Include the cycle boundary, operating mode, relevant source-update behaviour, selected observations and known gaps in dataset documentation or a supplementary resource. Preserve acquired histories in `raw/` when available. The current file structure does not infer a missing cycle boundary or reconstruct omitted observations.

The [CSV converter](../tools/csv_to_cycle_package/README.md) accepts already aligned cycle blocks. Its default `constant` selection checks that values agree within a block; explicit `first` and `last` select the literal first or last cell, including an empty one. It does not detect process events, controller delays or incomplete cycles. Prepare and check those associations before conversion.
