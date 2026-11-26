#!/usr/bin/env python3
"""Create a privacy-conscious inventory of a locally extracted Belgium OBU dataset.

Streams large CSV/TSV files; does not copy dataset contents. Cell values are never
written to the report. Only filenames, sizes, positional column metadata, sampled type hints and
sample counts are recorded. No header is assumed by default.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from collections import Counter
from datetime import datetime
from pathlib import Path

SAMPLE_ROWS = 50


def guess_type(values: list[str]) -> str:
    vals = [v.strip() for v in values if v and v.strip()]
    if not vals:
        return "empty_or_unknown"
    def is_int(s: str) -> bool:
        try: int(s); return True
        except ValueError: return False
    def is_float(s: str) -> bool:
        try: return math.isfinite(float(s))
        except ValueError: return False
    if all(is_int(v) for v in vals): return "integer_like"
    if all(is_float(v) for v in vals): return "numeric_like"
    low = [v.lower() for v in vals]
    if all(v in {"true", "false", "yes", "no", "0", "1"} for v in low): return "boolean_like"
    return "text_or_identifier"


def sniff_delimiter(path: Path) -> str:
    if path.suffix.lower() == ".tsv": return "\t"
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
        sample = f.read(65536)
    try: return csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
    except csv.Error: return ","


def csv_info(path: Path) -> dict:
    """Inspect headerless time-series CSVs without assuming row 1 is a header.

    The Belgium OBU inventory's first pass showed timestamp/numeric values being
    mistaken for column names. This version treats every row as data and reports
    positional fields only; it never writes sampled cell values.
    """
    delimiter = sniff_delimiter(path)
    values: list[list[str]] = []
    sampled_rows = 0
    malformed_rows = 0
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
        reader = csv.reader(f, delimiter=delimiter)
        for row in reader:
            if not row:
                continue
            if not values:
                values = [[] for _ in row]
            if len(row) != len(values):
                malformed_rows += 1
                if len(row) > len(values):
                    values.extend([[] for _ in range(len(row) - len(values))])
            for i in range(len(values)):
                values[i].append(row[i] if i < len(row) else "")
            sampled_rows += 1
            if sampled_rows >= SAMPLE_ROWS:
                break
    return {
        "format": "csv/tsv",
        "header_assumption": "headerless; first row treated as data pending dataset documentation",
        "delimiter": "TAB" if delimiter == "\t" else delimiter,
        "column_count": len(values),
        "columns": [
            {"index": i, "sampled_type": guess_type(col),
             "sampled_nonempty": sum(bool(v.strip()) for v in col)}
            for i, col in enumerate(values)
        ],
        "sampled_rows": sampled_rows,
        "rows_with_unexpected_column_count": malformed_rows,
        "note": "Only up to 50 data rows were sampled. Cell values are intentionally excluded; field meanings require dataset documentation.",
    }

def _parse_datetime(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None

def csv_quality_info(path: Path) -> dict:
    """Scan every record without storing or reporting cell values."""
    delimiter = sniff_delimiter(path)
    sample_values: list[list[str]] = []
    field_stats: list[Counter] = []
    row_widths: Counter[int] = Counter()
    total_rows = 0
    blank_rows = 0
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as source:
        reader = csv.reader(source, delimiter=delimiter)
        for row in reader:
            if not row or all(not value.strip() for value in row):
                blank_rows += 1
                continue
            total_rows += 1
            row_widths[len(row)] += 1
            if len(row) > len(field_stats):
                extra = len(row) - len(field_stats)
                for _ in range(extra):
                    stat = Counter()
                    stat["empty_values"] = total_rows - 1
                    field_stats.append(stat)
                sample_values.extend([] for _ in range(extra))
            for index in range(len(field_stats)):
                value = row[index].strip() if index < len(row) else ""
                stat = field_stats[index]
                stat["empty_values" if not value else "nonempty_values"] += 1
                if not value:
                    continue
                if "\ufffd" in value:
                    stat["utf8_replacement_char_values"] += 1
                if len(sample_values[index]) < SAMPLE_ROWS:
                    sample_values[index].append(value)
                try:
                    number = float(value)
                except ValueError:
                    parsed = _parse_datetime(value)
                    if parsed is not None:
                        stat["text_timestamp_values"] += 1
                        if parsed.tzinfo is None:
                            stat["naive_text_timestamp_values"] += 1
                        else:
                            stat["timezone_aware_text_timestamp_values"] += 1
                    continue
                stat["numeric_values"] += 1
                if not math.isfinite(number):
                    stat["nonfinite_numeric_values"] += 1
                    continue
                if 946684800 <= number <= 4102444800:
                    stat["epoch_seconds_candidate_values"] += 1
                if 946684800000 <= number <= 4102444800000:
                    stat["epoch_milliseconds_candidate_values"] += 1
    modal_width = max(row_widths, key=lambda width: (row_widths[width], -width)) if row_widths else 0
    columns = []
    for index, stat in enumerate(field_stats):
        columns.append({
            "index": index,
            "sampled_type": guess_type(sample_values[index]),
            **dict(stat),
        })
    return {
        "format": "csv/tsv",
        "header_assumption": "headerless; first row treated as data pending source documentation",
        "delimiter": "TAB" if delimiter == "\t" else delimiter,
        "full_scan": True,
        "total_nonblank_rows": total_rows,
        "blank_rows": blank_rows,
        "modal_column_count": modal_width,
        "rows_with_unexpected_column_count": sum(count for width, count in row_widths.items() if width != modal_width),
        "row_width_counts": {str(width): count for width, count in sorted(row_widths.items())},
        "columns": columns,
        "note": "All rows were counted. Only up to 50 values per position were used for type hints; raw values and exact numeric ranges are omitted. Field meanings and units require source documentation.",
    }

def json_structure_info(path: Path) -> dict:
    """Summarize JSON structure and schema keys without reporting feature values."""
    data = json.loads(path.read_text(encoding="utf-8"))
    result = {"format": "json", "root_type": type(data).__name__}
    if not isinstance(data, dict):
        return result
    result["root_keys"] = sorted(data.keys())
    crs = data.get("crs")
    if isinstance(crs, dict):
        result["crs_name"] = (crs.get("properties") or {}).get("name")
    features = data.get("features")
    if isinstance(features, list):
        result["feature_count"] = len(features)
        result["feature_keys"] = sorted({key for item in features if isinstance(item, dict) for key in item.keys()})
        result["geometry_types"] = sorted({
            item.get("geometry", {}).get("type")
            for item in features
            if isinstance(item, dict) and isinstance(item.get("geometry"), dict)
        })
        result["property_keys"] = sorted({
            key
            for item in features
            if isinstance(item, dict) and isinstance(item.get("properties"), dict)
            for key in item["properties"].keys()
        })
    geometries = data.get("geometries")
    if isinstance(geometries, list):
        result["geometry_count"] = len(geometries)
        result["geometry_types"] = sorted({
            item.get("type") for item in geometries if isinstance(item, dict)
        })
        result["geometry_keys"] = sorted({
            key for item in geometries if isinstance(item, dict) for key in item.keys()
        })
    return result

def file_signature(path: Path) -> str:
    try:
        with path.open("rb") as f: head = f.read(16)
    except OSError: return "unreadable"
    if head.startswith(b"PAR1"): return "parquet"
    if head.startswith(b"PK\x03\x04"): return "zip_container_or_office_file"
    if head.startswith(b"%PDF"): return "pdf"
    if head.startswith(b"\x89PNG\r\n\x1a\n"): return "png"
    if head.startswith(b"\xff\xd8\xff"): return "jpeg"
    if head.startswith((b"II*\x00", b"MM\x00*")): return "tiff"
    if head.startswith(b"SQLite format 3\x00"): return "sqlite"
    return "unknown_or_text"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("dataset_folder", help="Root folder containing the extracted dataset")
    p.add_argument("--output", default="belgium_obu_inventory", help="Output filename prefix")
    p.add_argument("--full-scan", action="store_true", help="Count every CSV row and field without exporting values")
    args = p.parse_args()
    root = Path(args.dataset_folder).expanduser().resolve()
    if not root.is_dir():
        p.error(f"Dataset folder does not exist: {root}")
    entries = []
    totals = Counter()
    for path in sorted(x for x in root.rglob("*") if x.is_file()):
        rel = str(path.relative_to(root))
        size = path.stat().st_size
        ext = path.suffix.lower() or "[no extension]"
        item = {"relative_path": rel, "extension": ext, "size_bytes": size,
                "size_mb": round(size / (1024 * 1024), 3), "signature": file_signature(path)}
        if ext in {".csv", ".tsv"}:
            try: item["details"] = csv_quality_info(path) if args.full_scan else csv_info(path)
            except Exception as exc: item["inspection_error"] = type(exc).__name__
        elif ext == ".json":
            try: item["details"] = json_structure_info(path)
            except Exception as exc: item["inspection_error"] = type(exc).__name__
        elif ext in {".jsonl", ".ndjson"}:
            item["details"] = {"format": "json-lines", "note": "Not parsed; content not copied."}
        elif ext == ".parquet":
            item["details"] = {"format": "parquet", "note": "Install pyarrow locally if schema inspection is needed."}
        entries.append(item)
        totals[ext] += 1
    report = {"dataset_root_name": root.name, "file_count": len(entries),
              "total_size_bytes": sum(x["size_bytes"] for x in entries),
              "counts_by_extension": dict(totals), "files": entries,
              "privacy": "No cell values, document contents, names, phone numbers or precise location records are exported."}
    out = Path(args.output).expanduser().resolve()
    if out.suffix.lower() == ".json": out = out.with_suffix("")
    json_path = out.with_suffix(".json")
    csv_path = out.with_name(out.name + "_files.csv")
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["relative_path", "extension", "size_bytes", "size_mb", "signature"])
        writer.writeheader()
        for item in entries: writer.writerow({k: item.get(k) for k in writer.fieldnames})
    print(f"Inventory complete: {len(entries)} files")
    print(f"JSON report: {json_path}")
    print(f"File list:   {csv_path}")
    print("No dataset cell values were included.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
