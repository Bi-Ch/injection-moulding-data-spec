# Complete fictional cycle example

This folder is a structural example only. Manufacturer, machine, dataset, cycle, timestamps and all values are invented and they do not relate to each other; none are measurements or product claims.
The example deliberately contains only a small selection of canonical parameters with the intention of showing every defined cycle-resource role:

- `manifest.json` identifies the cycle package and lists every resource by relative path and role.
- `README.md` is itself inventoried as the `supplementary` resource that explains the package.
- `metadata/measured_000001.csv` contains non-quality measured cycle values.
- `metadata/measured_qualities_000001.csv` demonstrates the typed Quality-Long layout and is inventoried with role `measuredQualities`.
- `actual_set_parameters/set_000001.csv` contains set values, a two-segment volumetric injection-velocity profile with one internal volumetric screw-position breakpoint and a time-based switchover criterion, per-segment holding durations, the cumulative total holding duration, and separate set temperatures for an interior barrel zone, the barrel flange and the nozzle.
- `actual_set_parameters/actual_000001.csv` contains optional once-per-cycle actual values, including separate temperatures for an indexed interior barrel zone, the barrel flange and the nozzle.
- `timeseries/timeseries_000001.csv` contains a short time series with `timeseriesRevolutionsScrew` and the corresponding derived `timeseriesVelocityScrewPeripheral`. With the manifest's invented `nominalDiameterScrew` of 40 mm, the peripheral values use `v = pi * d * n / 60` and are rounded to six decimal places.

The internal breakpoint value of 10.0 ccm refers to the volumetric screw position at the segment transition. The mechanically foremost screw position defines 0 ccm; the value does not describe the volume displaced since injection started.

Wide CSV files use canonical headers in row 1 and one unit or unit-semantics cell per column in row 2. The heterogeneous Quality-Long file is the documented exception: its unit is stored per observation and it has no unit row. Replace or extend the invented data rows as needed; validate every added header, type, unit, instance suffix and manifest path against the repository definitions.
