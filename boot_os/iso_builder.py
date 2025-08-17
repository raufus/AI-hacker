
"""
Custom Kali/Ubuntu ISO builder with persistence
"""
import os
import subprocess
import logging
from pathlib import Path

class ISOBuilder:
    def __init__(self):
        self.logger = logging.getLogger("ISOBuilder")
        self.work_dir = Path("boot_os/work")
        self.iso_dir = Path("boot_os/iso")
        self.tools_list = [
            "nmap", "sqlmap", "nikto", "metasploit-framework",
            "sublist3r", "whatweb", "gobuster", "dirb"
        ]
    
    def create_directories(self):
        """Create necessary directories"""
        self.work_dir.mkdir(exist_ok=True)
        self.iso_dir.mkdir(exist_ok=True)
    
    def download_base_iso(self, iso_url: str = None):
        """Download base Kali Linux ISO"""
        if not iso_url:
            iso_url = "https://cdimage.kali.org/kali-2023.4/kali-linux-2023.4-live-amd64.iso"
        
        iso_file = self.iso_dir / "kali-base.iso"
        
        if iso_file.exists():
            self.logger.info("Base ISO already exists")
            return str(iso_file)
        
        self.logger.info(f"Downloading base ISO from {iso_url}")
        try:
            subprocess.run([
                "wget", "-O", str(iso_file), iso_url
            ], check=True)
            return str(iso_file)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to download ISO: {e}")
            return None
    
    def extract_iso(self, iso_file: str):
        """Extract ISO contents"""
        extract_dir = self.work_dir / "iso_extract"
        extract_dir.mkdir(exist_ok=True)
        
        try:
            # Mount ISO
            mount_point = self.work_dir / "iso_mount"
            mount_point.mkdir(exist_ok=True)
            
            subprocess.run([
                "sudo", "mount", "-o", "loop", iso_file, str(mount_point)
            ], check=True)
            
            # Copy contents
            subprocess.run([
                "sudo", "cp", "-r", f"{mount_point}/*", str(extract_dir)
            ], shell=True, check=True)
            
            # Unmount
            subprocess.run([
                "sudo", "umount", str(mount_point)
            ], check=True)
            
            return str(extract_dir)
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to extract ISO: {e}")
            return None
    
    def customize_iso(self, extract_dir: str):
        """Customize ISO with AI_HackerOS"""
        try:
            # Copy AI_HackerOS to ISO
            hackeros_dir = Path(extract_dir) / "ai_hackeros"
            hackeros_dir.mkdir(exist_ok=True)
            
            # Copy project files
            project_files = [
                "main.py", "README.md", "ai_brain/", "modules/",
                "agent/", "browser_bot/", "report/", "utils/", "config/"
            ]
            
            for file_path in project_files:
                if Path(file_path).exists():
                    if Path(file_path).is_dir():
                        subprocess.run([
                            "cp", "-r", file_path, str(hackeros_dir)
                        ], check=True)
                    else:
                        subprocess.run([
                            "cp", file_path, str(hackeros_dir)
                        ], check=True)
            
            # Create startup script
            startup_script = hackeros_dir / "startup.sh"
            with open(startup_script, "w") as f:
                f.write("""#!/bin/bash
# AI_HackerOS Startup Script
cd /ai_hackeros
python3 main.py --install-tools
echo "AI_HackerOS Ready!"
""")
            
            os.chmod(startup_script, 0o755)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to customize ISO: {e}")
            return False
    
    def create_iso(self, extract_dir: str, output_file: str = "ai_hackeros.iso"):
        """Create new ISO file"""
        try:
            output_path = self.iso_dir / output_file
            
            subprocess.run([
                "sudo", "genisoimage",
                "-o", str(output_path),
                "-b", "isolinux/isolinux.bin",
                "-c", "isolinux/boot.cat",
                "-no-emul-boot",
                "-boot-load-size", "4",
                "-boot-info-table",
                "-J", "-R", "-V", "AI_HackerOS",
                extract_dir
            ], check=True)
            
            self.logger.info(f"ISO created: {output_path}")
            return str(output_path)
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to create ISO: {e}")
            return None
    
    def build_custom_iso(self):
        """Build complete custom ISO"""
        self.logger.info("Starting custom ISO build")
        
        # Create directories
        self.create_directories()
        
        # Download base ISO
        base_iso = self.download_base_iso()
        if not base_iso:
            return None
        
        # Extract ISO
        extract_dir = self.extract_iso(base_iso)
        if not extract_dir:
            return None
        
        # Customize ISO
        if not self.customize_iso(extract_dir):
            return None
        
        # Create new ISO
        custom_iso = self.create_iso(extract_dir)
        
        return custom_iso
