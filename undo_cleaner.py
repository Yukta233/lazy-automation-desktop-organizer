#!/usr/bin/env python3
"""
undo_cleaner.py
Move files from category folders back to Desktop root (simple restore).
"""
import logging
from pathlib import Path
import shutil

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

def get_desktop_path():
    return Path.home() / "Desktop"

def undo():
    desktop = get_desktop_path()
    skip = {"Backup", ".git", "sample-before-after"}
    for folder in desktop.iterdir():
        if folder.is_dir() and folder.name not in skip:
            for f in list(folder.iterdir()):
                dst = desktop / f.name
                # handle conflict
                if dst.exists():
                    dst = desktop / f"{f.stem} (restored){f.suffix}"
                shutil.move(str(f), str(dst))
                logging.info(f"Restored {f} -> {dst}")
    logging.info("Undo complete.")

if __name__ == "__main__":
    undo()
