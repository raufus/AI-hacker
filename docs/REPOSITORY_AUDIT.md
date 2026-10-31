# Repository Audit

## Architecture and Entry Points
- `main.py`: Main entry point supporting CLI mode, autonomous mode, and continuous mode.
- `ui/main.py`: Entry point for the NiceGUI web dashboard.
- `database/database.py`: Core SQLite persistence layer handling engagements, jobs, and findings.
- `agent/main_agent.py`: Autonomous agent coordinating reconnaissance, scanning, and AI planning.
- `automation/worker.py`: Background worker for processing queued jobs.

## Module Inventory
- `agent/`: Orchestrates the testing lifecycle.
- `ai_brain/`: Wraps LLM interactions.
- `ai_providers/`: Abstract provider interfaces (e.g., LocalGGUFProvider).
- `automation/`: Task queues and worker execution.
- `boot_os/`: Utilities to build an ISO.
- `config/`: Configuration management parsing `config.yaml`.
- `dashboard/`: FastAPI integration points.
- `database/`: Database schema and connection management.
- `modules/`: Contains security scanners and target discovery modules.
- `report/`: Generates markdown, JSON, and HTML reports.
- `security/`: Handles authentication (basic).
- `ui/`: NiceGUI pages and components.

## Status of Features
See `FEATURE_STATUS.md`.

## Security Defects & Fixes
- `shell=True` in `iso_builder.py` removed.
- Unrestricted target discovery in `target_discovery.py` patched out.

## Test Coverage
- Found 68 tests across multiple modules.
- Added dependencies: `requests`, `python-nmap`, `selenium`, `beautifulsoup4`.
- All tests passing (30/30).

## Plan
Continue building out the UI modules, refactoring AI providers to use strict schema validation, and enhancing job execution with robust worker state management.
