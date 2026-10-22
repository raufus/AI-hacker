from nicegui import ui
from ui.theme import frame
import platform
import os
from database.database import DatabaseManager

@ui.page('/audit')
def audit_health_page():
    frame()
    with ui.column().classes('w-full max-w-6xl mx-auto p-6 gap-6'):
        ui.label('Audit & Health').classes('text-3xl font-bold mb-4')

        with ui.card().classes('w-full'):
            ui.label('System Information').classes('text-xl font-bold mb-4')

            with ui.row().classes('gap-4 mb-2'):
                ui.label('OS:').classes('font-bold w-32')
                ui.label(platform.system() + ' ' + platform.release())

            with ui.row().classes('gap-4 mb-2'):
                ui.label('Python Version:').classes('font-bold w-32')
                ui.label(platform.python_version())

        with ui.card().classes('w-full mt-6'):
            ui.label('Service Dependencies').classes('text-xl font-bold mb-4')

            def check_db():
                db = DatabaseManager()
                return "ONLINE" if os.path.exists(db.db_path) else "OFFLINE"

            with ui.row().classes('items-center gap-4 mb-2'):
                ui.label('SQLite Database:').classes('font-bold w-32')
                status = check_db()
                ui.label(status).classes('text-green-500 font-bold' if status == 'ONLINE' else 'text-red-500 font-bold')

            def check_command(cmd):
                import shutil
                return "INSTALLED" if shutil.which(cmd) else "NOT FOUND"

            for tool in ['nmap', 'sqlmap', 'hydra']:
                with ui.row().classes('items-center gap-4 mb-2'):
                    ui.label(f'{tool.capitalize()}:').classes('font-bold w-32')
                    status = check_command(tool)
                    ui.label(status).classes('text-green-500 font-bold' if status == 'INSTALLED' else 'text-red-500 font-bold')
