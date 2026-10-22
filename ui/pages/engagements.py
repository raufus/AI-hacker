from nicegui import ui
from ui.theme import frame
import sqlite3
from database.database import DatabaseManager

db = DatabaseManager()

@ui.page('/engagements')
def engagements_page():
    frame()
    with ui.column().classes('w-full max-w-6xl mx-auto p-6 gap-6'):
        with ui.row().classes('w-full justify-between items-center mb-4'):
            ui.label('Engagements').classes('text-3xl font-bold')
            ui.button('New Engagement', icon='add', on_click=lambda: add_dialog.open()).classes('bg-blue-600')

        with ui.column().classes('card w-full'):
            ui.label('Active Engagements').classes('text-xl font-bold mb-4')

            with sqlite3.connect(db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id, name, description, status, start_date, created_at FROM engagements ORDER BY created_at DESC')
                db_engs = cursor.fetchall()

            columns = [
                {'name': 'id', 'label': 'ID', 'field': 'id', 'align': 'left'},
                {'name': 'name', 'label': 'Name', 'field': 'name', 'align': 'left'},
                {'name': 'status', 'label': 'Status', 'field': 'status', 'align': 'left'},
                {'name': 'created', 'label': 'Created', 'field': 'created', 'align': 'left'},
            ]

            rows = [
                {'id': e[0], 'name': e[1], 'status': e[3], 'created': e[5]}
                for e in db_engs
            ]

            if not rows:
                ui.label('No engagements found.').classes('text-gray-500 italic')
            else:
                ui.table(columns=columns, rows=rows, row_key='id').classes('w-full')

        # Add Engagement Dialog
        with ui.dialog() as add_dialog, ui.card().classes('w-96'):
            ui.label('Create New Engagement').classes('text-xl font-bold')
            name_input = ui.input('Engagement Name').classes('w-full')
            desc_input = ui.textarea('Description').classes('w-full')

            def save_engagement():
                if name_input.value:
                    db.create_engagement(name_input.value, desc_input.value)
                    ui.notify('Engagement created successfully', type='positive')
                    add_dialog.close()
                    ui.navigate.reload()
                else:
                    ui.notify('Name is required', type='negative')

            with ui.row().classes('w-full justify-end mt-4'):
                ui.button('Cancel', on_click=add_dialog.close).classes('bg-gray-500')
                ui.button('Create', on_click=save_engagement).classes('bg-blue-600')
