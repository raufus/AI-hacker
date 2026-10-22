from nicegui import ui
from ui.theme import frame
from ai_brain.llm import LLMEngine

@ui.page('/ai')
def ai_control_page():
    frame()
    with ui.column().classes('w-full max-w-6xl mx-auto p-6 gap-6'):
        ui.label('AI Control Center').classes('text-3xl font-bold mb-4')

        with ui.card().classes('w-full'):
            ui.label('Current AI Provider').classes('text-xl font-bold mb-4')

            # Simple check for the default local model
            engine = LLMEngine()

            with ui.row().classes('items-center gap-4'):
                ui.label('Provider:').classes('font-bold')
                ui.label(engine.provider_name.upper()).classes('bg-gray-700 px-2 py-1 rounded')

            with ui.row().classes('items-center gap-4 mt-2'):
                ui.label('Model Path:').classes('font-bold')
                ui.label(engine.provider.model_path)

            status_color = 'text-green-500' if getattr(engine.provider, 'is_loaded', False) else 'text-red-500'
            status_text = 'LOADED' if getattr(engine.provider, 'is_loaded', False) else 'UNLOADED / CHECKING...'

            with ui.row().classes('items-center gap-4 mt-2'):
                ui.label('Status:').classes('font-bold')
                status_label = ui.label(status_text).classes(f'font-bold {status_color}')

            import asyncio

            async def check_model():
                ui.notify('Attempting to load AI model in background... This may take a moment.')
                # Run the heavy loading task in an executor to avoid blocking the main UI thread
                import concurrent.futures
                loop = asyncio.get_running_loop()
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    success = await loop.run_in_executor(pool, engine.load_model)

                if success:
                    status_label.set_text('LOADED')
                    status_label.classes(remove='text-red-500', add='text-green-500')
                    ui.notify('Model loaded successfully.', type='positive')
                else:
                    status_label.set_text('FAILED TO LOAD')
                    status_label.classes(remove='text-green-500', add='text-red-500')
                    ui.notify('Model failed to load. Check logs.', type='negative')

            ui.button('Test / Load Model', on_click=check_model).classes('mt-4 bg-blue-600')
