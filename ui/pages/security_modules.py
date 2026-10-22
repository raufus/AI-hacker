from nicegui import ui
from ui.theme import frame
import sqlite3
import json
from database.database import DatabaseManager

db = DatabaseManager()

@ui.page('/modules')
def security_modules_page():
    frame()
    with ui.column().classes('w-full max-w-6xl mx-auto p-6 gap-6'):
        ui.label('Security Modules & Execution').classes('text-3xl font-bold mb-4')

        # Load engagements for dropdown
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, name FROM engagements WHERE status = "active"')
            engagements = {row[0]: row[1] for row in cursor.fetchall()}

            cursor.execute('SELECT id, target, engagement_id FROM targets WHERE authorized = 1')
            targets = cursor.fetchall()

        if not engagements or not targets:
            ui.label('You must have at least one active engagement and authorized target to execute modules.').classes('text-warning')
            return

        target_options = {t[0]: f"{t[1]} (Eng: {engagements.get(t[2], 'Unknown')})" for t in targets}

        # Module Execution Form
        with ui.card().classes('w-full'):
            ui.label('Launch Scan').classes('text-xl font-bold mb-4')

            with ui.row().classes('w-full gap-4'):
                target_select = ui.select(target_options, label='Select Target').classes('flex-1')
                module_select = ui.select({
                    'Network Scanner': 'Network Scanner (Nmap)',
                    'Web Scanner': 'Web Scanner (SQLMap/Forms)',
                    'Vulnerability Scanner': 'Vulnerability Scanner (Nikto/Nuclei)'
                }, label='Select Module').classes('flex-1')

            def launch_job():
                if not target_select.value or not module_select.value:
                    ui.notify('Target and Module are required.', type='negative')
                    return

                target_id = target_select.value
                # find engagement id for target
                eng_id = next(t[2] for t in targets if t[0] == target_id)

                db.create_job(eng_id, target_id, module_select.value)
                ui.notify(f'Job queued for {module_select.value}.', type='positive')
                ui.navigate.to('/jobs')

            ui.button('Queue Scan Job', on_click=launch_job).classes('mt-4 bg-blue-600 w-full')
