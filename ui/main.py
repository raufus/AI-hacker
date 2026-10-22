from nicegui import ui
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import pages to register their routes
from nicegui import ui as nice_ui

import ui.pages.overview
import ui.pages.assets
import ui.pages.engagements
import ui.pages.security_modules
import ui.pages.jobs
import ui.pages.findings
import ui.pages.reports
import ui.pages.ai_control
import ui.pages.audit

def run_ui():
    """Starts the NiceGUI application."""
    nice_ui.run(title='Devnox AI Hacker OS', dark=True, port=8080, reload=False, show=False)

if __name__ in {"__main__", "__mp_main__"}:
    run_ui()
