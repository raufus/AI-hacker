# Security Controls

1. **Target Authorization:** All targets must be explicitly defined and set as `authorized = 1` in the database.
2. **Scope Boundaries:** Subprocess scanners like Nmap and BeautifulSoup scrapers must validate domains/IPs strictly before interacting with networks.
3. **Prompt Injection:** Output from LLM modules must be rigorously parsed (e.g. strict JSON schema) and sanitized before triggering any action.
4. **Secrets Management:** Credentials, API keys, and sensitive tokens are injected via environment variables and never logged or serialized to the DB in plain text.
5. **Worker Isolation:** Job workers fetch inputs from the queue but operate independently. Output is parsed by adapters rather than arbitrary shell execution.