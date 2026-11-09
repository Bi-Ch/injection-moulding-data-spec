import argparse
import csv
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import io
import json
import math
from pathlib import Path
import re
import tempfile

# Basic CSV-to-cycle-package example. Python 3.10+, standard library only.
# Source columns are mapped explicitly; no machine interface or proprietary mapping is included.

VERSION = "1.0"
SPECIFICATION = Path(__file__).resolve().parents[2]
ROLES = {"set": "setParameters", "actual": "actualParameters", "timeseries": "timeSeries"}
CONTEXT = {"actualCountCycleMachine", "actualTimestepSizeIMM", "actualTimeCycleStart",
           "measuredTimeCreationFile", "measuredQualityCycleIsGood"}
STRUCTURAL = {"$schema", "manifestVersion", "parameterDefinition", "cycleId", "resources"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"),
                      object_pairs_hook=unique_object)


def keys(value, allowed, where):
    require(isinstance(value, dict), f"{where} must be an object")
    require(not set(value) - set(allowed), f"Unknown keys in {where}: {set(value) - set(allowed)}")


def safe_name(value):
    require(isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", value),
            f"Unsafe folder/cycle name: {value!r}; use 1-80 letters, digits, hyphens or underscores")
    require(not re.fullmatch(r"(?i:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])", value),
            f"Reserved folder/cycle name: {value}")
    return value


class Catalogue:
    def __init__(self, document):
        self.definitions = {p["variableName"]: p for p in document["parameters"]}
        require(len(self.definitions) == len(document["parameters"]), "Duplicate catalogue variableName")
        self.patterns = []
        for definition in self.definitions.values():
            instances = definition["instances"]
            if not instances["supported"]:
                continue
            pattern = re.escape(instances["headerPattern"])
            for dimension in instances["dimensions"]:
                values = dimension.get("allowedValues")
                expression = "|".join(re.escape(v) for v in values) if values else "[1-9][0-9]*"
                pattern = pattern.replace(re.escape("<" + dimension["key"] + ">"),
                                          "(?:" + expression + ")")
            self.patterns.append((re.compile(pattern), definition))

    def resolve(self, header, *, allow_cycle_quality_label=False):
        definition = self.definitions.get(header)
        if definition:
            policy = definition["instances"].get("unsuffixedValuePolicy")
            require(policy != "notAllowed", f"{header} requires explicit instance indices")
        else:
            matches = [d for pattern, d in self.patterns if pattern.fullmatch(header)]
            require(len(matches) == 1, f"Unknown or ambiguous canonical header: {header}")
            definition = matches[0]
        require(definition.get("definitionStatus") != "deprecated" and not definition.get("deprecated"),
                f"Deprecated parameter: {header}")
        supplied_cycle_label = allow_cycle_quality_label and header == "measuredQualityCycleIsGood"
        require(not definition["representativeValue"]["isRepresentative"] or supplied_cycle_label,
                f"Representative derivations are outside this small parser's scope: {header}")
        return definition


def unit_cell(definition):
    return definition["unit"]["displayName"] if definition["unit"] else definition["unitSemantics"]


def comparison_value(value, definition):
    """Compare case-insensitive enum values without changing their stored spelling."""
    if isinstance(value, str) and definition.get("allowedValuesCaseSensitive", True) is False:
        return value.casefold()
    return value


def typed(value, definition, where):
    """Blank CSV cells and JSON null stay missing; never turn them into zero."""
    if value is None or value == "":
        return None
    kind = definition["dataType"]
    if kind in {"int", "float"}:
        require(not isinstance(value, bool), f"{where}: Boolean is not a number")
        try:
            number = Decimal(str(value))
            require(number.is_finite(), f"{where}: number must be finite")
            if kind == "int":
                require(number == number.to_integral_value(), f"{where}: expected an integer")
                return int(number)
            result = float(number)
            require(math.isfinite(result), f"{where}: number outside floating-point range")
            return result
        except InvalidOperation as error:
            raise ValueError(f"{where}: expected a number, got {value!r}") from error
    if kind == "boolean":
        if isinstance(value, bool):
            return value
        require(isinstance(value, str) and value.lower() in {"true", "false"},
                f"{where}: use true or false")
        return value.lower() == "true"
    require(kind == "string" and isinstance(value, str), f"{where}: unsupported or invalid type {kind}")
    if "allowedValues" in definition:
        require(comparison_value(value, definition) in
                [comparison_value(allowed, definition) for allowed in definition["allowedValues"]],
                f"{where}: value must be one of {definition['allowedValues']}")
    return value


def prepare_mapping(mapping, catalogue, cycle_id):
    keys(mapping, {"cycle_column", "delimiter", "has_unit_row", *ROLES}, "mapping")
    column = mapping.get("cycle_column")
    require((isinstance(column, str) and bool(column)) != (cycle_id is not None),
            "Choose either mapping.cycle_column or --cycle-id (not both)")
    if cycle_id is not None:
        safe_name(cycle_id)
    delimiter = mapping.get("delimiter", ",")
    require(isinstance(delimiter, str) and len(delimiter) == 1 and delimiter not in '\r\n"',
            "delimiter must be one character other than a quote or newline")
    require(type(mapping.get("has_unit_row", False)) is bool, "has_unit_row must be true or false")
    prepared = {}
    for role in ROLES:
        entries = mapping.get(role, {})
        require(isinstance(entries, dict), f"{role} must be an object")
        prepared[role] = []
        for target, rule in entries.items():
            keys(rule, {"column", "unit", "select"}, target)
            require(isinstance(rule.get("column"), str) and rule["column"], f"{target}: column is required")
            definition = catalogue.resolve(target)
            require(rule.get("unit") == unit_cell(definition),
                    f"{target}: input unit must be {unit_cell(definition)!r}; convert values explicitly before import")
            if role == "timeseries":
                require(definition["dataRepresentation"] == "timeSeries", f"{target} is not a time series")
                require("select" not in rule, f"{target}: selection is only for cycle values")
            else:
                require(definition["dataRepresentation"] == "cycleValue"
                        and definition["valueRole"] == role
                        and definition["variableName"].startswith(role)
                        and definition["variableName"] not in CONTEXT,
                        f"{target} does not belong in the {role} resource")
                require(rule.get("select", "constant") in {"constant", "first", "last"},
                        f"{target}: select must be constant, first or last")
            prepared[role].append((target, rule, definition))
    require(any(prepared.values()), "Map at least one parameter")
    if prepared["timeseries"]:
        require("relativeTimestampCycle" in mapping["timeseries"],
                "Time series require a relativeTimestampCycle mapping in ms")
        require(len(prepared["timeseries"]) > 1, "Map at least one signal beside the time axis")
        prepared["timeseries"].sort(key=lambda item: item[0] != "relativeTimestampCycle")
    check_profiles(prepared["set"], catalogue)
    return prepared


def check_profiles(entries, catalogue):
    """Check companion columns for the catalogue's segmented set-value profiles."""
    headers = {target for target, _, _ in entries}

    def indices(name):
        require(name not in headers, f"Profile parameter {name} needs explicit indices in this parser")
        return {int(h[len(name) + 1:]) for h in headers
                if re.fullmatch(re.escape(name) + r"_[1-9][0-9]*", h)}

    for definition in catalogue.definitions.values():
        profile = definition.get("profileSegments")
        if not profile:
            continue
        name = definition["variableName"]
        segments = indices(name)
        if "segmentEndPositionParameterRef" in profile:
            position = profile["segmentEndPositionParameterRef"]
            endpoints = indices(position)
            force = profile["segmentForceLimitParameterRef"]
            limits = indices(force)
            if not segments and not endpoints and not limits:
                continue
            require(segments and segments == set(range(1, len(segments) + 1)),
                    f"{name}: segments must be 1..N")
            allowed_endpoints = [segments]
            if "defaultLastSegmentEndPosition" in profile:
                allowed_endpoints.append(segments - {len(segments)})
            require(endpoints in allowed_endpoints,
                    f"{name}: inconsistent endpoint indices for {position}")
            require(not limits or limits == segments,
                    f"{name}: inconsistent force-limit indices for {force}")
            continue
        companion = profile.get("segmentDurationParameterRef") or profile["internalBreakpoints"]["parameterRef"]
        other = indices(companion)
        if not segments and not other:
            continue
        require(segments and segments == set(range(1, len(segments) + 1)), f"{name}: segments must be 1..N")
        expected = segments if "segmentDurationParameterRef" in profile else set(range(1, len(segments)))
        require(other == expected, f"{name}: inconsistent companion indices for {companion}")


def prepare_context(config, catalogue):
    keys(config, {"machine_folder", "manifest"}, "context config")
    machine = safe_name(config.get("machine_folder"))
    context = config.get("manifest", {})
    require(isinstance(context, dict), "manifest context must be an object")
    result = {}
    for name, value in context.items():
        if name == "manifestMetadata":
            require(isinstance(value, dict) and "csvToCyclePackage" not in value,
                    "manifestMetadata must be an object; csvToCyclePackage is reserved for provenance")
            result[name] = value.copy()
            continue
        require(name not in STRUCTURAL and name != "measuredTimeCreationFile", f"Generated field cannot be configured: {name}")
        definition = catalogue.resolve(name, allow_cycle_quality_label=True)
        require(definition["valueRole"] in {"nominal", "description"} or name in CONTEXT,
                f"{name}: process values belong in CSV resources")
        converted = typed(value, definition, name)
        require(converted == value and type(converted) is type(value)
                or (definition["dataType"] == "float" and type(value) in {int, float}),
                f"{name}: use the catalogue's JSON type in the context config")
        result[name] = converted
    for name in ("nominalDiameterScrew", "actualTimestepSizeIMM"):
        if name in result:
            require(result[name] is not None and result[name] > 0, f"{name} must be positive")
    count = result.get("nominalCountCavitiesMould")
    require(count is None or count >= 1, "nominalCountCavitiesMould must be positive or null")
    filler = result.get("nominalMaterialFillerPercentWeight")
    require(filler is None or 0 <= filler <= 100, "Filler percentage must be between 0 and 100")
    for name, value in result.items():
        if name.startswith("descriptionMouldCavity_"):
            require(isinstance(value, str) and value.strip(), f"{name} must be nonempty")
            require(count is None or int(name.rsplit("_", 1)[1]) <= count, f"{name} exceeds the cavity count")
    if "actualCountCycleMachine" in result:
        require(result["actualCountCycleMachine"] is not None and result["actualCountCycleMachine"] >= 0,
                "actualCountCycleMachine must be nonnegative")
    if "actualTimeCycleStart" in result:
        value = result["actualTimeCycleStart"]
        require(isinstance(value, str) and "T" in value, "actualTimeCycleStart needs an ISO timestamp")
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
        require(stamp.tzinfo is not None, "actualTimeCycleStart needs a timezone")
    return machine, result


def read_cycles(data, mapping, prepared, cycle_id):
    reader = csv.reader(io.StringIO(data.decode("utf-8-sig"), newline=""),
                        delimiter=mapping.get("delimiter", ","), strict=True)
    header = next(reader, [])
    require(header and all(header) and len(set(header)) == len(header), "CSV header must be nonempty and unique")
    required = {rule["column"] for entries in prepared.values() for _, rule, _ in entries}
    if cycle_id is None:
        required.add(mapping["cycle_column"])
    require(required <= set(header), f"Missing CSV columns: {sorted(required - set(header))}")
    if mapping.get("has_unit_row", False):
        units = next(reader, [])
        require(len(units) == len(header), "Invalid or missing input unit row")
        unit_map = dict(zip(header, units))
        for entries in prepared.values():
            for target, rule, _ in entries:
                require(unit_map[rule["column"]] == rule["unit"], f"Input unit row disagrees with mapping for {target}")
    cycles = {}
    seen = set()
    previous = None
    for row in reader:
        require(len(row) == len(header), f"CSV line {reader.line_num}: expected {len(header)} cells, got {len(row)}")
        record = dict(zip(header, row))
        identifier = safe_name(cycle_id if cycle_id is not None else record[mapping["cycle_column"]])
        if identifier != previous:
            require(identifier.casefold() not in seen, f"Repeated cycle block or counter reset: {identifier}")
            if previous is not None and previous.isdigit() and identifier.isdigit():
                require(int(identifier) > int(previous), "Decreasing/repeated cycle counter; split acquisition runs explicitly")
            seen.add(identifier.casefold())
            cycles[identifier] = []
            previous = identifier
        cycles[identifier].append((reader.line_num, record))
    require(cycles, "CSV has no observations")
    return cycles


def values_for_cycle(rows, prepared):
    tables = {}
    for role, entries in prepared.items():
        if not entries:
            continue
        columns = []
        for target, rule, definition in entries:
            values = [typed(row[rule["column"]], definition, f"CSV line {line}, {target}") for line, row in rows]
            if role != "timeseries":
                selection = rule.get("select", "constant")
                if selection == "constant":
                    compared = [comparison_value(v, definition) for v in values]
                    require(all(v == compared[0] for v in compared), f"{target} changes within a cycle; specify first/last only if scientifically justified")
                values = [values[-1] if selection == "last" else values[0]]
            elif target == "relativeTimestampCycle":
                require(all(v is not None and v >= 0 for v in values), "Time axis must be nonnegative and nonmissing")
                require(all(b > a for a, b in zip(values, values[1:])), "Time axis must increase strictly within each cycle")
            columns.append(values)
        tables[role] = list(zip(*columns))
    if "set" in tables:
        selected = dict(zip((target for target, _, _ in prepared["set"]), tables["set"][0]))
        profiles = {definition["variableName"]: definition["profileSegments"]
                    for _, _, definition in prepared["set"] if "profileSegments" in definition}
        for name, profile in profiles.items():
            start = profile.get("rampStartValueParameterRef")
            mode = selected.get(profile.get("interpolationParameterRef"))
            if start and isinstance(mode, str) and mode.casefold() == "ramps":
                require(selected.get(start) is not None,
                        f"{name}: Ramps requires a nonmissing {start} start value")
            if "segmentEndPositionParameterRef" in profile:
                position = profile["segmentEndPositionParameterRef"]
                force = profile["segmentForceLimitParameterRef"]
                for target, value in selected.items():
                    if re.fullmatch(re.escape(position) + r"_[1-9][0-9]*", target):
                        require(value is not None, f"{target}: a supplied endpoint must be nonmissing")
                    if re.fullmatch(re.escape(force) + r"_[1-9][0-9]*", target):
                        require(value is None or value >= 0, f"{target}: force limit must be nonnegative")
    return tables


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def convert(input_path, mapping_path, context_path, output, specification=SPECIFICATION, cycle_id=None):
    """Create a new output tree; never modify source files or an existing output."""
    input_path, specification, output = Path(input_path), Path(specification), Path(output).absolute()
    require(not output.exists() and not output.is_symlink(), f"Output already exists: {output}")
    require(output.parent.is_dir(), "Output parent must already exist")
    snapshots = {name: (specification / name).read_bytes() for name in
                 ("parameterDefinition.json", "parameterDefinition.schema.json", "manifest.schema.json")}
    catalogue = Catalogue(json.loads(snapshots["parameterDefinition.json"].decode("utf-8-sig")))
    schema = json.loads(snapshots["manifest.schema.json"].decode("utf-8-sig"))
    mapping = read_json(mapping_path)
    prepared = prepare_mapping(mapping, catalogue, cycle_id)
    machine, context = prepare_context(read_json(context_path), catalogue)
    data = input_path.read_bytes()
    cycles = read_cycles(data, mapping, prepared, cycle_id)
    if len(cycles) > 1:
        require(not {"actualTimeCycleStart", "actualCountCycleMachine"} & context.keys(),
                "A static cycle start/counter is valid only for single-cycle input")
        require("measuredQualityCycleIsGood" not in context,
                "A supplied cycle-quality label is valid only for single-cycle input")
    provenance = {"software": "csv_to_cycle_package", "version": VERSION,
                  "sourceFile": input_path.name, "sourceSha256": hashlib.sha256(data).hexdigest(),
                  "mapping": mapping, "fixedCycleId": cycle_id,
                  "cycleCompleteness": "notAssessed"}
    # A private temporary directory under the chosen parent bounds all cleanup.
    # No user path is recursively removed; only this TemporaryDirectory is cleaned.
    with tempfile.TemporaryDirectory(prefix=".cycle-package-", dir=output.parent) as temporary:
        stage = Path(temporary) / "dataset"
        require(stage.resolve().parent.parent == output.parent.resolve(), "Unexpected staging path")
        definitions = stage / "_definitions"
        definitions.mkdir(parents=True)
        for name, content in snapshots.items():
            (definitions / name).write_bytes(content)
        for identifier, rows in cycles.items():
            tables = values_for_cycle(rows, prepared)
            root = stage / machine / identifier
            root.mkdir(parents=True)
            resources = []
            for role, observations in tables.items():
                folder = "timeseries" if role == "timeseries" else "actual_set_parameters"
                relative = f"{folder}/{role}_{identifier}.csv"
                path = root / relative
                path.parent.mkdir(exist_ok=True)
                with path.open("w", encoding="utf-8", newline="") as handle:
                    writer = csv.writer(handle, lineterminator="\n")
                    writer.writerow([target for target, _, _ in prepared[role]])
                    writer.writerow([unit_cell(d) for _, _, d in prepared[role]])
                    writer.writerows([[str(v).lower() if isinstance(v, bool) else v for v in row] for row in observations])
                resources.append({"path": relative, "role": ROLES[role]})
            metadata = dict(context.get("manifestMetadata", {}))
            metadata["csvToCyclePackage"] = {**provenance, "sourceLines": [rows[0][0], rows[-1][0]]}
            manifest = {**context, "$schema": "../../_definitions/manifest.schema.json",
                        "manifestVersion": schema["properties"]["manifestVersion"]["const"],
                        "parameterDefinition": "../../_definitions/parameterDefinition.json",
                        "cycleId": identifier, "resources": resources,
                        "measuredTimeCreationFile": datetime.now(timezone.utc).isoformat(),
                        "manifestMetadata": metadata}
            write_json(root / "manifest.json", manifest)
        require(not output.exists() and not output.is_symlink(), f"Output already exists: {output}")
        stage.rename(output)
    return [output / machine / identifier / "manifest.json" for identifier in cycles]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="UTF-8 CSV, one row per observation")
    parser.add_argument("--mapping", required=True, type=Path, help="JSON column mapping")
    parser.add_argument("--context", required=True, type=Path, help="JSON machine folder and manifest context")
    parser.add_argument("--output", required=True, type=Path, help="New output directory; parent must exist")
    parser.add_argument("--specification", type=Path, default=SPECIFICATION, help="Directory with catalogue and both schemas")
    parser.add_argument("--cycle-id", help="Assign all input rows to this cycle; omit mapping.cycle_column")
    parser.add_argument("--version", action="version", version=VERSION)
    args = parser.parse_args()
    try:
        results = convert(args.input, args.mapping, args.context, args.output, args.specification, args.cycle_id)
    except (ValueError, OSError, KeyError, TypeError, csv.Error) as error:
        parser.exit(2, f"Error: {error}\n")
    print(f"Wrote {len(results)} cycle package(s) to {args.output}")


if __name__ == "__main__":
    main()
