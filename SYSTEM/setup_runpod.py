#!/usr/bin/env python3
"""
RunPod Foundation Setup Script
Installs only: GIT, Miniconda, Python, and essential tools
PyTorch will be installed manually per project
"""

import os
import subprocess
import sys
import urllib.request
import threading
import time
import shutil

class Spinner:
    """A simple spinner animation for indicating progress"""
    def __init__(self, message="Working"):
        self.message = message
        self.spinner_chars = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
        self.stop_running = False
        self.thread = None
    
    def spin(self):
        """Run the spinner animation"""
        i = 0
        while not self.stop_running:
            sys.stdout.write(f"\r{self.spinner_chars[i]} {self.message}")
            sys.stdout.flush()
            time.sleep(0.1)
            i = (i + 1) % len(self.spinner_chars)
    
    def __enter__(self):
        """Start the spinner when entering context"""
        self.thread = threading.Thread(target=self.spin)
        self.thread.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop the spinner when exiting context"""
        self.stop_running = True
        self.thread.join()
        sys.stdout.write("\r" + " " * (len(self.message) + 2) + "\r")
        sys.stdout.flush()

def run_command(cmd, description="", check=True, show_output=False):
    """Execute a shell command with error handling and progress indication"""
    if description:
        print(f"🚀 {description}...")
    
    try:
        with Spinner(f"Running: {cmd[:50]}{'...' if len(cmd) > 50 else ''}"):
            if show_output:
                # Show command output in real-time
                result = subprocess.run(cmd, shell=True, check=check, text=True)
            else:
                # Capture output and show only if there's an error
                result = subprocess.run(cmd, shell=True, check=check, 
                                      capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Success: {description}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Error {description}: {e}")
        if not check:
            return e
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        sys.exit(1)

def download_with_progress(url, filename):
    """Download a file with progress indicator"""
    def reporthook(count, block_size, total_size):
        percent = int(count * block_size * 100 / total_size)
        sys.stdout.write(f"\r📥 Downloading: {percent}% ({count * block_size / (1024*1024):.1f} MB)")
        sys.stdout.flush()
    
    print(f"📥 Downloading: {os.path.basename(url)}")
    urllib.request.urlretrieve(url, filename, reporthook)
    print("\r✅ Download completed" + " " * 30)  # Clear the line

def accept_conda_tos(channel_url):
    """Accept Conda channel Terms of Service"""
    print(f"📝 Accepting TOS for channel: {channel_url}")
    result = run_command(
        f"/opt/conda/bin/conda tos accept --override-channels --channel {channel_url}",
        f"Accepting TOS for {channel_url}",
        check=False
    )
    
    if result.returncode != 0:
        print(f"ℹ️  TOS acceptance for {channel_url} may not be required or already accepted")

def install_git():
    """Install GIT"""
    run_command("apt-get update", "Updating package list", show_output=True)
    run_command("apt-get install -y git", "Installing GIT", show_output=True)

def install_miniconda():
    """Install Miniconda"""
    miniconda_url = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
    install_script = "/tmp/miniconda.sh"
    
    # Download Miniconda with progress
    download_with_progress(miniconda_url, install_script)
    
    # Install Miniconda
    run_command(f"bash {install_script} -b -p /opt/conda", "Installing Miniconda", show_output=True)
    
    # Add conda to PATH
    conda_path = "/opt/conda/bin"
    os.environ['PATH'] = f"{conda_path}:{os.environ['PATH']}"
    
    # Initialize conda for bash
    run_command("/opt/conda/bin/conda init bash", "Initializing Conda for bash")
    
    # Initialize conda for the current shell session
    run_command('eval "$(/opt/conda/bin/conda shell.bash hook)"', "Setting up Conda for current shell")
    
    # Accept TOS for default channels
    default_channels = [
        "https://repo.anaconda.com/pkgs/main",
        "https://repo.anaconda.com/pkgs/r",
        "defaults",
        "nvidia",
        "pytorch",
        "conda-forge"
    ]
    
    for i, channel in enumerate(default_channels):
        print(f"📝 Accepting TOS ({i+1}/{len(default_channels)}): {channel}")
        accept_conda_tos(channel)
    
    # Update conda
    run_command("/opt/conda/bin/conda update -n base -c defaults conda -y", "Updating Conda", show_output=True)
    
    # Clean up
    os.remove(install_script)
    
    return conda_path

def install_essential_tools():
    """Install essential development tools"""
    tools = ["wget", "curl", "vim", "nano", "htop"]
    print(f"📦 Installing tools: {', '.join(tools)}")
    run_command("apt-get install -y " + " ".join(tools), "Installing essential tools", show_output=True)

def setup_environment():
    """Set up basic environment configuration"""
    # Add conda to PATH in bashrc
    with open("/root/.bashrc", "a") as f:
        f.write("\n# Added by RunPod setup script\n")
        f.write("export PATH=/opt/conda/bin:$PATH\n")
        f.write('eval "$(/opt/conda/bin/conda shell.bash hook)"\n')
    
    # Also set up for current session
    os.environ['PATH'] = f"/opt/conda/bin:{os.environ['PATH']}"
    
    # Initialize conda for the current shell
    run_command('eval "$(/opt/conda/bin/conda shell.bash hook)"', "Initializing Conda for current shell")
    
    print("✅ Environment variables configured")

def test_conda_initialization():
    """Test if conda is properly initialized"""
    print("🧪 Testing Conda initialization...")
    
    # Test if we can create a new environment
    result = run_command(
        "/opt/conda/bin/conda create -n test_env -y",
        "Testing Conda environment creation",
        check=False
    )
    
    if result.returncode == 0:
        # Clean up test environment
        run_command("/opt/conda/bin/conda env remove -n test_env -y", "Removing test environment")
        print("✅ Conda is properly initialized and working")
        return True
    else:
        print("⚠️  Conda initialization may need manual intervention")
        print("💡 Try running: source ~/.bashrc")
        return False

def check_disk_space():
    """Check available disk space"""
    total, used, free = shutil.disk_usage("/")
    print(f"💾 Disk space: {free // (2**30)} GB free of {total // (2**30)} GB total")

def main():
    """Main setup function"""
    print("=" * 60)
    print("🏗️  RunPod Foundation Setup Script")
    print("📦 Base tools only - PyTorch to be installed manually")
    print("=" * 60)
    
    # Check disk space
    check_disk_space()
    
    # Check if we're on a Linux system
    if not sys.platform.startswith('linux'):
        print("❌ This script is designed for Linux systems (RunPod)")
        sys.exit(1)
    
    # Install GIT
    install_git()
    
    # Install essential tools
    install_essential_tools()
    
    # Install Miniconda
    install_miniconda()
    
    # Set up environment
    setup_environment()
    
    # Test conda initialization
    test_conda_initialization()
    
    print("=" * 60)
    print("🎉 Foundation setup completed successfully!")
    print("📋 Installed components:")
    print("   ✅ GIT")
    print("   ✅ Essential tools (curl, wget, vim, htop)")
    print("   ✅ Miniconda with Python")
    print("   ✅ Conda channel TOS accepted")
    print("   ✅ Conda initialized for bash")
    print("")
    print("🚀 Now you can create environments directly:")
    print("")
    print("   # Create a new environment")
    print("   conda create -n my-ai-app python=3.10")
    print("   conda activate my-ai-app")
    print("")
    print("   # Install PyTorch with CUDA 11.8")
    print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
    print("")
    print("   # Or with Conda:")
    print("   conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia")
    print("")
    print("   # Verify installation")
    print("   python -c \"import torch; print(torch.__version__); print(torch.cuda.is_available())\"")
    print("=" * 60)

if __name__ == "__main__":
    main()
