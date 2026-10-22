from nicegui import ui
from ui.theme import frame
import os
import sqlite3
from report.reporter import SecurityReporter
from database.database import DatabaseManager

db = DatabaseManager()

@ui.page('/reports')
def reports_page():
    frame()
    with ui.column().classes('w-full max-w-6xl mx-auto p-6 gap-6'):
        ui.label('Report Generation').classes('text-3xl font-bold mb-4')

        with ui.card().classes('w-full'):
            ui.label('Generate Report from Target').classes('text-xl font-bold mb-4')

            with sqlite3.connect(db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT target FROM targets WHERE authorized = 1')
                targets = [r[0] for r in cursor.fetchall()]

            if not targets:
                ui.label('No authorized targets found with scan data.').classes('text-warning')
                return

            target_select = ui.select(targets, label='Select Target').classes('w-full max-w-md')

            def generate_report():
                if not target_select.value:
                    ui.notify('Please select a target', type='negative')
                    return

                target = target_select.value
                reporter = SecurityReporter()
                reporter.set_target(target)

                # Load vulnerabilities for this target into reporter
                with sqlite3.connect(db.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT v.details
                        FROM vulnerabilities v
                        JOIN scan_results s ON v.scan_id = s.id
                        JOIN targets t ON s.target_id = t.id
                        WHERE t.target = ?
                    ''', (target,))
                    vulns = cursor.fetchall()
                    import json
                    for v in vulns:
                        # v.details is stored as json dumped text
                        reporter.add_vulnerability(json.loads(v[0]))

                # Generate Markdown and HTML
                md_file = reporter.generate_markdown_report()
                html_file = reporter.generate_html_report()
                ui.notify(f'Reports generated: {md_file}, {html_file}', type='positive')
                ui.navigate.reload()

            ui.button('Generate', on_click=generate_report).classes('mt-4 bg-blue-600')

        with ui.card().classes('w-full mt-6'):
            ui.label('Available Reports').classes('text-xl font-bold mb-4')
            reports_dir = 'reports'
            if os.path.exists(reports_dir):
                files = os.listdir(reports_dir)
                if files:
                    for f in files:
                        ui.label(f).classes('text-gray-300')
                else:
                    ui.label('No reports generated yet.').classes('text-gray-500 italic')
            else:
                ui.label('Reports directory not found.').classes('text-gray-500 italic')
