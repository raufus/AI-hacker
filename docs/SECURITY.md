# Devnox AI Hacker OS - Security Model

## Threat Model and Boundaries
This software is intended **strictly for authorized penetration testing**. To prevent runaway execution or unauthorized testing, strict bounds have been built in:

* **Scope Authorization:** Every scan execution must verify that its target exists in the `targets` table with `authorized = True`. The `discover_targets()` and `run_autonomous_operation()` workflows abort immediately if a target fails this check.
* **Isolated Tools:** The AI agent may suggest plans and paths, but it *cannot* arbitrarily invoke shell scripts. It must pass typed inputs to explicit tool adapters in `modules/`.
* **Subprocess Safety:** Adapters running tools like `nmap` invoke them using list structures (e.g. `subprocess.run(["nmap", target])`) rather than shell interpolation, mitigating argument injection.

## Secret Management
Settings and credentials (like Metasploit RPC tokens) are retrieved dynamically through `config/config_manager.py` and are not stored in logs, UI output, or source code.
