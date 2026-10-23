#!/usr/bin/env python3
"""Read-only SQLite tuning-cache snapshot and reproducible logical hashes.

Source is opened mode=ro/query_only. Only a new output directory is written.
No environment discovery, FlagGems import, checkpoint, VACUUM or cache reset.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sqlite3
import sys


def utc():
    return datetime.now(timezone.utc).isoformat()


def canonical(value):
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"), allow_nan=False).encode("ascii")


def typed(value):
    if value is None:
        return ["null"]
    if type(value) is int:
        return ["integer", str(value)]
    if type(value) is float:
        return ["real", value.hex()]
    if type(value) is str:
        return ["text", value]
    if type(value) is bytes:
        return ["blob", value.hex()]
    raise TypeError("unsupported SQLite value type: " + type(value).__name__)


def quote_identifier(value):
    if "\x00" in value:
        raise ValueError("SQLite identifier contains NUL")
    return '"' + value.replace('"', '""') + '"'


def open_readonly(path):
    connection = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=10)
    connection.execute("PRAGMA query_only=ON")
    if connection.execute("PRAGMA query_only").fetchone() != (1,):
        connection.close()
        raise RuntimeError("SQLite query_only guard did not take effect")
    return connection


def file_hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fingerprint(snapshot):
    connection = open_readonly(snapshot)
    try:
        schema = connection.execute(
            "SELECT type,name,tbl_name,sql FROM sqlite_schema ORDER BY type,name,tbl_name,sql"
        ).fetchall()
        tables = []
        # Sort encoded rows, retaining duplicates and SQLite scalar types.
        # Memory use is bounded by the largest individual tuning-cache table.
        for name in sorted(row[1] for row in schema if row[0] == "table"):
            quoted = quote_identifier(name)
            columns = connection.execute("PRAGMA table_xinfo(" + quoted + ")").fetchall()
            cursor = connection.execute("SELECT * FROM " + quoted)
            names = [column[0] for column in cursor.description]
            rows = sorted(canonical([typed(value) for value in row]) for row in cursor)
            content = hashlib.sha256()
            for row in rows:
                content.update(row)
                content.update(b"\n")
            tables.append({"name": name, "row_count": len(rows), "column_names": names,
                           "columns_xinfo": columns,
                           "schema_sha256": hashlib.sha256(canonical([row for row in schema if row[2] == name])).hexdigest(),
                           "content_sha256": content.hexdigest()})
        logical = [[table["name"], table["schema_sha256"], table["row_count"], table["content_sha256"]]
                   for table in tables]
        return {
            "schema_objects": schema,
            "schema_sha256": hashlib.sha256(canonical(schema)).hexdigest(),
            "table_count": len(tables),
            "user_table_count": sum(not table["name"].startswith("sqlite_") for table in tables),
            "row_count": sum(table["row_count"] for table in tables),
            "tables": tables,
            "logical_content_sha256": hashlib.sha256(canonical(logical)).hexdigest(),
            "snapshot_pragmas": {key: connection.execute("PRAGMA " + key).fetchone()[0]
                                 for key in ("schema_version", "user_version", "page_size", "page_count", "journal_mode")},
        }
    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="new directory; never overwritten")
    args = parser.parse_args()
    database, output = args.database.resolve(strict=True), args.output.resolve()
    if not database.is_file():
        raise ValueError("database must be an existing regular file")
    output.mkdir(parents=True, exist_ok=False)
    snapshot = output / "snapshot.sqlite"
    snapshot.touch(exist_ok=False)
    manifest = {
        "format": "sqlite-tuning-snapshot-v1", "started_utc": utc(),
        "command": [sys.executable, *sys.argv], "source_database": str(database),
        "snapshot": str(snapshot), "python": platform.python_version(),
        "sqlite_version": sqlite3.sqlite_version,
        "read_protocol": "source URI mode=ro and query_only; SQLite backup to new destination",
        "content_hash_protocol": "per-table lexically sorted typed JSON rows, each followed by LF; duplicates retained",
        "limitations": [
            "Logical schema excludes physical rootpage addresses; snapshot SHA includes physical file layout.",
            "data_version is local to one connection; never compare it across runs as a database identity.",
            "A completed backup is consistent; live source can change before or after it.",
            "Hashes record cache state; they do not make cold/warm caches or different table counts performance-equivalent.",
        ],
    }
    source = open_readonly(database)
    destination = None
    try:
        manifest["source_data_version_before"] = source.execute("PRAGMA data_version").fetchone()[0]
        manifest["backup_started_utc"] = utc()
        destination = sqlite3.connect(snapshot)
        source.backup(destination, pages=256, sleep=0.01)
        destination.close()
        destination = None
        manifest["backup_finished_utc"] = utc()
        manifest["source_data_version_after"] = source.execute("PRAGMA data_version").fetchone()[0]
    finally:
        if destination is not None:
            destination.close()
        source.close()
    manifest.update(fingerprint(snapshot))
    manifest.update(snapshot_sha256=file_hash(snapshot), snapshot_bytes=snapshot.stat().st_size,
                    finished_utc=utc(), status="complete")
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=True, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({key: manifest[key] for key in
                      ("status", "snapshot", "snapshot_sha256", "schema_sha256", "logical_content_sha256", "table_count", "row_count")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
