#!/usr/bin/env python3
"""
Automatic1111 Script Generator for RunPod - Creates a working shell script
"""

import os

def main():
    print("Automatic1111 Shell Script Generator for RunPod")
    print("=" * 60)
    
    script_content = """#!/bin/bash
# Automatic1111 Startup Script for RunPod
echo "Starting Automatic1111 WebUI..."
echo "Setting up environment..."

# Export environment variables
export COMMANDLINE_ARGS="--no-download-sd-model --xformers --no-half-vae --api --theme dark --listen --port 8288"

# Change to workspace directory
cd /workspace

# Source conda and activate environment
if [ -f "/opt/conda/etc/profile.d/conda.sh" ]; then
    source "/opt/conda/etc/profile.d/conda.sh"
elif [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
    source "$HOME/miniconda3/etc/profile.d/conda.sh"
else
    echo "Warning: conda.sh not found in common locations"
fi

# Activate conda environment (Python 3.10 for stable-diffusion-webui)
conda activate /workspace/ENVS/Conda_P3.10

# Change to Automatic1111 directory
cd /workspace/stable-diffusion-webui

echo "Environment setup complete"
echo "Launching Automatic1111 WebUI on port 8288..."
echo "COMMANDLINE_ARGS: $COMMANDLINE_ARGS"

# Run launch.py directly with the specified arguments
python launch.py $COMMANDLINE_ARGS
"""
    
    # Create the startup script in the Automatic1111 base folder
    script_filename = "/workspace/stable-diffusion-webui/start_automatic1111.sh"
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(script_filename), exist_ok=True)
        
        with open(script_filename, 'w') as f:
            f.write(script_content)
        
        os.chmod(script_filename, 0o755)  # Make it executable
        
        print(f"✓ Created executable script: {script_filename}")
        
        # Now create a launcher script in the workspace directory
        launcher_content = """#!/usr/bin/env python3
import os
import subprocess
import sys

def main():
    print("Launching Automatic1111 WebUI...")
    script_path = "/workspace/stable-diffusion-webui/start_automatic1111.sh"
    
    if not os.path.exists(script_path):
        print(f"Error: Startup script not found at {script_path}")
        sys.exit(1)
    
    # Make sure the script is executable
    os.chmod(script_path, 0o755)
    
    # Run the script
    try:
        process = subprocess.Popen(["bash", script_path], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.STDOUT,
                                  universal_newlines=True)
        
        # Stream output in real-time
        for line in process.stdout:
            print(line, end='')
            
        process.wait()
        
    except Exception as e:
        print(f"Error running Automatic1111: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
"""
        
        launcher_filename = "/workspace/launch_automatic1111.py"
        
        with open(launcher_filename, 'w') as f:
            f.write(launcher_content)
        
        os.chmod(launcher_filename, 0o755)  # Make it executable
        
        print(f"✓ Created launcher script: {launcher_filename}")
        print("\nTo run Automatic1111, execute:")
        print(f"  python {launcher_filename}")
        print("\nOr run the shell script directly:")
        print(f"  bash {script_filename}")
        print("\nThe script will:")
        print("  - Start on port 8288 (for RunPod)")
        print("  - Use the specified COMMANDLINE_ARGS")
        print("  - Activate conda environment: /workspace/ENVS/Conda_P3.10")
        print("  - Run from /workspace/stable-diffusion-webui")
        print("  - Execute launch.py directly with arguments")
        
    except Exception as e:
        print(f"✗ Error creating script: {e}")
        print("\nManual commands to run:")
        print("cd /workspace")
        print("conda activate /workspace/ENVS/Conda_P3.10")
        print("cd /workspace/stable-diffusion-webui")
        print("export COMMANDLINE_ARGS=\"--no-download-sd-model --xformers --no-half-vae --api --theme dark --listen --port 8288\"")
        print("python launch.py $COMMANDLINE_ARGS")

if __name__ == "__main__":
    main()
