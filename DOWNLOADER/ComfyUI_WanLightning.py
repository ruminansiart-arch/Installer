#!/usr/bin/env python3
"""
Wan Lighting Model Downloader for ComfyUI with Xet Storage compatibility
This script tries to download via Xet first, then falls back to manual download.
"""

import os
import requests
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

# Configuration - UPDATED PATH according to workspace structure
COMFYUI_PATH = "/workspace/ComfyUI"
MODEL_URLS = [
    "https://huggingface.co/bullerwins/Wan2.2-I2V-A14B-GGUF/resolve/main/wan2.2_i2v_high_noise_14B_Q6_K.gguf",
    "https://huggingface.co/bullerwins/Wan2.2-I2V-A14B-GGUF/resolve/main/wan2.2_i2v_low_noise_14B_Q6_K.gguf",
    "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors",
    "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors",
    "https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/Lightx2v/lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors"
]

# Xet repository mapping (HuggingFace URL to Xet path)
XET_REPO_MAPPING = {
    "Comfy-Org/Wan_2.2_ComfyUI_Repackaged": "xet://XetHub/ComfyUI-Models/main/Comfy-Org/Wan_2.2_ComfyUI_Repackaged",
    "Kijai/WanVideo_comfy": "xet://XetHub/ComfyUI-Models/main/Kijai/WanVideo_comfy",
    "bullerwins/Wan2.2-I2V-A14B-GGUF": "xet://XetHub/ComfyUI-Models/main/bullerwins/Wan2.2-I2V-A14B-GGUF"
}

def check_xet_installed():
    """Check if Xet is installed and available"""
    try:
        result = subprocess.run(["xet", "--version"], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        return False

def get_xet_path(url):
    """Convert HuggingFace URL to Xet path if available"""
    for hf_path, xet_path in XET_REPO_MAPPING.items():
        if hf_path in url:
            # Replace the base URL with Xet path
            relative_path = url.split(hf_path)[1]
            return f"{xet_path}{relative_path}"
    return None

def download_with_xet(xet_url, destination):
    """Download a file using Xet storage"""
    try:
        print(f"🦄 Attempting Xet download: {os.path.basename(xet_url)}")
        
        # Create destination directory
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        
        # Use xet cp command to download with real-time output
        cmd = ["xet", "cp", xet_url, destination]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        
        if result.returncode == 0:
            print(f"✅ Xet download successful: {os.path.basename(destination)}")
            return True
        else:
            print(f"⚠️ Xet download failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Xet download timed out")
        return False
    except Exception as e:
        print(f"❌ Xet download error: {e}")
        return False

def download_with_requests(url, destination):
    """Download a file using requests library (fallback)"""
    try:
        print(f"⬇️ Manual download: {os.path.basename(url)}")
        
        # Create destination directory
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        
        # Stream the download to handle large files
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Get file size for progress tracking
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        # Download the file
        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    # Show progress
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"   Progress: {progress:.1f}% ({downloaded}/{total_size} bytes)", end='\r')
        
        print(f"\n✅ Manual download successful: {os.path.basename(destination)}")
        return True
        
    except Exception as e:
        print(f"\n❌ Manual download error {url}: {e}")
        return False

def create_directories():
    """Create the required directory structure in ComfyUI"""
    directories = [
        "models/diffusion_models",  # For GGUF models and other diffusion models
        "models/vae",
        "models/clip"
    ]
    
    for directory in directories:
        full_path = os.path.join(COMFYUI_PATH, directory)
        os.makedirs(full_path, exist_ok=True)
        print(f"✅ Created directory: {full_path}")

def get_destination_path(url):
    """Determine the destination path based on URL content"""
    filename = os.path.basename(urlparse(url).path)
    
    # GGUF models go to models/diffusion_models/
    if "wan2.2_i2v" in url and url.endswith(".gguf"):
        return os.path.join(COMFYUI_PATH, "models", "diffusion_models", filename)
    # Other diffusion models
    elif "diffusion_models" in url or "Lightx2v" in url:
        return os.path.join(COMFYUI_PATH, "models", "diffusion_models", filename)
    elif "vae" in url:
        return os.path.join(COMFYUI_PATH, "models", "vae", filename)
    elif "text_encoders" in url:
        return os.path.join(COMFYUI_PATH, "models", "clip", filename)
    else:
        return os.path.join(COMFYUI_PATH, "models", filename)

def install_requests_if_needed():
    """Check if requests is installed, install if needed"""
    try:
        import requests
        return True
    except ImportError:
        print("📦 Installing requests library...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
            import requests
            return True
        except:
            print("❌ Failed to install requests library")
            return False

def main():
    """Main function to download all model files"""
    print("=" * 60)
    print("🚀 Wan Lighting Model Downloader for ComfyUI")
    print("🦄 With Xet Storage compatibility")
    print("=" * 60)
    
    # Check if ComfyUI path exists
    if not os.path.exists(COMFYUI_PATH):
        print(f"❌ ComfyUI path not found: {COMFYUI_PATH}")
        print("Please update the COMFYUI_PATH variable in the script")
        return
    
    # Install requests if needed
    if not install_requests_if_needed():
        print("❌ Requests library is required for fallback download")
        return
    
    # Check if Xet is available
    xet_available = check_xet_installed()
    if xet_available:
        print("✅ Xet storage is available")
    else:
        print("⚠️ Xet storage not available, using manual download")
    
    # Create necessary directories
    create_directories()
    
    # Download all files
    print("\n📦 Starting downloads...")
    success_count = 0
    xet_success_count = 0
    manual_success_count = 0
    
    for url in MODEL_URLS:
        destination = get_destination_path(url)
        
        # Check if file already exists
        if os.path.exists(destination):
            file_size = os.path.getsize(destination)
            print(f"⚠️ File already exists ({file_size} bytes), skipping: {os.path.basename(destination)}")
            success_count += 1
            continue
        
        # Try Xet first if available
        downloaded = False
        if xet_available:
            xet_url = get_xet_path(url)
            if xet_url:
                if download_with_xet(xet_url, destination):
                    success_count += 1
                    xet_success_count += 1
                    downloaded = True
                else:
                    print(f"⚠️ Xet download failed, trying manual download for: {os.path.basename(url)}")
            else:
                print(f"ℹ️ No Xet mapping found for: {os.path.basename(url)}")
        
        # Fall back to manual download if Xet failed or not available
        if not downloaded:
            if download_with_requests(url, destination):
                success_count += 1
                manual_success_count += 1
            else:
                print(f"❌ Failed to download: {os.path.basename(url)}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Download Summary:")
    print("=" * 60)
    print(f"Total files: {len(MODEL_URLS)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {len(MODEL_URLS) - success_count}")
    print(f"Via Xet: {xet_success_count}")
    print(f"Via Manual: {manual_success_count}")
    
    if success_count == len(MODEL_URLS):
        print("\n🎉 All files downloaded successfully!")
        print("\n📍 Files are located in:")
        print(f"   Diffusion models: {COMFYUI_PATH}/models/diffusion_models/")
        print(f"   VAE models: {COMFYUI_PATH}/models/vae/")
        print(f"   Text encoders: {COMFYUI_PATH}/models/clip/")
    else:
        print("\n⚠️ Some files failed to download. You may need to run the script again.")

if __name__ == "__main__":
    main()
