# Threat Model

1. **Malicious LLM Directives:** Untrusted text parsed from web targets could poison LLM prompts.
   - *Mitigation:* Strict input length bounding and JSON extraction parsers to prevent LLM actions from executing arbitrary code.
2. **SSRF (Server-Side Request Forgery):** Scanners could be tricked into scanning internal metadata endpoints (e.g. AWS 169.254.169.254).
   - *Mitigation:* Explicit internal IP denylists and strict scope validation before any `requests` or `socket` action.
3. **Command Injection:** Target URLs could include shell metacharacters passed to `nmap` or other CLI tools.
   - *Mitigation:* We use array-based `subprocess.run(["nmap", target])` instead of shell interpolation.
4. **Data Exfiltration:** Extracted vulnerability logs could leak PII.
   - *Mitigation:* UI redaction layers and restricted DB access for multi-tenant users.