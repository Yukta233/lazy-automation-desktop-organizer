# Desktop Organizer

A small local web UI + Python automation to organize your Desktop files into categorized folders.

## Features
- Dry-run preview
- Actual organize (move files)
- Optional backup
- Undo (restore moved files)
- Customizable categories in `config.yaml`
- Local-only (runs on your machine)

## Requirements
- Python 3.8+
- pip

## Setup (fast)
```bash
# clone
git clone https://github.com/<your-username>/desktop-organizer.git
cd desktop-organizer

# create venv
python -m venv venv
# mac/linux
source venv/bin/activate
# windows
# venv\Scripts\activate

pip install -r requirements.txt
