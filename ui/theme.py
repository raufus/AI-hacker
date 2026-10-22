from nicegui import ui

def apply_theme():
    """Applies the default Devnox AI Hacker OS dark theme."""
    ui.colors(primary='#1E40AF', secondary='#9333EA', accent='#F43F5E',
              dark='#111827', positive='#22C55E', negative='#EF4444',
              info='#3B82F6', warning='#F59E0B')

    ui.add_head_html('''
        <style>
            body {
                background-color: #0F172A;
                color: #F8FAFC;
                font-family: 'Inter', sans-serif;
            }
            .nav-link {
                color: #CBD5E1;
                text-decoration: none;
                padding: 10px;
                border-radius: 5px;
                display: block;
                margin-bottom: 5px;
                transition: background-color 0.2s;
            }
            .nav-link:hover {
                background-color: #1E293B;
                color: #FFFFFF;
            }
            .card {
                background-color: #1E293B;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            }
            .metric-value {
                font-size: 2rem;
                font-weight: bold;
                color: #3B82F6;
            }
        </style>
    ''')

def frame():
    """Creates the application shell (header and sidebar)."""
    apply_theme()

    with ui.header(elevated=True).style('background-color: #1E293B').classes('items-center justify-between'):
        with ui.row().classes('items-center gap-4'):
            ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=white')
            ui.label('Devnox AI Hacker OS').classes('text-xl font-bold tracking-wider text-white')
        with ui.row().classes('items-center gap-4'):
            ui.icon('account_circle', size='md', color='white')

    with ui.left_drawer(elevated=True).style('background-color: #0F172A; border-right: 1px solid #1E293B') as left_drawer:
        with ui.column().classes('w-full p-4'):
            ui.link('Dashboard Overview', '/').classes('nav-link')
            ui.link('Assets & Scope', '/assets').classes('nav-link')
            ui.link('Engagements & Scans', '/engagements').classes('nav-link')
            ui.link('AI Control Center', '/ai').classes('nav-link')
            ui.link('Security Modules', '/modules').classes('nav-link')
            ui.link('Findings & Evidence', '/findings').classes('nav-link')
            ui.link('Reports', '/reports').classes('nav-link')
            ui.link('Audit & Health', '/audit').classes('nav-link')
