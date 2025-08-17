
"""
USB persistence and auto-boot functionality
"""
import os
import subprocess
import logging
from pathlib import Path

class PersistenceManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.boot_dir = Path("/boot")
        self.persistence_dir = Path("/persistence")
        
    def setup_persistence(self) -> bool:
        """Setup persistent storage on USB"""
        try:
            # Create persistence directory
            self.persistence_dir.mkdir(exist_ok=True)
            
            # Copy AI_HackerOS to persistence
            subprocess.run([
                "rsync", "-av", "/ai_hackeros/", 
                str(self.persistence_dir / "ai_hackeros")
            ], check=True)
            
            # Create autostart script
            autostart_script = self.persistence_dir / "autostart.sh"
            with open(autostart_script, "w") as f:
                f.write("""#!/bin/bash
# AI_HackerOS Autostart Script

# Wait for network
sleep 30

# Start AI_HackerOS in autonomous mode
cd /persistence/ai_hackeros
python3 main.py --auto --target auto-discover

""")
            
            os.chmod(autostart_script, 0o755)
            
            # Add to system startup
            self.add_to_startup(str(autostart_script))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup persistence: {e}")
            return False
    
    def add_to_startup(self, script_path: str):
        """Add script to system startup"""
        try:
            # Create systemd service
            service_content = f"""[Unit]
Description=AI_HackerOS Autonomous Service
After=network.target

[Service]
Type=forking
ExecStart={script_path}
Restart=always
User=root

[Install]
WantedBy=multi-user.target
"""
            
            service_file = Path("/etc/systemd/system/ai-hackeros.service")
            with open(service_file, "w") as f:
                f.write(service_content)
            
            # Enable service
            subprocess.run(["systemctl", "enable", "ai-hackeros.service"], check=True)
            
        except Exception as e:
            self.logger.error(f"Failed to add to startup: {e}")
    
    def create_bootable_usb(self, usb_device: str, iso_path: str) -> bool:
        """Create bootable USB with persistence"""
        try:
            # Write ISO to USB
            subprocess.run([
                "dd", f"if={iso_path}", f"of={usb_device}", 
                "bs=4M", "status=progress"
            ], check=True)
            
            # Add persistence partition
            subprocess.run([
                "parted", usb_device, "mkpart", "primary", 
                "ext4", "2GB", "100%"
            ], check=True)
            
            # Format persistence partition
            persistence_partition = f"{usb_device}2"
            subprocess.run([
                "mkfs.ext4", "-L", "persistence", persistence_partition
            ], check=True)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create bootable USB: {e}")
            return False
