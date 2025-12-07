#!/usr/bin/env python3
from flask import Flask, render_template, jsonify, request
from pathlib import Path
import desktop_cleaner as dc
import yaml
import os

app = Flask(__name__)

# Use an absolute path relative to this file to avoid CWD issues
CONFIG_PATH = Path(__file__).parent / "config.yaml"

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
    # Safely parse JSON body
    data = request.get_json(silent=True) or {}
    backup = bool(data.get("backup", False))
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
    # Bind to all interfaces and allow env overrides for host/port
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "5000"))
    app.run(host=host, port=port, debug=True)
