"""
System-level utilities, including privilege management.
"""
import os
import sys
import ctypes

def is_admin():
    """Check if the script is running with administrative privileges on Windows."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Re-launch the script with administrative privileges on Windows."""
    if sys.platform == 'win32':
        if not is_admin():
            script = os.path.abspath(sys.argv[0])
            params = ' '.join([f'"{p}"' for p in sys.argv[1:]])
            log_file = os.path.join(os.path.dirname(script), "agent_run.log")
            # Command to re-launch the script with output redirected to a log file.
            # We use cmd.exe /c to handle the redirection.
            command = f'\"{sys.executable}\" \"{script}\" {params}'
            redirected_command = f'cmd.exe /c {command} > \"{log_file}\" 2>&1'

            try:
                full_params = f'/c \"{sys.executable}\" \"{script}\" {params} > \"{log_file}\" 2>&1'
                h_instance = ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd.exe", full_params, None, 0)

                if h_instance <= 32:
                    print(f"Error: Failed to elevate privileges. ShellExecuteW returned error code: {h_instance}")
                    sys.exit(1)
                else:
                    # Successfully launched elevated process.
                    sys.exit(0)
            except Exception as e:
                print(f"Error: An exception occurred while trying to elevate privileges: {e}")
                sys.exit(1)
