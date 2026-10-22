from nicegui import ui
from ui.theme import frame
from database.database import DatabaseManager

@ui.page('/findings')
def findings_page():
    frame()
    db = DatabaseManager()

    with ui.column().classes('w-full max-w-6xl mx-auto p-6 gap-6'):
        ui.label('Findings & Vulnerabilities').classes('text-3xl font-bold mb-4')

        import sqlite3
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT v.id, t.target, v.vulnerability, v.severity, v.status, v.created_at
                FROM vulnerabilities v
                JOIN scan_results s ON v.scan_id = s.id
                JOIN targets t ON s.target_id = t.id
                ORDER BY
                    CASE severity
                        WHEN 'critical' THEN 1
                        WHEN 'high' THEN 2
                        WHEN 'medium' THEN 3
                        WHEN 'low' THEN 4
                        ELSE 5
                    END, v.created_at DESC
            ''')
            findings = cursor.fetchall()

        columns = [
            {'name': 'id', 'label': 'ID', 'field': 'id'},
            {'name': 'target', 'label': 'Target', 'field': 'target'},
            {'name': 'vulnerability', 'label': 'Vulnerability', 'field': 'vulnerability'},
            {'name': 'severity', 'label': 'Severity', 'field': 'severity'},
            {'name': 'status', 'label': 'Status', 'field': 'status'},
            {'name': 'created_at', 'label': 'Date', 'field': 'created_at'},
        ]

        rows = [
             {'id': f[0], 'target': f[1], 'vulnerability': f[2], 'severity': f[3], 'status': f[4], 'created_at': f[5]}
             for f in findings
        ]

        if not rows:
             ui.label('No vulnerabilities found yet.').classes('text-gray-500 italic')
        else:
             ui.table(columns=columns, rows=rows, row_key='id').classes('w-full')
