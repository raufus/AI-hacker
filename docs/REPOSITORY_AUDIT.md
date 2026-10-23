# Repository Audit

## Architecture and Entry Points
- Modular AI penetration testing OS.
- Core entry points: `main.py` (CLI), `ui/main.py` (NiceGUI Frontend), `dashboard/dashboard.py` (FastAPI dashboard), `agent/main_agent.py` (AI engine).

## Module-by-module Inventory
- `agent/`, `ai/`, `ai_brain/`, `ai_providers/`: AI logic and routing. Local Llama GGUF models are supported.
- `api/`, `dashboard/`: FastAPI web interfaces and REST handlers.
- `automation/`: Job queue system and workers.
- `boot_os/`, `browser_bot/`: System components and selenium bots.
- `config/`: Configuration files and yaml manager.
- `database/`: SQLite database initialization and models for scan tracking.
- `modules/`, `security/`, `templates/`, `utils/`: Scanning modules (nmap, web_scanner, etc.), auth features.

## Functionality Status
- **Working:** Configuration manager, Basic scan launching via nmap.
- **Partially Working:** UI frontend runs but is lacking some connected features, Database tracking.
- **Broken/Missing:** Missing templates (like `dashboard.html`), broken JSON structures in mock data, missing strict bounds on scanning targets.
- **Unverified:** Heavy ML integrations.

## Dependency and Runtime Requirements
- Python 3.12+
- `fastapi`, `nicegui`, `uvicorn`, `python-nmap`, `beautifulsoup4`, `selenium`, `scapy`.
- External tools: `nmap`.

## Existing UI Status
- Developed in NiceGUI (`ui/main.py`). The UI supports basic dashboarding and views for Engagements, Findings, and Job Tracking.

## Security Defects
- **Severity: High** - Subprocess invocations may allow shell injection if arguments are constructed poorly.
- **Severity: Medium** - Secrets can be easily leaked in logging if not sanitized. Target validation is rudimentary.

## Test Coverage
- `pytest` baseline is currently 30 tests. All 30 tests pass.

## Reuse/Refactor/Replace Plan
- **Reuse:** The NiceGUI frontend layout, test suite, and module adapters.
- **Refactor:** `database/database.py` to handle async operations better and strictly enforce target scopes.
- **Replace:** Mock JSON generation in dashboard, use real database instead.

## Implementation Plan
1. Fix core crashes in existing apps (`dashboard.py`).
2. Implement strict scope boundaries before scanning tools run.
3. Enhance the NiceGUI dashboard.
4. Ensure all test cases pass.