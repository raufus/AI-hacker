# Agents Protocol

- AI integrations must inherit from the `AIProvider` base class.
- Verify that `requirements.txt` installs properly in isolated environments.
- Always execute safe subprocesses without shell=True to avoid injection risks.
- `database/database.py` operations must be synchronous or explicitly managed via transactions to avoid race conditions.