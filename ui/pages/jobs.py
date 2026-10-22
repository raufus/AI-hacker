from nicegui import ui
from ui.theme import frame
from database.database import DatabaseManager

@ui.page('/jobs')
def jobs_page():
    frame()
    db = DatabaseManager()

    with ui.column().classes('w-full max-w-6xl mx-auto p-6 gap-6'):
        ui.label('Jobs & Activity').classes('text-3xl font-bold mb-4')

        table_container = ui.column().classes('w-full')

        def update_table():
            table_container.clear()
            import sqlite3
            with sqlite3.connect(db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT j.id, e.name, t.target, j.module, j.status, j.created_at, j.updated_at
                    FROM jobs j
                    JOIN targets t ON j.target_id = t.id
                    LEFT JOIN engagements e ON j.engagement_id = e.id
                    ORDER BY j.created_at DESC
                ''')
                db_jobs = cursor.fetchall()

            columns = [
                {'name': 'id', 'label': 'Job ID', 'field': 'id'},
                {'name': 'engagement', 'label': 'Engagement', 'field': 'engagement'},
                {'name': 'target', 'label': 'Target', 'field': 'target'},
                {'name': 'module', 'label': 'Module', 'field': 'module'},
                {'name': 'status', 'label': 'Status', 'field': 'status'},
                {'name': 'created_at', 'label': 'Created', 'field': 'created_at'},
            ]

            rows = [
                 {'id': j[0], 'engagement': j[1] or 'None', 'target': j[2], 'module': j[3], 'status': j[4], 'created_at': j[5]}
                 for j in db_jobs
            ]

            with table_container:
                if not rows:
                     ui.label('No jobs found.').classes('text-gray-500 italic')
                else:
                     ui.table(columns=columns, rows=rows, row_key='id').classes('w-full')

        update_table()
        ui.timer(2.0, update_table) # Refresh table every 2 seconds
