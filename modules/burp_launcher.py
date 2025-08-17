"""
Module for launching and managing Burp Suite.
"""
import subprocess
import logging
from pathlib import Path
from config.config_manager import ConfigManager

class BurpLauncher:
    """A class to launch and manage the Burp Suite application."""

    def __init__(self):
        """Initialize the BurpLauncher."""
        self.logger = logging.getLogger(__name__)
        self.config = ConfigManager()
        self.process = None

    def launch(self) -> bool:
        """Launches the Burp Suite JAR file as a subprocess.

        Returns:
            bool: True if Burp Suite was launched successfully, False otherwise.
        """
        burp_config = self.config.get_setting('burp_suite')
        if not burp_config or not burp_config.get('jar_path'):
            self.logger.error("Burp Suite configuration or JAR path not found.")
            return False

        jar_path = Path(burp_config['jar_path'])
        if not jar_path.exists():
            self.logger.error(f"Burp Suite JAR not found at specified path: {jar_path}")
            return False

        # Command to launch Burp Suite. 
        # Additional arguments for headless mode or specific configs can be added here.
        command = ["java", "-jar", str(jar_path)]

        try:
            self.logger.info(f"Launching Burp Suite from: {jar_path}")
            # Use Popen to run Burp Suite as a non-blocking background process.
            self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.logger.info(f"Burp Suite launched successfully with PID: {self.process.pid}")
            return True
        except FileNotFoundError:
            self.logger.error("Java is not installed or not in the system's PATH. Cannot launch Burp Suite.")
            return False
        except Exception as e:
            self.logger.error(f"Failed to launch Burp Suite: {e}")
            return False

    def shutdown(self):
        """Terminates the Burp Suite process if it is running."""
        if self.process and self.process.poll() is None:
            self.logger.info("Shutting down Burp Suite...")
            self.process.terminate()
            try:
                self.process.wait(timeout=10)  # Wait for 10 seconds
                self.logger.info("Burp Suite shut down successfully.")
            except subprocess.TimeoutExpired:
                self.logger.warning("Burp Suite did not terminate gracefully. Forcing shutdown.")
                self.process.kill()
