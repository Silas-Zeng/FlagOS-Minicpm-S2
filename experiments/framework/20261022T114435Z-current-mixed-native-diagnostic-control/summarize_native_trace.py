#!/usr/bin/env python3
"""Read a native profiler SQLite export; emit evidence, not a capture verdict.

Example: python scripts/summarize_native_trace.py trace.json --time-unit ns
Exit 0: positive-duration GPU kernel records; 2: no timed GPU kernel evidence;
3: input/read error. A .json suffix does not imply a JSON file. No dependencies
outside the Python standard library are needed. The input is opened mode=ro.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import re
import sqlite3
import statistics
import sys
from typing import Any


def ident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def safe(value: Any) -> Any:
    if isinstance(value, bytes):
        return {"blob_hex": value.hex()}
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    return value


def schema_of(connection: sqlite3.Connection) -> dict[str, dict[str, Any]]:
    result = {}
    for name, kind in connection.execute(
        "SELECT name,type FROM sqlite_master WHERE type IN ('table','view') "
        "AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall():
        columns = [r[1] for r in connection.execute(f"PRAGMA table_info({ident(name)})")]
        entry = {"kind": kind, "columns": columns}
        try:
            entry["rows"] = connection.execute(
                f"SELECT COUNT(*) FROM {ident(name)}"
            ).fetchone()[0]
        except sqlite3.Error as error:
            entry.update(rows=None, read_error=str(error))
        result[name] = entry
    return result


def column(columns: list[str], *choices: str) -> str | None:
    by_norm = {norm(c): c for c in columns}
    return next((by_norm[norm(c)] for c in choices if norm(c) in by_norm), None)


def lookup(connection: sqlite3.Connection, schema: dict, candidates: tuple[str, ...],
           key_choices: tuple[str, ...], value_choices: tuple[str, ...]) -> dict:
    for table in candidates:
        if table not in schema or not schema[table].get("rows"):
            continue
        columns = schema[table]["columns"]
        key, value = column(columns, *key_choices), column(columns, *value_choices)
        if key and value:
            return dict(connection.execute(
                f"SELECT {ident(key)},{ident(value)} FROM {ident(table)}"
            ))
    return {}


def process_maps(connection: sqlite3.Connection, schema: dict) -> tuple[dict, dict, dict]:
    processes, threads, tracks = {}, {}, {}
    for table in ("process", "internal_process"):
        if table not in schema:
            continue
        columns = schema[table]["columns"]
        key, pid = column(columns, "upid", "id"), column(columns, "pid")
        name = column(columns, "name")
        if key and pid:
            for row in connection.execute(f"SELECT * FROM {ident(table)}"):
                data = dict(zip(columns, row))
                processes[data[key]] = {"pid": data[pid], "name": data.get(name)}
    for table in ("thread", "internal_thread"):
        if table not in schema:
            continue
        columns = schema[table]["columns"]
        key, upid = column(columns, "utid", "id"), column(columns, "upid")
        if key and upid:
            threads.update(connection.execute(
                f"SELECT {ident(key)},{ident(upid)} FROM {ident(table)}"
            ))
    for table, entry in schema.items():
        if "track" not in table.lower() or not entry.get("rows"):
            continue
        columns = entry["columns"]
        key = column(columns, "id")
        upid, utid = column(columns, "upid"), column(columns, "utid")
        if key and (upid or utid):
            for row in connection.execute(f"SELECT * FROM {ident(table)}"):
                data = dict(zip(columns, row))
                owner = data.get(upid) if upid else threads.get(data.get(utid))
                if owner in processes:
                    tracks[data[key]] = processes[owner]
    return processes, threads, tracks


def event_query(connection: sqlite3.Connection, schema: dict, table: str) -> tuple[str, str, list[str]]:
    """Use an existing decoded view, or a checked one-to-one slice join."""
    entry = schema[table]
    view = table[:-5] if table.endswith("_data") else None
    if view and view in schema and schema[view]["kind"] == "view":
        if schema[view].get("rows") == entry.get("rows"):
            return f"SELECT * FROM {ident(view)}", f"existing view {view}", schema[view]["columns"]
    columns = entry["columns"]
    if column(columns, "dur", "duration", "duration_ns", "duration_us", "duration_ms", "duration_s"):
        return f"SELECT * FROM {ident(table)}", "direct table", columns
    source_id = column(columns, "id")
    if source_id and entry.get("rows"):
        for slices in ("internal_slice", "slice"):
            if slices not in schema or not schema[slices].get("rows"):
                continue
            extra = schema[slices]["columns"]
            slice_id = column(extra, "id", "slice_id")
            if not slice_id or not column(extra, "dur", "duration"):
                continue
            # Perfetto derived tables share ids. Verify this instance, rather
            # than inferring a correlationId/pid relation from matching numbers.
            counts = connection.execute(
                f"SELECT COUNT(*),COUNT(DISTINCT {ident(source_id)}) FROM {ident(table)}"
            ).fetchone()
            matches = connection.execute(
                f"SELECT COUNT(*) FROM {ident(table)} b JOIN {ident(slices)} s "
                f"ON b.{ident(source_id)}=s.{ident(slice_id)}"
            ).fetchone()[0]
            if counts[0] == counts[1] == matches:
                added = [c for c in extra if norm(c) not in {norm(v) for v in columns}]
                selections = ["b.*"] + [f"s.{ident(c)}" for c in added]
                return (
                    f"SELECT {','.join(selections)} FROM {ident(table)} b "
                    f"JOIN {ident(slices)} s ON b.{ident(source_id)}=s.{ident(slice_id)}",
                    f"checked 1:1 id join to {slices}; schema-family interpretation",
                    columns + added,
                )
    return f"SELECT * FROM {ident(table)}", "no timing join available", columns


PARAMETERS = {
    "shape", "shapes", "inputshape", "inputshapes", "inputdims", "tensorshapes",
    "m", "n", "k", "dtype", "grid", "block", "griddim", "blockdim",
    "gridx", "gridy", "gridz", "blockx", "blocky", "blockz", "regs", "srfs",
    "registersperthread", "staticsharedmemory", "dynamicsharedmemory",
    "sharedmemory", "numwarps", "numstages", "blockm", "blockn", "blockk",
}


def duration_unit(field: str | None, requested: str) -> tuple[str, str]:
    if requested != "auto":
        return requested, "explicit CLI override" if requested != "unknown" else "explicit unknown"
    if field:
        for unit in ("ns", "us", "ms", "s"):
            if norm(field) == "duration" + unit or field.lower().endswith("_" + unit):
                return unit, "duration column suffix"
    return "unknown", "plain ts/dur SQL columns do not declare units; use --time-unit only with format evidence"


def stats(values: list[int | float], unit: str) -> dict[str, Any]:
    values.sort()
    result = {
        "samples": len(values), "sum_raw": sum(values),
        "median_raw": statistics.median(values) if values else None,
        "p95_raw": values[math.ceil(len(values) * .95) - 1] if values else None,
        "min_raw": values[0] if values else None,
        "max_raw": values[-1] if values else None, "unit": unit,
    }
    factor = {"ns": 1e-6, "us": 1e-3, "ms": 1., "s": 1e3}.get(unit)
    if factor is not None:
        result.update({key.replace("_raw", "_ms"): result[key] * factor
                       if result[key] is not None else None
                       for key in ("sum_raw", "median_raw", "p95_raw", "min_raw", "max_raw")})
    return result


def summarize(connection: sqlite3.Connection, requested_unit: str, top: int) -> dict:
    schema = schema_of(connection)
    processes, threads, tracks = process_maps(connection, schema)
    names = lookup(connection, schema, ("function_name_map",), ("id",), ("name",))
    sizes = lookup(connection, schema, ("function_size_map",), ("id",), ("name",))
    pid_names = {p["pid"]: p.get("name") for p in processes.values() if p["pid"] is not None}
    sources, graph_sources, warnings = [], [], []
    # Tables only: decoded views are used by event_query, never added twice.
    candidates = [name for name, entry in schema.items()
                  if entry["kind"] == "table" and "kernel" in name.lower()]
    graph_candidates = [name for name, entry in schema.items()
                        if entry["kind"] == "table" and "graph" in name.lower()
                        and column(entry["columns"], "dur", "duration")]
    for table in candidates + graph_candidates:
        if not schema[table].get("rows"):
            continue
        query, resolution, columns = event_query(connection, schema, table)
        fields = {norm(c): c for c in columns}
        duration = column(columns, "dur", "duration", "duration_ns", "duration_us", "duration_ms", "duration_s")
        unit, unit_basis = duration_unit(duration, requested_unit)
        groups, owner_durations, owner_counts = {}, defaultdict(list), Counter()
        invalid = Counter()
        graph_fields = [c for c in columns if norm(c) in {"graphid", "graphnodeid", "nodeid"}]
        positive, named = 0, 0
        for row in connection.execute(query):
            data = dict(zip(columns, row))
            kernel = data.get(column(columns, "name", "kernel_name", "function_name"))
            if kernel is None and "nameid" in fields:
                kernel = names.get(data[fields["nameid"]])
            if kernel is None:
                kernel = {"unresolved_name_id": safe(data.get(fields.get("nameid")))}
            else:
                named += 1
            params = {c: safe(data[c]) for c in columns if norm(c) in PARAMETERS and data[c] is not None}
            for base in ("grid", "block"):
                if base not in fields and base + "id" in fields:
                    value = data[fields[base + "id"]]
                    params[base] = sizes.get(value, {"unresolved_id": safe(value)})
            owner = {"pid": None, "name": None, "attribution": "unresolved"}
            pid_field = column(columns, "processId", "process_id", "pid")
            upid_field, utid_field = column(columns, "upid"), column(columns, "utid")
            track_field = column(columns, "track_id")
            if pid_field and data[pid_field] is not None:
                owner = {"pid": safe(data[pid_field]), "name": pid_names.get(data[pid_field]),
                         "attribution": f"direct {pid_field}"}
            elif upid_field and data[upid_field] in processes:
                owner = {**processes[data[upid_field]], "attribution": "upid lookup"}
            elif utid_field and threads.get(data[utid_field]) in processes:
                owner = {**processes[threads[data[utid_field]]], "attribution": "utid -> upid lookup"}
            elif track_field and data[track_field] in tracks:
                owner = {**tracks[data[track_field]], "attribution": "track owner lookup"}
            device_field = column(columns, "deviceId", "device_id", "device")
            device = safe(data[device_field]) if device_field else None
            key = json.dumps([kernel, params, owner, device], sort_keys=True, ensure_ascii=True)
            group = groups.setdefault(key, {"kernel_name": kernel, "parameters": params,
                                            "process": owner, "device": device, "count": 0,
                                            "_durations": []})
            group["count"] += 1
            owner_key = json.dumps(owner, sort_keys=True)
            owner_counts[owner_key] += 1
            value = data.get(duration)
            if not isinstance(value, (int, float)) or not math.isfinite(value):
                invalid["missing_or_nonnumeric"] += 1
            elif value < 0:
                invalid["negative_or_unfinished"] += 1
            else:
                group["_durations"].append(value)
                owner_durations[owner_key].append(value)
                positive += value > 0
        rows = []
        for group in groups.values():
            group["duration"] = stats(group.pop("_durations"), unit)
            rows.append(group)
        rows.sort(key=lambda g: g["duration"]["sum_raw"], reverse=True)
        source = {
            "table": table, "records": schema[table]["rows"], "resolution": resolution,
            "duration_field": duration, "duration_unit": unit, "duration_unit_basis": unit_basis,
            "positive_duration_records": positive, "named_records": named,
            "invalid_durations": dict(invalid), "group_count": len(rows),
            "groups_omitted": max(0, len(rows) - top) if top else 0,
            "groups": rows[:top] if top else rows,
            "processes": [{"process": json.loads(key), "count": count,
                           "duration": stats(owner_durations[key], unit)}
                          for key, count in owner_counts.items()],
            "graph_node_identifier_fields": graph_fields,
            "duration": stats([value for values in owner_durations.values() for value in values], unit),
        }
        if table in graph_candidates:
            for group in source["groups"]:
                group["graph_name"] = group.pop("kernel_name")
            source["role"] = "graph aggregate, not individual graph-node kernel"
            graph_sources.append(source)
        else:
            source["role"] = "auxiliary kernel summary" if any(
                token in table.lower() for token in ("ratio", "summary", "stat")
            ) else "kernel event source (schema heuristic)"
            sources.append(source)
    timed = any(s["positive_duration_records"] for s in sources
                if s["role"].startswith("kernel event"))
    graph_tables = {name: entry["rows"] for name, entry in schema.items()
                    if entry["kind"] == "table" and "graph" in name.lower()
                    and any(norm(c) in {"dur", "duration"} for c in entry["columns"])}
    if not timed:
        warnings.append("No positive-duration GPU kernel evidence. Empty GPU tables are not successful capture evidence.")
    if any(graph_tables.values()) and not timed:
        warnings.append("Graph records exist without timed kernel records; graph internals cannot be ranked from this trace.")
    warnings.extend([
        "Kernel durations are summed activity time, not elapsed latency, utilization, or official throughput; overlapping streams may overlap.",
        "Sources are reported separately and are not summed globally: source tables may describe overlapping or mirrored activity.",
        "Launch grid/block are not tensor M/N/K; tensor shape and process names are unknown unless explicitly present/resolved.",
        "Kernel rows do not establish complete CUDA graph-node visibility. Graph membership and missing graph-internal kernels remain unproven.",
    ])
    if any(graph_tables.values()):
        warnings.append("Graph aggregate durations are separate from kernel activity; do not interpret the external-kernel percentages as graph-internal GEMM/attention shares.")
    return {
        "summary_format": "native_sqlite_kernel_summary_v1", "input_format": "SQLite 3",
        "read_only": True, "status": "timed_gpu_kernel_records_present" if timed else "no_timed_gpu_kernels",
        "has_timed_gpu_kernels": timed, "requested_time_unit": requested_unit,
        "percentile_method": "p95 nearest-rank; median is arithmetic midpoint for even sample counts",
        "nonempty_tables": {n: e["rows"] for n, e in schema.items() if e["kind"] == "table" and e.get("rows")},
        "kernel_tables": {n: schema[n]["rows"] for n in candidates},
        "schema": schema, "kernel_sources": sources, "graph_sources": graph_sources,
        "graph_visibility": {"graph_table_rows": graph_tables, "completeness": "unproven",
                             "membership_fields_present": any(s["graph_node_identifier_fields"] for s in sources),
                             "kernel_share_of_graph_time": None,
                             "reason": "No validated graph-node membership/completeness relation; kernel and graph sums are not a coverage ratio."},
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace", type=Path)
    parser.add_argument("--output", type=Path, help="JSON output; default stdout")
    parser.add_argument("--time-unit", choices=("auto", "unknown", "ns", "us", "ms", "s"), default="auto",
                        help="auto recognizes explicit column suffixes; plain dur remains unknown")
    parser.add_argument("--top", type=int, default=50, help="groups per source; 0 returns all")
    args = parser.parse_args()
    if args.top < 0:
        parser.error("--top must be nonnegative")
    path = args.trace.resolve()
    try:
        with path.open("rb") as handle:
            if handle.read(16) != b"SQLite format 3\x00":
                raise ValueError("Input is not SQLite 3; use the Chrome-trace analyzer for JSON events")
        if args.output and args.output.resolve() == path:
            raise ValueError("Output must not overwrite the input trace")
        connection = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
        try:
            connection.execute("PRAGMA query_only=ON")
            result = summarize(connection, args.time_unit, args.top)
        finally:
            connection.close()
        result["trace_path"] = str(path)
        exit_code = 0 if result["has_timed_gpu_kernels"] else 2
    except (OSError, sqlite3.Error, ValueError) as error:
        result = {"summary_format": "native_sqlite_kernel_summary_v1", "status": "input_or_read_error",
                  "read_only": True, "trace_path": str(path), "error": str(error)}
        exit_code = 3
    # ASCII escaping also keeps JSON valid through Windows code-page pipes.
    payload = json.dumps(result, ensure_ascii=True, indent=2, allow_nan=False) + "\n"
    if args.output:
        try:
            # Repeat the guard even on the error path.
            if args.output.resolve() == path:
                raise ValueError("Output must not overwrite the input trace")
            args.output.write_text(payload, encoding="utf-8")
        except (OSError, ValueError) as error:
            print(json.dumps({"status": "output_error", "error": str(error)}), file=sys.stderr)
            return 3
    else:
        sys.stdout.write(payload)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
