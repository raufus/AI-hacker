# Architecture

- **Core Strategy:** Python-first modular monolith.
- **Frontend:** NiceGUI for native python rich interfaces (`ui/main.py`). FastAPI + Jinja2 for a standalone dashboard (`dashboard/dashboard.py`).
- **Data Persistence:** SQLite database (`database/database.py`) with models for Users, Assets, Engagements, Jobs, and Findings.
- **Background Jobs:** Handled via SQLite queue where a persistent worker (`automation/worker.py`) picks up queued scans.
- **AI Core:** Built around abstracted AI providers in `ai_providers/`, with local GGUF models acting as the default strategy (`ai/llama_engine.py`).
- **Scanning Engine:** Tools are wrapped in Python adapters (`modules/scanning/`) and run as isolated subprocesses to prevent unsafe string interpolation.
