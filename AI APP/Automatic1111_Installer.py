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
    
    def install_webui_dependencies(self):
        """Install WebUI dependencies using the conda environment"""
        print("Installing WebUI dependencies...")
        
        env_path = self.envs_dir / "Conda_P3.10"
        
        # Install torch and other dependencies first
        try:
            # Activate conda environment and install requirements
            install_cmd = [
                "conda", "run", "--prefix", str(env_path),
                "pip", "install",
                "torch", "torchvision", "torchaudio",
                "--index-url", "https://download.pytorch.org/whl/cu118"
            ]
            
            result = subprocess.run(install_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✓ PyTorch installed successfully")
            else:
                print(f"✗ Failed to install PyTorch: {result.stderr}")
                return False
                
            # Install other requirements from the webui repository
            requirements_file = self.webui_dir / "requirements.txt"
            if requirements_file.exists():
                install_cmd = [
                    "conda", "run", "--prefix", str(env_path),
                    "pip", "install", "-r", str(requirements_file)
                ]
                
                result = subprocess.run(install_cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("✓ WebUI requirements installed successfully")
                    return True
                else:
                    print(f"✗ Failed to install requirements: {result.stderr}")
                    return False
            else:
                print("⚠ Requirements file not found, trying to install xformers and other essentials")
                
                # Install essential packages if requirements.txt is missing
                essential_packages = [
                    "xformers", "transformers", "accelerate",
                    "diffusers", "open-clip-torch", "clip",
                    "numpy", "pillow", "scipy", "tqdm",
                    "requests", "ftfy", "ipywidgets"
                ]
                
                install_cmd = [
                    "conda", "run", "--prefix", str(env_path),
                    "pip", "install"
                ] + essential_packages
                
                result = subprocess.run(install_cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("✓ Essential packages installed successfully")
                    return True
                else:
                    print(f"✗ Failed to install essential packages: {result.stderr}")
                    return False
                
        except Exception as e:
            print(f"✗ Error installing dependencies: {str(e)}")
            return False
    
    def create_launch_script(self):
        """Create a launch script for the WebUI"""
        print("Creating launch script...")
        
        launch_script = self.installer_dir / "AI APP" / "launch_webui.sh"
        env_path = self.envs_dir / "Conda_P3.10"
        
        script_content = f"""#!/bin/bash
# Automatic1111 WebUI Launch Script
export CONDA_ENV_PATH="{env_path}"
export WEBUI_DIR="{self.webui_dir}"

# Activate conda environment
source activate "$CONDA_ENV_PATH"

# Navigate to WebUI directory
cd "$WEBUI_DIR"

# Set environment variables for GPU acceleration
export COMMANDLINE_ARGS="--listen --port 7860 --enable-insecure-extension-access --xformers"

# Launch the WebUI
python launch.py $COMMANDLINE_ARGS
"""
        
        try:
            with open(launch_script, 'w') as f:
                f.write(script_content)
            
            # Make the script executable
            os.chmod(launch_script, 0o755)
            print(f"✓ Launch script created: {launch_script}")
            return True
            
        except Exception as e:
            print(f"✗ Error creating launch script: {str(e)}")
            return False
    
    def create_conda_activation_script(self):
        """Create a script to activate the conda environment"""
        print("Creating conda activation script...")
        
        activation_script = self.installer_dir / "SYSTEM" / "activate_env.sh"
        env_path = self.envs_dir / "Conda_P3.10"
        
        script_content = f"""#!/bin/bash
# Script to activate the Conda environment for Automatic1111 WebUI
export CONDA_ENV_PATH="{env_path}"

# Activate conda environment
source activate "$CONDA_ENV_PATH"

echo "Conda environment activated: $CONDA_ENV_PATH"
echo "WebUI directory: {self.webui_dir}"
"""
        
        try:
            with open(activation_script, 'w') as f:
                f.write(script_content)
            
            # Make the script executable
            os.chmod(activation_script, 0o755)
            print(f"✓ Conda activation script created: {activation_script}")
            return True
            
        except Exception as e:
            print(f"✗ Error creating conda activation script: {str(e)}")
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
        
        # Install dependencies
        if not self.install_webui_dependencies():
            print("Failed to install WebUI dependencies.")
            return False
        
        # Create launch script
        if not self.create_launch_script():
            print("Failed to create launch script.")
            return False
            
        # Create conda activation script
        if not self.create_conda_activation_script():
            print("Failed to create conda activation script.")
            return False
        
        print("\n" + "="*60)
        print("Installation completed successfully!")
        print("="*60)
        print(f"WebUI installed at: {self.webui_dir}")
        print(f"Conda environment: {self.envs_dir / 'Conda_P3.10'}")
        print(f"Launch script: {self.installer_dir / 'AI APP' / 'launch_webui.sh'}")
        print(f"Activation script: {self.installer_dir / 'SYSTEM' / 'activate_env.sh'}")
        print("\nTo start the WebUI, run:")
        print(f"  bash {self.installer_dir / 'AI APP' / 'launch_webui.sh'}")
        print("\nTo activate the environment for manual use:")
        print(f"  source {self.installer_dir / 'SYSTEM' / 'activate_env.sh'}")
        
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
