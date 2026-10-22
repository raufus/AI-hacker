from nicegui import ui
from ui.theme import frame

@ui.page('/assets')
def assets_page():
    frame()
    with ui.column().classes('w-full max-w-6xl mx-auto p-6 gap-6'):
        with ui.row().classes('w-full justify-between items-center mb-4'):
            ui.label('Assets & Scope Management').classes('text-3xl font-bold')
            ui.button('Add Asset', icon='add').classes('bg-blue-600')

        with ui.column().classes('card w-full'):
            ui.label('Authorized Assets').classes('text-xl font-bold mb-4')

            from database.database import DatabaseManager
            db = DatabaseManager()
            import sqlite3
            with sqlite3.connect(db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT t.target, t.type, e.name, t.authorized
                    FROM targets t LEFT JOIN engagements e ON t.engagement_id = e.id
                ''')
                db_assets = cursor.fetchall()

            columns = [
                {'name': 'target', 'label': 'Target / Asset', 'field': 'target', 'align': 'left'},
                {'name': 'type', 'label': 'Type', 'field': 'type', 'align': 'left'},
                {'name': 'engagement', 'label': 'Engagement', 'field': 'engagement', 'align': 'left'},
                {'name': 'status', 'label': 'Status', 'field': 'status', 'align': 'left'},
                {'name': 'actions', 'label': 'Actions', 'field': 'actions', 'align': 'center'}
            ]

            rows = [
                {'target': a[0], 'type': a[1], 'engagement': a[2] or 'Unassigned', 'status': 'Authorized' if a[3] else 'Pending'}
                for a in db_assets
            ]

            if not rows:
                ui.label('No assets currently configured.').classes('text-gray-500 italic')
            else:
                ui.table(columns=columns, rows=rows, row_key='target').classes('w-full')
