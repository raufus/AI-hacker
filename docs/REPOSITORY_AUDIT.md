# Repository Audit

## Architecture & Entry Points
The application uses a modular AI-powered penetration testing architecture:
- `main.py`: The main entry point supporting continuous, autonomous, and manual execution modes.
- `agent/main_agent.py`: Houses `AutonomousAgent` representing the autonomous loop (observe-orient-decide-act) relying on the `AIPlanner`.
- `ui/main.py`: The UI entry point utilizing NiceGUI on port 8080.

## Module-by-module Inventory
- `agent/`: Orchestrates testing lifecycle (`AutonomousAgent`).
- `ai/`, `ai_brain/`: Contains the logic for analyzing and planning (via local GGUF models or simulated engines).
- `ai_providers/`: Clean object-oriented wrappers mapping models (like `LocalGGUFProvider`) against a generic `AIProvider` base class.
- `automation/`: Handlers for asynchronous job polling and execution (`Worker`).
- `config/`: Configuration parsing and settings models.
- `database/`: Central SQLite `DatabaseManager` providing transactional safety, schema lifecycle, and findings storage.
- `modules/`: Individual capabilities (e.g., Nikto/Nuclei scanning, Metasploit RPC connections).
- `report/`: Module exporting vulnerabilities into final HTML/JSON/Markdown documentation.
- `ui/`: Full NiceGUI implementation with pages for jobs, engagements, and findings.

## Dependency Status
The system uses Python 3.12 and dependencies specified in `requirements.txt`. Extensive integrations exist for Nmap, Metasploit, Nikto, and SQLMap which must be locally accessible or configured safely.

## Testing and Verification Baseline
Current execution verifies `PYTHONPATH=. python3 -m pytest tests/` runs successfully with SQLite passing and base component logic functioning across ~30 tests.

## Action Plan
1. Refactor autonomous execution modes to strictly deny unbounded target evaluation.
2. Restrict process execution inside `modules` against arbitrary shell interpolation.
3. Apply rigorous schema querying throughout the UI and Reporting capabilities.
