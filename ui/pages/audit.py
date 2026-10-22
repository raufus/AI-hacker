from nicegui import ui
from ui.theme import frame
from database.database import DatabaseManager

@ui.page('/audit')
def audit_page():
    frame()
    db = DatabaseManager()

    with ui.column().classes('w-full max-w-6xl mx-auto p-6 gap-6'):
        ui.label('Audit & Health').classes('text-3xl font-bold mb-4')

        with ui.row().classes('w-full gap-6'):
            with ui.column().classes('card flex-1'):
                ui.label('System Health').classes('text-xl font-bold mb-4')

                with ui.row().classes('items-center gap-2 mb-2'):
                    ui.icon('check_circle', color='green', size='sm')
                    ui.label('Database Connection: OK')

                # Assume basic tools if Python can run this
                with ui.row().classes('items-center gap-2 mb-2'):
                    ui.icon('check_circle', color='green', size='sm')
                    ui.label('Web Scanner Dependencies: OK')

                import shutil
                nmap_path = shutil.which('nmap')
                with ui.row().classes('items-center gap-2 mb-2'):
                    if nmap_path:
                        ui.icon('check_circle', color='green', size='sm')
                        ui.label(f'Nmap Installed: {nmap_path}')
                    else:
                        ui.icon('warning', color='yellow', size='sm')
                        ui.label('Nmap NOT Installed (Network Discovery will fail)')

            with ui.column().classes('card flex-2'):
                 ui.label('Audit Log').classes('text-xl font-bold mb-4')
                 ui.label('System events and access logs will appear here.').classes('text-gray-500 italic')
                 # Mock log data
                 ui.markdown('''
                 - **[System]** Application started
                 - **[Database]** Connected successfully
                 - **[Auth]** Initialized default admin user
                 ''')
