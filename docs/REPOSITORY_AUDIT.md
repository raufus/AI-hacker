# Devnox AI Hacker OS - Repository Audit

## Architecture and Entry Points
* **Core Language:** Python 3
* **Primary Entry Points:**
  * `main.py`: Command-line interface for manual, auto, and continuous scanning.
  * `ui/main.py`: NiceGUI web application.
* **Database:** SQLite (`data/ai_hackeros.db`) managed via `database/database.py`. Includes multi-table support (targets, engagements, scan results, etc.).
* **Agent Core:** `agent/main_agent.py` orchestrates the hacking loop, leaning on AI planners.
* **Security Modules:** Found in `modules/`, utilizing tools like Nmap, Selenium, BeautifulSoup.

## Module Inventory
* **`ai_brain/`**: Interacts with local GGUF models (`nous-hermes-2-solar-10.7b`) via llama.cpp or falls back to simulated/mock responses.
* **`dashboard/`**: FastAPI dashboard (Deprecated in favor of `ui/`).
* **`database/`**: Robust SQLite interaction with schema definition on init.
* **`tests/`**: Includes tests for config, web automation, scanning, directory bruteforce, target discovery.

## Working/Broken Functionality
* **Working:** Core database creation, Web scraping via Selenium/BS4, Test suite (30 passing tests after dependency resolution), AI orchestration logic.
* **Partially Working:** Reporting (relies somewhat on mock data locally, needs DB hookup).
* **Missing:** Full NiceGUI implementations for modules, settings, proper DB linkage in some UI pages. Full implementation of Metasploit RPC in tests (stubbed).

## Security Defects & Severity
* **High Severity:** Continuous mode currently discovers targets and scans them without verifying strict authorization via the DB. SSRF risk in target parsing.
* **High Severity:** Subprocess calls in `modules/` potentially susceptible to argument injection if AI outputs arbitrary strings.

## Implementation Plan
1. Hook up strict DB authorization checks in `main.py` and `main_agent.py`.
2. Transition UI fully to NiceGUI and delete FastAPI dashboard.
3. Wire UI and Reporting to the real SQLite database findings.
