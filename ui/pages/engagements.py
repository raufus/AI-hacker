from nicegui import ui
from ui.theme import frame
from database.database import DatabaseManager

@ui.page('/engagements')
def engagements_page():
    frame()
    db = DatabaseManager()

    with ui.column().classes('w-full max-w-6xl mx-auto p-6 gap-6'):
        with ui.row().classes('w-full justify-between items-center mb-4'):
            ui.label('Engagements Management').classes('text-3xl font-bold')

            def open_new_engagement_dialog():
                new_engagement_dialog.open()

            ui.button('New Engagement', icon='add', on_click=open_new_engagement_dialog).classes('bg-blue-600')

        with ui.dialog() as new_engagement_dialog, ui.card():
            ui.label('Create New Engagement').classes('text-xl font-bold')
            name_input = ui.input('Engagement Name').classes('w-full')
            desc_input = ui.textarea('Description').classes('w-full')

            def create_engagement():
                if name_input.value:
                    db.create_engagement(name=name_input.value, description=desc_input.value or "")
                    ui.notify(f'Engagement {name_input.value} created.', type='positive')
                    new_engagement_dialog.close()
                    ui.navigate.to('/engagements')
                else:
                    ui.notify('Name is required', type='negative')

            with ui.row().classes('w-full justify-end mt-4'):
                ui.button('Cancel', on_click=new_engagement_dialog.close).classes('bg-gray-500')
                ui.button('Create', on_click=create_engagement).classes('bg-blue-600')

        with ui.column().classes('card w-full'):
            ui.label('Active Engagements').classes('text-xl font-bold mb-4')

            import sqlite3
            with sqlite3.connect(db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id, name, description, status, created_at FROM engagements ORDER BY created_at DESC')
                db_engagements = cursor.fetchall()

            columns = [
                {'name': 'id', 'label': 'ID', 'field': 'id', 'align': 'left'},
                {'name': 'name', 'label': 'Name', 'field': 'name', 'align': 'left'},
                {'name': 'description', 'label': 'Description', 'field': 'description', 'align': 'left'},
                {'name': 'status', 'label': 'Status', 'field': 'status', 'align': 'left'},
                {'name': 'created_at', 'label': 'Created At', 'field': 'created_at', 'align': 'left'},
            ]

            rows = [
                {'id': e[0], 'name': e[1], 'description': e[2], 'status': e[3], 'created_at': e[4]}
                for e in db_engagements
            ]

            if not rows:
                ui.label('No active engagements.').classes('text-gray-500 italic')
            else:
                ui.table(columns=columns, rows=rows, row_key='id').classes('w-full')
