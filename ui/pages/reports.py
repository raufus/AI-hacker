from nicegui import ui
from ui.theme import frame
from database.database import DatabaseManager
import json

@ui.page('/reports')
def reports_page():
    frame()
    db = DatabaseManager()

    with ui.column().classes('w-full max-w-6xl mx-auto p-6 gap-6'):
        ui.label('Reports Generation').classes('text-3xl font-bold mb-4')

        import sqlite3
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT target FROM targets WHERE authorized = 1')
            targets = [row[0] for row in cursor.fetchall()]

        if not targets:
             ui.label('No authorized targets available to generate reports for.').classes('text-red-500 font-bold')
             return

        with ui.card().classes('w-full'):
            target_select = ui.select(targets, label='Select Target for Report').classes('w-full max-w-md')

            def download_json():
                if not target_select.value:
                    ui.notify('Select a target first', type='warning')
                    return
                data = db.export_data(target_select.value, format='json')
                ui.download(data.encode('utf-8'), f'report_{target_select.value}.json')

            def download_markdown():
                 if not target_select.value:
                    ui.notify('Select a target first', type='warning')
                    return
                 data_json = db.export_data(target_select.value, format='json')
                 data = json.loads(data_json)

                 md = f"# Penetration Test Report: {target_select.value}\n\n"
                 md += "## Statistics\n"
                 md += f"- Total Scans: {data['stats']['total_scans']}\n"
                 md += f"- Critical Vulnerabilities: {data['stats']['vulnerabilities']['critical']}\n"
                 md += f"- High Vulnerabilities: {data['stats']['vulnerabilities']['high']}\n\n"

                 md += "## Vulnerabilities\n"
                 for v in data['vulnerabilities']:
                     md += f"### {v['vulnerability']} ({v['severity'].upper()})\n"
                     md += f"Status: {v['status']}\n\n"

                 ui.download(md.encode('utf-8'), f'report_{target_select.value}.md')

            def download_html():
                 if not target_select.value:
                    ui.notify('Select a target first', type='warning')
                    return
                 data_json = db.export_data(target_select.value, format='json')
                 data = json.loads(data_json)

                 import html
                 escaped_target = html.escape(target_select.value)

                 html_out = f"<html><head><title>Report: {escaped_target}</title></head><body>"
                 html_out += f"<h1>Penetration Test Report: {escaped_target}</h1>"
                 html_out += "<h2>Statistics</h2><ul>"
                 html_out += f"<li>Total Scans: {data['stats']['total_scans']}</li>"
                 html_out += f"<li>Critical Vulnerabilities: {data['stats']['vulnerabilities']['critical']}</li>"
                 html_out += f"<li>High Vulnerabilities: {data['stats']['vulnerabilities']['high']}</li></ul>"

                 html_out += "<h2>Vulnerabilities</h2>"
                 for v in data['vulnerabilities']:
                     html_out += f"<h3>{html.escape(v['vulnerability'])} ({html.escape(v['severity'].upper())})</h3>"
                     html_out += f"<p>Status: {html.escape(v['status'])}</p>"

                 html_out += "</body></html>"

                 ui.download(html_out.encode('utf-8'), f'report_{target_select.value}.html')

            with ui.row().classes('mt-4 gap-4'):
                ui.button('Download JSON', on_click=download_json).classes('bg-blue-600')
                ui.button('Download Markdown', on_click=download_markdown).classes('bg-green-600')
                ui.button('Download HTML', on_click=download_html).classes('bg-purple-600')
