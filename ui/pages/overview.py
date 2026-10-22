from nicegui import ui
from ui.theme import frame

@ui.page('/')
def overview_page():
    frame()
    with ui.column().classes('w-full max-w-6xl mx-auto p-6 gap-6'):
        ui.label('Dashboard Overview').classes('text-3xl font-bold mb-4')

        from database.database import DatabaseManager
        db = DatabaseManager()

        # Load actual stats from the database
        with open(db.db_path, 'r', encoding='utf-8') as f:
            pass # Just ensuring file check works, db logic is done by sqlite3

        import sqlite3
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM engagements')
            active_engagements = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM targets')
            assets_in_scope = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM vulnerabilities')
            total_findings = cursor.fetchone()[0]

            # Aggregate findings by severity
            cursor.execute('SELECT severity, COUNT(*) FROM vulnerabilities GROUP BY severity')
            severity_counts = dict(cursor.fetchall())

            # Fetch recent jobs
            cursor.execute('''
                SELECT j.id, t.target, j.module, j.status
                FROM jobs j JOIN targets t ON j.target_id = t.id
                ORDER BY j.created_at DESC LIMIT 5
            ''')
            recent_jobs = cursor.fetchall()

        # Summary Cards
        with ui.row().classes('w-full gap-6'):
            with ui.column().classes('card flex-1 items-center'):
                ui.label('Active Engagements').classes('text-gray-400 text-sm uppercase tracking-wide')
                ui.label(str(active_engagements)).classes('metric-value')
            with ui.column().classes('card flex-1 items-center'):
                ui.label('Total Findings').classes('text-gray-400 text-sm uppercase tracking-wide')
                ui.label(str(total_findings)).classes(f'metric-value {"text-red-500" if total_findings > 0 else "text-green-500"}')
            with ui.column().classes('card flex-1 items-center'):
                ui.label('Assets in Scope').classes('text-gray-400 text-sm uppercase tracking-wide')
                ui.label(str(assets_in_scope)).classes('metric-value')
            with ui.column().classes('card flex-1 items-center'):
                ui.label('AI Engine Health').classes('text-gray-400 text-sm uppercase tracking-wide')
                # AI Engine check would go here, hardcoded as ONLINE for now since we don't have a live AI status yet
                ui.label('ONLINE').classes('metric-value text-green-500')

        # Recent Activity & Findings Distribution
        with ui.row().classes('w-full gap-6 mt-6'):
            with ui.column().classes('card flex-2'):
                ui.label('Recent Scan Activity').classes('text-xl font-bold mb-4')
                columns = [
                    {'name': 'job', 'label': 'Job ID', 'field': 'job'},
                    {'name': 'target', 'label': 'Target', 'field': 'target'},
                    {'name': 'module', 'label': 'Module', 'field': 'module'},
                    {'name': 'status', 'label': 'Status', 'field': 'status'},
                ]
                rows = [{'job': j[0], 'target': j[1], 'module': j[2], 'status': j[3]} for j in recent_jobs]
                if not rows:
                    ui.label('No recent jobs.').classes('text-gray-500 italic')
                else:
                    ui.table(columns=columns, rows=rows, row_key='job').classes('w-full bg-transparent')

            with ui.column().classes('card flex-1'):
                ui.label('Findings by Severity').classes('text-xl font-bold mb-4')

                if total_findings == 0:
                     ui.label('No findings recorded.').classes('text-gray-500 italic')
                else:
                    ui.echart({
                        'tooltip': {'trigger': 'item'},
                        'series': [
                            {
                                'name': 'Severity',
                                'type': 'pie',
                                'radius': ['40%', '70%'],
                                'itemStyle': {
                                    'borderRadius': 10,
                                    'borderColor': '#1E293B',
                                    'borderWidth': 2
                                },
                                'data': [
                                    {'value': severity_counts.get('critical', 0), 'name': 'Critical', 'itemStyle': {'color': '#EF4444'}},
                                    {'value': severity_counts.get('high', 0), 'name': 'High', 'itemStyle': {'color': '#F97316'}},
                                    {'value': severity_counts.get('medium', 0), 'name': 'Medium', 'itemStyle': {'color': '#EAB308'}},
                                    {'value': severity_counts.get('low', 0), 'name': 'Low', 'itemStyle': {'color': '#3B82F6'}}
                                ]
                            }
                        ]
                    }).classes('w-full h-64')
