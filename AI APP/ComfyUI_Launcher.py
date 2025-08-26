[file name]: /Installer/AI APP/ComfyUI_Installer.py
[file content begin]
#!/usr/bin/env python3
"""
ComfyUI Installer Script
Automates the installation of ComfyUI with specified configurations
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description, cwd=None):
    """Execute a shell command with error handling and real-time output"""
    print(f"\n🔧 {description}...")
    print(f"   Running: {command}")
    
    try:
        # Remove capture_output=True to show real-time output
        result = subprocess.run(command, shell=True, check=True, cwd=cwd, text=True)
        print(f"   ✅ Success: {description}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error: {description}")
        print(f"   Return code: {e.returncode}")
        return False

def main():
    print("🚀 Starting ComfyUI Installation")
    print("=" * 50)
    
    # Define paths based on the new structure
    workspace_path = "/workspace"
    envs_path = os.path.join(workspace_path, "ENVS")
    conda_p311_path = os.path.join(envs_path, "Conda_P3.11")
    comfyui_path = os.path.join(workspace_path, "ComfyUI")
    custom_nodes_path = os.path.join(comfyui_path, "custom_nodes")
    
    # 1. Create conda environment
    conda_create_cmd = f"conda create --prefix {conda_p311_path} python=3.11 -y"
    if not run_command(conda_create_cmd, "Creating conda environment"):
        sys.exit(1)
    
    # 2. Create ENVS directory if it doesn't exist
    print(f"\n📁 Creating ENVS directory at {envs_path}...")
    try:
        os.makedirs(envs_path, exist_ok=True)
        print("   ✅ ENVS directory created successfully")
    except Exception as e:
        print(f"   ❌ Error creating ENVS directory: {e}")
        sys.exit(1)
    
    # 3. Clone ComfyUI repository
    clone_cmd = "git clone https://github.com/comfyanonymous/ComfyUI.git"
    if not run_command(clone_cmd, "Cloning ComfyUI repository", cwd=workspace_path):
        sys.exit(1)
    
    # 4. Install torch with conda environment activated
    pip_install_torch_cmd = (
        f"conda run --prefix {conda_p311_path} "
        f"pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
    )
    if not run_command(pip_install_torch_cmd, "Installing PyTorch", cwd=comfyui_path):
        sys.exit(1)
    
    # 5. Install requirements.txt
    pip_install_reqs_cmd = (
        f"conda run --prefix {conda_p311_path} "
        "pip install -r requirements.txt"
    )
    if not run_command(pip_install_reqs_cmd, "Installing requirements", cwd=comfyui_path):
        sys.exit(1)
    
    # 6. Create custom_nodes directory and clone ComfyUI-Manager
    print(f"\n📁 Creating custom_nodes directory...")
    try:
        os.makedirs(custom_nodes_path, exist_ok=True)
        print("   ✅ custom_nodes directory created")
    except Exception as e:
        print(f"   ❌ Error creating custom_nodes directory: {e}")
        sys.exit(1)
    
    # Clone ComfyUI-Manager
    clone_manager_cmd = "git clone https://github.com/ltdrdata/ComfyUI-Manager.git"
    if not run_command(clone_manager_cmd, "Cloning ComfyUI-Manager", cwd=custom_nodes_path):
        sys.exit(1)
    
    # Create the shell script in ComfyUI base folder
    shell_script_path = os.path.join(comfyui_path, "run_comfyui.sh")
    try:
        with open(shell_script_path, 'w') as f:
            f.write("""#!/bin/bash
# ComfyUI Runner Script
cd /workspace/ComfyUI
source activate /workspace/ENVS/Conda_P3.11
python main.py --listen --port 8188
""")
        # Make the script executable
        os.chmod(shell_script_path, 0o755)
        print(f"   ✅ Created run_comfyui.sh at {shell_script_path}")
    except Exception as e:
        print(f"   ❌ Error creating shell script: {e}")
        sys.exit(1)
    
    # Create the Python launcher in workspace
    launcher_path = os.path.join(workspace_path, "comfyui_launcher.py")
    try:
        with open(launcher_path, 'w') as f:
            f.write("""#!/usr/bin/env python3
import subprocess
import os

def main():
    comfyui_path = "/workspace/ComfyUI"
    shell_script = os.path.join(comfyui_path, "run_comfyui.sh")
    
    print("🚀 Launching ComfyUI...")
    print(f"Running: {shell_script}")
    
    try:
        subprocess.run([shell_script], check=True, cwd=comfyui_path)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching ComfyUI: {e}")
    except KeyboardInterrupt:
        print("\n🛑 ComfyUI stopped by user")

if __name__ == "__main__":
    main()
""")
        print(f"   ✅ Created comfyui_launcher.py at {launcher_path}")
    except Exception as e:
        print(f"   ❌ Error creating launcher script: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 ComfyUI Installation Completed Successfully!")
    print(f"📁 Installation location: {comfyui_path}")
    print(f"🐍 Conda environment: {conda_p311_path}")
    print(f"🌐 ComfyUI-Manager installed at: {custom_nodes_path}/ComfyUI-Manager")
    print(f"📜 Shell script created at: {shell_script_path}")
    print(f"🚀 Launcher script created at: {launcher_path}")
    print("\n📋 Next steps:")
    print("   1. Run the launcher script: python comfyui_launcher.py")
    print("   2. Open your browser to: http://localhost:8188")

if __name__ == "__main__":
    main()
[file content end]

[file name]: /workspace/ComfyUI/run_comfyui.sh
[file content begin]
#!/bin/bash
# ComfyUI Runner Script
cd /workspace/ComfyUI
source activate /workspace/ENVS/Conda_P3.11
python main.py --listen --port 8188
[file content end]

[file name]: /workspace/comfyui_launcher.py
[file content begin]
#!/usr/bin/env python3
import subprocess
import os

def main():
    comfyui_path = "/workspace/ComfyUI"
    shell_script = os.path.join(comfyui_path, "run_comfyui.sh")
    
    print("🚀 Launching ComfyUI...")
    print(f"Running: {shell_script}")
    
    try:
        subprocess.run([shell_script], check=True, cwd=comfyui_path)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching ComfyUI: {e}")
    except KeyboardInterrupt:
        print("\n🛑 ComfyUI stopped by user")

if __name__ == "__main__":
    main()
[file content end]
