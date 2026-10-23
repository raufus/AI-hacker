# Testing Guidelines

- **Unit Tests:** Run all Python tests using `PYTHONPATH=. python3 -m pytest tests/`
- **Integration Tests:** Use intentionally vulnerable lab targets (e.g. `localhost:8080`) instead of scanning uncontrolled internet assets.
- **Coverage:** Aim to cover policy validation, task state transitions, model routing, and scope rejection.