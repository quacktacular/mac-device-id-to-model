#!/usr/bin/env python3
"""Scrape Apple Support 'Identify your Mac' pages into a models file."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

import requests
import yaml
from bs4 import BeautifulSoup, Tag

CONFIG_FILE = Path(__file__).with_name("config.yaml")
FIELDS = ("name", "identifiers", "year", "part_numbers")
HEADING_TAGS = ("h2", "b", "strong")
YEAR_RE = re.compile(r"\b((?:19|20)\d{2})\b")
DEFAULT_OUTPUT = {
    "txt": "models.txt",
    "csv": "models.csv",
    "yaml": "models.yaml",
    "json": "models.json",
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("-f", "--format", action="append", choices=DEFAULT_OUTPUT, dest="formats",
                   help="Output format; repeatable (default: txt).")
    p.add_argument("-o", "--output", type=Path,
                   help="Output path (single --format only; default: models.<format>).")
    p.add_argument("-c", "--config", type=Path, default=CONFIG_FILE,
                   help=f"Config YAML (default: {CONFIG_FILE.name}).")
    args = p.parse_args()
    args.formats = args.formats or ["txt"]
    if args.output and len(args.formats) > 1:
        p.error("-o/--output requires a single --format")
    return args


def load_config(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def tokens(raw: str | list | None) -> list[str]:
    """Split a space/comma-separated field, keeping commas inside IDs (Mac16,6)."""
    if isinstance(raw, list):
        return [str(x).strip() for x in raw if str(x).strip()]
    if not raw:
        return []
    return str(raw).replace(";", " ").replace(", ", " ").split()


def model(name: str, identifiers=None, year="", part_numbers=None) -> dict:
    return {
        "name": name.strip(),
        "identifiers": tokens(identifiers),
        "year": str(year or "").strip(),
        "part_numbers": tokens(part_numbers),
    }


def flat(m: dict) -> dict:
    """Stringify list fields for txt/csv output."""
    return {
        "name": m["name"],
        "identifiers": " ".join(m["identifiers"]),
        "year": m["year"],
        "part_numbers": " ".join(m["part_numbers"]),
    }


def is_model_heading(tag: Tag) -> bool:
    if tag.name not in HEADING_TAGS:
        return False
    text = tag.get_text(strip=True)
    return bool(text) and "model" not in text.lower() and ("(" in text or "Mac" in text)


def labeled_field(start: Tag, label: str) -> str:
    """Read 'Label: value' from following siblings (or the parent's siblings)."""
    siblings = list(start.find_next_siblings())
    if start.parent:
        siblings += list(start.parent.find_next_siblings())
    for tag in siblings:
        text = tag.get_text(strip=True)
        if label not in text:
            continue
        return text.replace(f"{label}s", "").replace(label, "").replace(":", "").strip()
    return ""


def year_for(name: str, heading: Tag) -> str:
    for text in (name, labeled_field(heading, "Year introduced")):
        if match := YEAR_RE.search(text):
            return match.group(1)
    # Rare fallback (older iMac Pro): year on a previous sibling.
    if not heading.parent:
        return ""
    for sibling in heading.parent.find_previous_siblings():
        if match := YEAR_RE.search(sibling.get_text(strip=True)):
            return match.group(1)
    return ""


def parse_heading(heading: Tag) -> dict:
    name = heading.get_text(strip=True)
    return model(
        name,
        labeled_field(heading, "Model Identifier"),
        year_for(name, heading),
        labeled_field(heading, "Part Number"),
    )


def scrape_family(url: str) -> list[dict]:
    page = requests.get(url, timeout=60)
    page.raise_for_status()
    soup = BeautifulSoup(page.content, "html.parser")

    if h1 := soup.find("h1"):
        print(f"Working on: {h1.get_text(strip=True)}")

    models = []
    for heading in soup.find_all(is_model_heading):
        # Skip nested <b> inside <h2> — same model, would duplicate.
        if heading.find_parent(is_model_heading):
            continue
        m = parse_heading(heading)
        print("|".join(flat(m).values()))
        models.append(m)
    return models


def dedupe(models: list[dict]) -> list[dict]:
    seen, unique = set(), []
    for m in models:
        key = (m["name"], tuple(m["identifiers"]), m["year"], tuple(m["part_numbers"]))
        if key in seen:
            continue
        seen.add(key)
        unique.append(m)
    return unique


def write_txt(path: Path, models: list[dict]) -> None:
    path.write_text("\n".join("|".join(flat(m).values()) for m in models) + "\n", encoding="utf-8")


def write_csv(path: Path, models: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(flat(m) for m in models)


def write_yaml(path: Path, models: list[dict]) -> None:
    path.write_text(yaml.safe_dump(models, sort_keys=False, allow_unicode=True), encoding="utf-8")


def write_json(path: Path, models: list[dict]) -> None:
    path.write_text(json.dumps(models, indent=2) + "\n", encoding="utf-8")


WRITERS = {"txt": write_txt, "csv": write_csv, "yaml": write_yaml, "json": write_json}


def main() -> None:
    args = parse_args()
    config = load_config(args.config)

    models = []
    for url in config.get("device_families") or []:
        models.extend(scrape_family(url))
    for entry in config.get("manual_entries") or []:
        m = model(**{k: entry.get(k, "") for k in FIELDS})
        print(f"Manual entry: {'|'.join(flat(m).values())}")
        models.append(m)

    unique = dedupe(models)
    for fmt in args.formats:
        out = args.output or Path(DEFAULT_OUTPUT[fmt])
        WRITERS[fmt](out, unique)
        print(f"Wrote {len(unique)} models to {out} ({len(models) - len(unique)} duplicates dropped)")


if __name__ == "__main__":
    main()
