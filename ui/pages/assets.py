from nicegui import ui
from ui.theme import frame

@ui.page('/assets')
def assets_page():
    frame()
    with ui.column().classes('w-full max-w-6xl mx-auto p-6 gap-6'):
        from database.database import DatabaseManager
        db = DatabaseManager()
        import sqlite3

        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, name FROM engagements WHERE status = "active"')
            engagements = {row[0]: row[1] for row in cursor.fetchall()}

        with ui.row().classes('w-full justify-between items-center mb-4'):
            ui.label('Assets & Scope Management').classes('text-3xl font-bold')
            ui.button('Add Asset', icon='add', on_click=lambda: add_dialog.open()).classes('bg-blue-600')

        with ui.column().classes('card w-full'):
            ui.label('Authorized Assets').classes('text-xl font-bold mb-4')

            with sqlite3.connect(db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT t.id, t.target, t.type, e.name, t.authorized
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
                {'target': a[1], 'type': a[2], 'engagement': a[3] or 'Unassigned', 'status': 'Authorized' if a[4] else 'Pending'}
                for a in db_assets
            ]

            if not rows:
                ui.label('No assets currently configured.').classes('text-gray-500 italic')
            else:
                ui.table(columns=columns, rows=rows, row_key='target').classes('w-full')

        # Add Asset Dialog
        with ui.dialog() as add_dialog, ui.card().classes('w-96'):
            ui.label('Add New Asset').classes('text-xl font-bold')
            target_input = ui.input('Target (IP, Domain, URL)').classes('w-full')
            type_select = ui.select(['IP Address', 'Domain', 'URL', 'CIDR'], value='Domain', label='Type').classes('w-full')

            eng_select = ui.select(engagements, label='Engagement').classes('w-full')
            auth_checkbox = ui.checkbox('I explicitly authorize scanning on this target').classes('w-full')

            def save_asset():
                if not target_input.value or not eng_select.value:
                    ui.notify('Target and Engagement are required', type='negative')
                    return
                # Enforce server-side security checks implicitly via the database API design
                db.add_target(
                    engagement_id=eng_select.value,
                    target=target_input.value.strip(),
                    target_type=type_select.value,
                    authorized=auth_checkbox.value
                )
                ui.notify('Asset added successfully', type='positive')
                add_dialog.close()
                ui.navigate.reload()

            with ui.row().classes('w-full justify-end mt-4'):
                ui.button('Cancel', on_click=add_dialog.close).classes('bg-gray-500')
                ui.button('Add Asset', on_click=save_asset).classes('bg-blue-600')
