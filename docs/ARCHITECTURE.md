# Devnox AI Hacker OS - Architecture

## Application Design
Devnox AI Hacker OS follows a modular monolithic architecture written primarily in Python 3. It leverages local AI capabilities to guide automated penetration testing sequences safely.

### Core Modules
* **UI/Frontend:** `ui/main.py` driven by NiceGUI, offering a Python-native dashboard and control center.
* **Agent System:** `agent/main_agent.py` orchestrates the testing loop (Reconnaissance -> Scanning -> Exploitation -> Post-Exploitation). It delegates decision making to the `ai_brain/`.
* **Database:** `database/database.py` manages a SQLite database `data/ai_hackeros.db`. It strictly tracks targets, engagements, and jobs to enforce boundaries.
* **AI Brain:** `ai_brain/llm.py` interfaces with either local models via GGUF (e.g. `nous-hermes-2-solar-10.7b`) or mock providers. The AI suggests plans but never directly executes shell commands without parsing by the agent.

## Persistence and Queuing
Jobs are written to the database with a 'queued' status. A worker (or continuous mode loop) picks up these jobs, checks authorization, and executes the proper tool adapters in `modules/`.
