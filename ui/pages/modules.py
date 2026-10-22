from nicegui import ui
from ui.theme import frame
from database.database import DatabaseManager

@ui.page('/modules')
def modules_page():
    frame()
    db = DatabaseManager()

    with ui.column().classes('w-full max-w-6xl mx-auto p-6 gap-6'):
        ui.label('Security Modules').classes('text-3xl font-bold mb-4')

        # We'll need a way to select an engagement and a target first.
        import sqlite3
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, name FROM engagements WHERE status = "active"')
            engagements = {row[0]: row[1] for row in cursor.fetchall()}

        if not engagements:
            ui.label('You must create an active engagement first.').classes('text-red-500 font-bold')
            return

        with ui.card().classes('w-full p-4 mb-4'):
            ui.label('Launch Scan').classes('text-xl font-bold')

            selected_engagement = ui.select(engagements, label='Select Engagement').classes('w-full max-w-md')
            selected_target = ui.select({}, label='Select Target').classes('w-full max-w-md')

            def update_targets():
                if not selected_engagement.value:
                    return
                with sqlite3.connect(db.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT id, target FROM targets WHERE engagement_id = ? AND authorized = 1', (selected_engagement.value,))
                    targets = {row[0]: row[1] for row in cursor.fetchall()}
                selected_target.options = targets
                selected_target.value = None
                selected_target.update()

            selected_engagement.on_value_change(update_targets)

            modules = {
                'network_discovery': 'Network Discovery (Nmap)',
                'web_scanner': 'Web Security Assessment'
            }
            selected_module = ui.select(modules, label='Select Module').classes('w-full max-w-md')

            def launch_scan():
                if not selected_engagement.value or not selected_target.value or not selected_module.value:
                    ui.notify('Please select Engagement, Target, and Module.', type='warning')
                    return

                # Create job
                job_id = db.create_job(
                    engagement_id=selected_engagement.value,
                    target_id=selected_target.value,
                    module=selected_module.value,
                    input_data={}
                )
                ui.notify(f'Job {job_id} queued successfully.', type='positive')
                ui.navigate.to('/jobs')

            ui.button('Queue Scan', on_click=launch_scan, icon='play_arrow').classes('bg-green-600 mt-4')

        with ui.row().classes('w-full gap-6'):
            with ui.column().classes('card flex-1'):
                ui.label('Network Discovery').classes('text-xl font-bold mb-2')
                ui.label('Uses nmap to discover open ports and services on a target.').classes('text-gray-300')
                ui.label('Prerequisites: nmap installed').classes('text-sm text-gray-500 mt-2')

            with ui.column().classes('card flex-1'):
                ui.label('Web Assessment').classes('text-xl font-bold mb-2')
                ui.label('Basic web crawler and security checks for HTTP services.').classes('text-gray-300')
                ui.label('Prerequisites: requests, BeautifulSoup').classes('text-sm text-gray-500 mt-2')
