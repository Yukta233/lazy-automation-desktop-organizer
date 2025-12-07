#!/usr/bin/env python3
from flask import Flask, render_template, jsonify, request
from pathlib import Path
import desktop_cleaner as dc
import yaml
import os

app = Flask(__name__)

CONFIG_PATH = Path("config.yaml")

def load_config():
    return dc.load_config(CONFIG_PATH)

@app.route("/")
def index():
    cfg = load_config()
    return render_template("index.html", config=cfg)

@app.route("/dry-run", methods=["GET"])
def dry_run():
    desktop = dc.get_desktop_path()
    cfg = load_config()
    actions = dc.plan_organize(desktop, cfg)
    return jsonify({"count": len(actions), "actions": actions})

@app.route("/run", methods=["POST"])
def run_organize():
    backup = request.json.get("backup", False)
    desktop = dc.get_desktop_path()
    cfg = load_config()
    actions = dc.perform_organize(desktop, cfg, backup=backup)
    return jsonify({"moved_count": len(actions), "actions": actions})

@app.route("/undo", methods=["POST"])
def undo():
    # run undo script
    from undo_cleaner import undo as undo_func
    undo_func()
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True)
