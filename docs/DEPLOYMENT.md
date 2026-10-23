# Deployment Guide

1. Ensure Python 3.12+ is installed.
2. Install dependencies via `pip install -r requirements.txt`. (Note: Some environments may need selective installation if heavy ML libs are problematic).
3. Set environment variables (e.g. `OPENAI_API_KEY`) using `.env` or system profiles.
4. Run migrations/initialization using `python3 main.py --install-tools`.
5. Start the frontend via `python3 ui/main.py`.
6. Alternatively, start the standalone dashboard via `python3 dashboard/dashboard.py`.
7. For continuous scanning, launch the background agent with `python3 main.py --continuous`.