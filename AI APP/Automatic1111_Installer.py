#!/usr/bin/env python3
"""
Automatic1111 WebUI Installer for RunPod
This script installs and configures the Stable Diffusion WebUI in /workspace directory.
"""

import os
import sys
import subprocess
import argparse
import platform
from pathlib import Path

class WebUIInstaller:
    def __init__(self):
        self.system = platform.system().lower()
        self.base_dir = Path("/workspace")
        self.webui_dir = self.base_dir / "stable-diffusion-webui"
        self.installer_dir = self.base_dir / "Installer"
        self.envs_dir = self.base_dir / "ENVS"
        
    def check_dependencies(self):
        """Check if required dependencies are installed"""
        print("Checking dependencies...")
        
        # Check if conda is available
        try:
            subprocess.run(["conda", "--version"], check=True, capture_output=True)
            print("✓ Conda is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("✗ Conda is not installed or not in PATH")
            return False
            
        # Check if git is available
        try:
            subprocess.run(["git", "--version"], check=True, capture_output=True)
            print("✓ Git is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("✗ Git is not installed")
            return False
            
        return True
    
    def create_directory_structure(self):
        """Create the required directory structure in /workspace"""
        print("Creating directory structure in /workspace...")
        
        directories = [
            self.base_dir,
            self.base_dir / "ComfyUI_Workflows",
            self.envs_dir,
            self.envs_dir / "Conda_P3.10",
            self.envs_dir / "Conda_P3.11",
            self.installer_dir,
            self.installer_dir / "AI APP",
            self.installer_dir / "DOWNLOADER",
            self.installer_dir / "SYSTEM"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created directory: {directory}")
    
    def setup_conda_environment(self):
        """Setup the Conda Python 3.10 environment"""
        print("Setting up Conda Python 3.10 environment...")
        
        env_path = self.envs_dir / "Conda_P3.10"
        
        try:
            # Create conda environment
            result = subprocess.run([
                "conda", "create", 
                "--prefix", str(env_path),
                "python=3.10", "-y"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✓ Conda environment created successfully")
                return True
            else:
                print(f"✗ Failed to create conda environment: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"✗ Error creating conda environment: {str(e)}")
            return False
    
    def clone_webui_repository(self):
        """Clone the Automatic1111 WebUI repository"""
        print("Cloning Automatic1111 WebUI repository...")
        
        if (self.webui_dir / ".git").exists():
            print("✓ WebUI repository already exists, skipping clone")
            return True
            
        try:
            result = subprocess.run([
                "git", "clone",
                "https://github.com/AUTOMATIC1111/stable-diffusion-webui.git",
                str(self.webui_dir)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✓ WebUI repository cloned successfully")
                return True
            else:
                print(f"✗ Failed to clone repository: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"✗ Error cloning repository: {str(e)}")
            return False
    
    def install(self):
        """Run the complete installation process"""
        print("Starting Automatic1111 WebUI installation in /workspace...")
        print(f"Base directory: {self.base_dir}")
        
        # Check dependencies
        if not self.check_dependencies():
            print("Please install the missing dependencies and try again.")
            return False
        
        # Create directory structure
        self.create_directory_structure()
        
        # Setup conda environment
        if not self.setup_conda_environment():
            print("Failed to setup conda environment.")
            return False
        
        # Clone repository
        if not self.clone_webui_repository():
            print("Failed to clone WebUI repository.")
            return False
        
        print("\n" + "="*60)
        print("Installation completed successfully!")
        print("="*60)
        print(f"WebUI installed at: {self.webui_dir}")
        print(f"Conda environment: {self.envs_dir / 'Conda_P3.10'}")
        print("\nTo start the WebUI, navigate to the directory and run:")
        print(f"  cd {self.webui_dir}")
        print("  bash webui-user.sh")
        print("\nDependencies will be installed automatically by webui-user.sh on first run")
        
        return True

def main():
    parser = argparse.ArgumentParser(description="Automatic1111 WebUI Installer for RunPod")
    parser.add_argument(
        "--skip-deps", 
        action="store_true",
        help="Skip dependency checks"
    )
    
    args = parser.parse_args()
    
    installer = WebUIInstaller()
    success = installer.install()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
