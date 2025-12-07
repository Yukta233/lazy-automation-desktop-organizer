#!/usr/bin/env python3
"""
desktop_cleaner.py
Core logic for organizing Desktop files with automatic detection of OneDrive or local Desktop.
"""

import shutil
import logging
from pathlib import Path
import yaml
import os

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def get_desktop_path() -> Path:
    """
    Returns the path to the user's Desktop.
    Checks for OneDrive Desktop first, falls back to regular Desktop.
    """
    user_profile = Path(os.environ['USERPROFILE'])
    onedrive_desktop = user_profile / "OneDrive" / "Desktop"
    local_desktop = user_profile / "Desktop"

    if onedrive_desktop.exists():
        return onedrive_desktop
    elif local_desktop.exists():
        return local_desktop
    else:
        raise FileNotFoundError("Could not locate a Desktop folder.")


def load_config(path: Path = Path("config.yaml")) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def ensure_folder(folder: Path):
    folder.mkdir(parents=True, exist_ok=True)


def unique_destination(dest: Path) -> Path:
    """
    Return a unique path by appending (1), (2), etc. if file exists.
    """
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


def plan_organize(desk: Path, cfg: dict) -> list[tuple[str, str]]:
    """
    Return a list of (src, dest) tuples that would be moved (dry run).
    """
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
                dest = unique_destination(dest_folder / item.name)
                actions.append((str(item), str(dest)))
                placed = True
                break

        if not placed:
            dest_folder = desk / "Others"
            dest = unique_destination(dest_folder / item.name)
            actions.append((str(item), str(dest)))

    return actions


def perform_organize(desk: Path, cfg: dict, backup: bool = False) -> list[tuple[str, str]]:
    """
    Perform moves. Returns list of performed actions.
    """
    actions = []
    categories = cfg.get("categories", {})
    exclude = set(cfg.get("exclude", []))
    move_hidden = cfg.get("move_hidden", False)

    # Ensure category folders exist
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
                dest = unique_destination(dest_folder / item.name)
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


if __name__ == "__main__":
    # Example usage:
    try:
        desktop = get_desktop_path()
        cfg = load_config()
        planned = plan_organize(desktop, cfg)
        logging.info("Planned actions (dry run):")
        for src, dest in planned:
            logging.info(f"{src} -> {dest}")
    except Exception as e:
        logging.error(e)
