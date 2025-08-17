"""
Tools installer & updater with automatic dependency handling.
"""
import subprocess
import sys
import logging
import shutil
import os
import requests
import zipfile
from typing import Dict
from pathlib import Path
from config.config_manager import ConfigManager

class ToolsInstaller:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = ConfigManager()
        self.tools_dir = Path(self.config.get_setting('tools.tools_path', 'tools'))
        self.git_tools = {
            "sqlmap": "https://github.com/sqlmapproject/sqlmap.git",
            "sublist3r": "https://github.com/aboul3la/Sublist3r.git",
            "whatweb": "https://github.com/urbanadventurer/WhatWeb.git",
            "nikto": "https://github.com/sullo/nikto.git",
        }
        self.binary_tools = {
            "nuclei": {
                "url": "https://github.com/projectdiscovery/nuclei/releases/download/v3.2.0/nuclei_3.2.0_windows_amd64.zip",
                "executable": "nuclei.exe"
            }
        }
        self.system_tools = {
            'nmap': {'check_command': 'nmap', 'windows': 'nmap', 'linux': 'nmap'},
            'metasploit': {'check_command': 'msfconsole', 'windows': None, 'linux': 'metasploit-framework'},
            'ruby': {'check_command': 'ruby', 'windows': 'ruby', 'linux': 'ruby-full'},
            'perl': {'check_command': 'perl', 'windows': None, 'linux': 'perl'},
        }
        self.python_packages = [
            "llama-cpp-python", "torch", "transformers", "scikit-learn", "numpy",
            "pandas", "matplotlib", "seaborn", "pyyaml", "python-dotenv",
            "fastapi", "uvicorn", "jinja2", "reportlab", "Pillow", "selenium",
            "playwright", "requests", "beautifulsoup4", "python-nmap", "scapy",
            "paramiko", "netaddr", "dnspython", "cryptography", "colorama",
            "tqdm", "click", "weasyprint", "markdown", "psutil", "pymetasploit3"
        ]

    def _is_command_available(self, command: str) -> bool:
        """Check if a command is available in the system's PATH or common locations."""
        # Standard check using shutil.which
        if shutil.which(command):
            return True

        # Custom checks for Windows where tools might not be in PATH
        if sys.platform == "win32":
            if command == "nmap":
                nmap_path = r"C:\Program Files (x86)\Nmap\nmap.exe"
                if os.path.exists(nmap_path):
                    self.logger.info(f"Found '{command}' at default Windows path: {nmap_path}")
                    return True
        
        return False

    def _auto_install_system_tool(self, tool_name: str, details: Dict[str, str]) -> bool:
        """Attempt to automatically install a missing system tool."""
        package_name = None
        install_command = []

        if sys.platform == "win32":
            package_name = details.get("windows")
            if not package_name:
                self.logger.warning(f"Auto-installation for '{tool_name}' is not supported on Windows. Please install it manually.")
                return False

            if not self._is_command_available("choco"):
                self.logger.error("Chocolatey is not installed. Please install it to auto-install system tools.")
                return False
            
            install_command = ["choco", "install", package_name, "-y"]
        
        elif sys.platform.startswith("linux"):
            package_name = details.get("linux")
            if package_name:
                # Running with sudo, which is required for apt. The user should be aware.
                self.logger.info("Attempting to run apt-get with sudo. This may require a password.")
                install_command = ["sudo", "apt-get", "install", "-y", package_name]
        
        if not install_command or not package_name:
            self.logger.warning(f"Auto-installation for '{tool_name}' is not supported on this OS.")
            return False

        try:
            self.logger.info(f"Running installation command: '{' '.join(install_command)}'")
            subprocess.run(install_command, check=True, capture_output=True, text=True)
            self.logger.info(f"Successfully installed {tool_name}.")
            return True
        except FileNotFoundError:
            self.logger.error(f"Command for package manager not found. Is it in your PATH?")
            return False
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to install {tool_name}. Error: {e.stderr}")
            return False

    def ensure_all_tools_installed(self):
        """Main method to ensure all system, git, and binary tools are installed."""
        self.logger.info("Ensuring all tools are installed...")
        self.tools_dir.mkdir(parents=True, exist_ok=True)

        # System tools
        for tool, details in self.system_tools.items():
            if not self._is_command_available(details['check_command']):
                self.logger.warning(f"System tool '{tool}' not found.")
                self._auto_install_system_tool(tool, details)
            else:
                self.logger.info(f"[+] System tool '{tool}' is already installed.")

        # Git-based tools
        for tool, url in self.git_tools.items():
            if not (self.tools_dir / tool).exists():
                self.logger.warning(f"Git-based tool '{tool}' not found. Cloning...")
                try:
                    subprocess.run(["git", "clone", url, str(self.tools_dir / tool)], check=True)
                    self.logger.info(f"[+] Cloned {tool} successfully.")
                except Exception as e:
                    self.logger.error(f"Failed to clone {tool}. Is Git installed? Error: {e}")
            else:
                self.logger.info(f"[+] Git-based tool '{tool}' is already installed.")

        # Binary tools
        for tool, details in self.binary_tools.items():
            if not (self.tools_dir / tool / details['executable']).exists():
                self.logger.warning(f"Binary tool '{tool}' not found. Downloading...")
                self._install_binary_tool(tool, details)
            else:
                self.logger.info(f"[+] Binary tool '{tool}' is already installed.")

        # Python packages
        self.install_python_packages()

    def install_python_packages(self):
        """Install required Python packages using pip."""
        self.logger.info("\nChecking and installing required Python packages...")
        for package in self.python_packages:
            try:
                subprocess.run([sys.executable, "-m", "pip", "show", package], check=True, capture_output=True)
                self.logger.info(f"[+] Package '{package}' is already installed.")
            except subprocess.CalledProcessError:
                self.logger.warning(f"Package '{package}' not found. Installing...")
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", package], check=True, capture_output=True)
                    self.logger.info(f"[+] Successfully installed {package}.")
                except subprocess.CalledProcessError as e:
                    self.logger.error(f"[!] Failed to install {package}. Error:\n{e.stderr.decode('utf-8', 'ignore')}")

    def _install_binary_tool(self, name: str, details: Dict[str, str]):
        """Downloads and extracts a binary tool from a zip file."""
        url = details['url']
        tool_dir = self.tools_dir / name
        tool_dir.mkdir(exist_ok=True)
        zip_path = self.tools_dir / f"{name}.zip"

        try:
            self.logger.info(f"Downloading {name} from {url}...")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            self.logger.info(f"Extracting {name}...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(tool_dir)
            self.logger.info(f"[+] {name} installed successfully.")

        except Exception as e:
            self.logger.error(f"An unexpected error occurred during the installation of {name}: {e}")
        finally:
            if zip_path.exists():
                zip_path.unlink()
