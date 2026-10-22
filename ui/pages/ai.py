from nicegui import ui
from ui.theme import frame
import os

@ui.page('/ai')
def ai_page():
    frame()
    with ui.column().classes('w-full max-w-6xl mx-auto p-6 gap-6'):
        ui.label('AI Control Center').classes('text-3xl font-bold mb-4')

        with ui.card().classes('w-full'):
            ui.label('Local GGUF Model Config').classes('text-xl font-bold mb-2')

            # Simulated state for the UI
            model_path = os.environ.get('GGUF_MODEL_PATH', 'models/nous-hermes-2-solar-10.7b.Q4_K_M.gguf')

            ui.input('Model Path', value=model_path).classes('w-full max-w-2xl').set_enabled(False)

            with ui.row().classes('items-center mt-4 gap-2'):
                if os.path.exists(model_path):
                    ui.icon('check_circle', color='green', size='sm')
                    ui.label('Model file found').classes('text-green-500')
                else:
                    ui.icon('error', color='red', size='sm')
                    ui.label('Model file not found').classes('text-red-500')

            ui.label('Note: Active AI analysis happens during the reporting/analysis phases when jobs complete. Currently using CPU-fallback if GPU is unavailable.').classes('text-gray-400 mt-4 italic')
