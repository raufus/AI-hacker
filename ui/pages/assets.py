from nicegui import ui
from ui.theme import frame

@ui.page('/assets')
def assets_page():
    frame()
    with ui.column().classes('w-full max-w-6xl mx-auto p-6 gap-6'):
        from database.database import DatabaseManager
        db = DatabaseManager()
        import sqlite3

        with ui.row().classes('w-full justify-between items-center mb-4'):
            ui.label('Assets & Scope Management').classes('text-3xl font-bold')

            def open_add_asset_dialog():
                add_asset_dialog.open()

            ui.button('Add Asset', icon='add', on_click=open_add_asset_dialog).classes('bg-blue-600')

        with ui.dialog() as add_asset_dialog, ui.card():
            ui.label('Add Target Asset').classes('text-xl font-bold')

            with sqlite3.connect(db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id, name FROM engagements WHERE status = "active"')
                engagements = {row[0]: row[1] for row in cursor.fetchall()}

            target_input = ui.input('Target (IP/Hostname/URL)').classes('w-full')
            type_select = ui.select({'ip': 'IP Address', 'hostname': 'Hostname', 'url': 'URL'}, label='Target Type', value='ip').classes('w-full')
            engagement_select = ui.select(engagements, label='Engagement').classes('w-full')
            authorize_checkbox = ui.checkbox('Explicitly Authorize Scanning', value=False)

            def add_asset():
                if not target_input.value or not engagement_select.value:
                    ui.notify('Target and Engagement are required', type='negative')
                    return
                db.add_target(
                    engagement_id=engagement_select.value,
                    target=target_input.value,
                    target_type=type_select.value,
                    authorized=authorize_checkbox.value
                )
                ui.notify(f'Asset {target_input.value} added.', type='positive')
                add_asset_dialog.close()
                ui.navigate.to('/assets')

            with ui.row().classes('w-full justify-end mt-4'):
                ui.button('Cancel', on_click=add_asset_dialog.close).classes('bg-gray-500')
                ui.button('Add', on_click=add_asset).classes('bg-blue-600')

        with ui.column().classes('card w-full'):
            ui.label('Authorized Assets').classes('text-xl font-bold mb-4')

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
