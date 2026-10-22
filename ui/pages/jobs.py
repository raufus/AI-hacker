from nicegui import ui
from ui.theme import frame
import sqlite3
import json
from database.database import DatabaseManager

db = DatabaseManager()

@ui.page('/jobs')
def jobs_page():
    frame()
    with ui.column().classes('w-full max-w-6xl mx-auto p-6 gap-6'):
        with ui.row().classes('w-full justify-between items-center mb-4'):
            ui.label('Jobs & Activity').classes('text-3xl font-bold')
            ui.button('Refresh', icon='refresh', on_click=lambda: ui.navigate.reload()).classes('bg-gray-700')

        with ui.column().classes('card w-full'):
            ui.label('Job Execution Queue').classes('text-xl font-bold mb-4')

            with sqlite3.connect(db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT j.id, e.name, t.target, j.module, j.status, j.created_at, j.updated_at, j.error_message
                    FROM jobs j
                    JOIN targets t ON j.target_id = t.id
                    JOIN engagements e ON j.engagement_id = e.id
                    ORDER BY j.created_at DESC
                ''')
                jobs = cursor.fetchall()

            columns = [
                {'name': 'id', 'label': 'Job ID', 'field': 'id', 'align': 'left'},
                {'name': 'engagement', 'label': 'Engagement', 'field': 'engagement', 'align': 'left'},
                {'name': 'target', 'label': 'Target', 'field': 'target', 'align': 'left'},
                {'name': 'module', 'label': 'Module', 'field': 'module', 'align': 'left'},
                {'name': 'status', 'label': 'Status', 'field': 'status', 'align': 'left'},
                {'name': 'created', 'label': 'Created', 'field': 'created', 'align': 'left'},
            ]

            rows = []
            for j in jobs:
                # Add basic styling to status
                status = j[4]
                status_icon = '⏳ ' if status == 'pending' else '▶️ ' if status == 'running' else '✅ ' if status == 'completed' else '❌ '
                rows.append({
                    'id': j[0],
                    'engagement': j[1],
                    'target': j[2],
                    'module': j[3],
                    'status': f"{status_icon} {status.upper()}",
                    'created': j[5],
                })

            if not rows:
                ui.label('No jobs found.').classes('text-gray-500 italic')
            else:
                ui.table(columns=columns, rows=rows, row_key='id').classes('w-full')
