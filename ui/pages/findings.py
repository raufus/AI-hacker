from nicegui import ui
from ui.theme import frame
import sqlite3
import json
from database.database import DatabaseManager

db = DatabaseManager()

@ui.page('/findings')
def findings_page():
    frame()
    with ui.column().classes('w-full max-w-6xl mx-auto p-6 gap-6'):
        with ui.row().classes('w-full justify-between items-center mb-4'):
            ui.label('Findings & Evidence').classes('text-3xl font-bold')

        with ui.column().classes('card w-full'):
            ui.label('Stored Vulnerabilities').classes('text-xl font-bold mb-4')

            with sqlite3.connect(db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT v.id, t.target, s.scan_type, v.severity, v.vulnerability, v.status, v.created_at
                    FROM vulnerabilities v
                    JOIN scan_results s ON v.scan_id = s.id
                    JOIN targets t ON s.target_id = t.id
                    ORDER BY v.created_at DESC
                ''')
                findings = cursor.fetchall()

            columns = [
                {'name': 'target', 'label': 'Target', 'field': 'target', 'align': 'left'},
                {'name': 'module', 'label': 'Module', 'field': 'module', 'align': 'left'},
                {'name': 'severity', 'label': 'Severity', 'field': 'severity', 'align': 'left'},
                {'name': 'name', 'label': 'Finding', 'field': 'name', 'align': 'left'},
                {'name': 'status', 'label': 'Status', 'field': 'status', 'align': 'left'},
                {'name': 'created', 'label': 'Created At', 'field': 'created', 'align': 'left'},
            ]

            rows = []
            for f in findings:
                rows.append({
                    'id': f[0],
                    'target': f[1],
                    'module': f[2],
                    'severity': f[3].upper(),
                    'name': f[4],
                    'status': f[5],
                    'created': f[6]
                })

            if not rows:
                ui.label('No findings recorded.').classes('text-gray-500 italic')
            else:
                ui.table(columns=columns, rows=rows, row_key='id').classes('w-full')
