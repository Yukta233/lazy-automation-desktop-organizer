#!/usr/bin/env python3
"""
desktop_cleaner.py
Core logic for organizing Desktop files.
"""

import shutil
import logging
from pathlib import Path
import yaml
import os

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def get_desktop_path():
    return Path.home() / "Desktop"

def load_config(path: Path = Path("config.yaml")):
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def ensure_folder(folder: Path):
    folder.mkdir(parents=True, exist_ok=True)

def unique_destination(dest: Path):
    if not dest.exists():
        return dest
    stem = dest.stem
    suffix = dest.suffix
    parent = dest.parent
    i = 1
    while True:
        candidate = parent / f"{stem} ({i}){suffix}"
        if not candidate.exists():
            return candidate
        i += 1

def plan_organize(desk: Path, cfg: dict):
    """Return a list of (src, dest) tuples that would be moved (dry run)."""
    actions = []
    categories = cfg.get("categories", {})
    exclude = set(cfg.get("exclude", []))
    move_hidden = cfg.get("move_hidden", False)

    for item in desk.iterdir():
        if item.name in categories.keys() or item.name in exclude:
            continue
        if item.is_dir():
            continue
        if item.name.startswith(".") and not move_hidden:
            continue

        ext = item.suffix.lower()
        placed = False
        for category, exts in categories.items():
            if ext in exts:
                dest_folder = desk / category
                dest = dest_folder / item.name
                dest = unique_destination(dest)
                actions.append((str(item), str(dest)))
                placed = True
                break
        if not placed:
            dest_folder = desk / "Others"
            dest = dest_folder / item.name
            dest = unique_destination(dest)
            actions.append((str(item), str(dest)))
    return actions

def perform_organize(desk: Path, cfg: dict, backup: bool = False):
    """Perform moves. Returns list of performed actions."""
    actions = []
    categories = cfg.get("categories", {})
    exclude = set(cfg.get("exclude", []))
    move_hidden = cfg.get("move_hidden", False)

    for category in categories.keys():
        ensure_folder(desk / category)
    ensure_folder(desk / "Others")
    if backup:
        ensure_folder(desk / "Backup")

    for item in desk.iterdir():
        if item.name in categories.keys() or item.name in exclude:
            continue
        if item.is_dir():
            continue
        if item.name.startswith(".") and not move_hidden:
            continue

        ext = item.suffix.lower()
        moved = False
        for category, exts in categories.items():
            if ext in exts:
                dest_folder = desk / category
                dest = dest_folder / item.name
                dest = unique_destination(dest)
                if backup:
                    bak_dest = unique_destination(desk / "Backup" / item.name)
                    shutil.copy2(item, bak_dest)
                shutil.move(str(item), str(dest))
                actions.append((str(item), str(dest)))
                moved = True
                break
        if not moved:
            dest_folder = desk / "Others"
            dest = unique_destination(dest_folder / item.name)
            if backup:
                bak_dest = unique_destination(desk / "Backup" / item.name)
                shutil.copy2(item, bak_dest)
            shutil.move(str(item), str(dest))
            actions.append((str(item), str(dest)))
    return actions
