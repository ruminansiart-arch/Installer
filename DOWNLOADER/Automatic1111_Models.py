import os
import requests
import subprocess
import urllib.parse
from pathlib import Path

# Add your CivitAI API key here if you have one
CIVITAI_API_KEY = os.environ.get('CIVITAI_API_KEY', '')

def download_file(url, destination, headers=None):
    """Download a file from URL to destination with progress tracking"""
    try:
        print(f"Downloading: {url}")
        
        if headers is None:
            headers = {}
            
        response = requests.get(url, stream=True, headers=headers)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"Progress: {progress:.1f}% ({downloaded}/{total_size} bytes)", end='\r')
        
        print(f"\nDownload completed: {destination}")
        return True
        
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def setup_directories():
    """Create necessary directories in /workspace"""
    base_dir = "/workspace"
    webui_dir = os.path.join(base_dir, "stable-diffusion-webui")
    
    directories = {
        'models': os.path.join(webui_dir, "models", "Stable-diffusion"),
        'loras': os.path.join(webui_dir, "models", "Lora"),
        'extensions': os.path.join(webui_dir, "extensions"),
        'codeformer': os.path.join(webui_dir, "models", "Codeformer"),
        'controlnet': os.path.join(webui_dir, "models", "ControlNet"),
        'esrgan': os.path.join(webui_dir, "models", "ESRGAN"),
        'remacri': os.path.join(webui_dir, "models", "Remacri"),
        'dfpgan': os.path.join(webui_dir, "models", "DFPGAN"),
        'realesrgan': os.path.join(webui_dir, "models", "RealESRGAN")
    }
    
    for dir_path in directories.values():
        os.makedirs(dir_path, exist_ok=True)
        print(f"Created directory: {dir_path}")
    
    return directories

def download_models(directories):
    """Download all Stable-diffusion models with proper filenames"""
    model_mapping = {
        # Public models that work without authentication
        "https://civitai.com/api/download/models/351306?type=Model&format=SafeTensor&size=full&fp=fp16": "DreamShaper XL.safetensors",
        "https://civitai.com/api/download/models/146134?type=Model&format=SafeTensor&size=pruned&fp=fp16": "Fantexi_realistic.safetensors",
        "https://civitai.com/api/download/models/222240?type=Model&format=SafeTensor&size=pruned&fp=fp16": "majicMIX alpha.safetensors",
        "https://civitai.com/api/download/models/1767402?type=Model&format=SafeTensor&size=pruned&fp=fp16": "WAI-ANI-NSFW-PONYXL.safetensors",
        "https://civitai.com/api/download/models/1075446?type=Model&format=SafeTensor&size=pruned&fp=fp16": "Realism By Stable Yogi.safetensors",
        
        # Models that might require authentication - will try with API key if available
        "https://civitai.com/api/download/models/1920896?type=Model&format=SafeTensor&size=full&fp=fp16": "Pony Realism XL.safetensors",
        "https://civitai.com/api/download/models/2071650?type=Model&format=SafeTensor&size=pruned&fp=fp16": "CyberRealistic Pony.safetensors",
        "https://civitai.com/api/download/models/1366495?type=Model&format=SafeTensor&size=full&fp=fp16": "iNiverse Mix(SFW & NSFW).safetensors",
    }
    
    headers = {}
    if CIVITAI_API_KEY:
        headers = {"Authorization": f"Bearer {CIVITAI_API_KEY}"}
        print("Using CivitAI API key for authentication")
    
    for url, filename in model_mapping.items():
        destination = os.path.join(directories['models'], filename)
        if not os.path.exists(destination):
            success = download_file(url, destination, headers)
            if not success and CIVITAI_API_KEY:
                print(f"Failed to download with API key, trying without...")
                download_file(url, destination)  # Try without auth headers
        else:
            print(f"File already exists: {destination}")

def download_codeformer(directories):
    """Download Codeformer models"""
    codeformer_mapping = {
        "https://huggingface.co/alexgenovese/facerestore/resolve/a957c0a70e7dfa88fdde05dcc8d7657feb17b8a3/codeformer.pth?download=true": "codeformer.pth"
    }
    
    for url, filename in codeformer_mapping.items():
        destination = os.path.join(directories['codeformer'], filename)
        if not os.path.exists(destination):
            download_file(url, destination)
        else:
            print(f"File already exists: {destination}")

def download_controlnet(directories):
    """Download ControlNet models"""
    controlnet_mapping = {
        "https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/control_depth-fp16.safetensors?download=true": "control_depth-fp16.safetensors",
        "https://huggingface.co/StableDiffusionVN/XLControlnet/resolve/663185e727e22d694a8d58ce574bcc3fec120383/control_instant_id_sdxl.safetensors?download=true": "control_instant_id_sdxl.safetensors",
        "https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11f1p_sd15_depth.pth?download=true": "control_v11f1p_sd15_depth.pth",
        "https://huggingface.co/Aitrepreneur/InstantiDA1111/resolve/main/ip-adapter_instant_id_sdxl.bin?download=true": "ip-adapter_instant_id_sdxl.bin"
    }
    
    for url, filename in controlnet_mapping.items():
        destination = os.path.join(directories['controlnet'], filename)
        if not os.path.exists(destination):
            download_file(url, destination)
        else:
            print(f"File already exists: {destination}")

def download_esrgan(directories):
    """Download ESRGAN models"""
    esrgan_mapping = {
        "https://huggingface.co/lokCX/4x-Ultrasharp/resolve/main/4x-UltraSharp.pth?download=true": "4x-UltraSharp.pth",
        "https://huggingface.co/ffxvs/upscaler/resolve/f8edf6d7f286acdd70178a6ff0c736fc592e818e/ESRGAN_4x.pth?download=true": "ESRGAN_4x.pth",
        "https://huggingface.co/dtarnow/UPscaler/resolve/main/RealESRGAN_x2plus.pth?download=true": "RealESRGAN_x2plus.pth"
    }
    
    for url, filename in esrgan_mapping.items():
        destination = os.path.join(directories['esrgan'], filename)
        if not os.path.exists(destination):
            download_file(url, destination)
        else:
            print(f"File already exists: {destination}")

def download_remacri(directories):
    """Download Remacri models"""
    remacri_mapping = {
        "https://huggingface.co/dtarnow/UPscaler/resolve/main/4x_foolhardy_Remacri.pth?download=true": "4x_foolhardy_Remacri.pth"
    }
    
    for url, filename in remacri_mapping.items():
        destination = os.path.join(directories['remacri'], filename)
        if not os.path.exists(destination):
            download_file(url, destination)
        else:
            print(f"File already exists: {destination}")

def download_dfpgan(directories):
    """Download DFPGAN models"""
    dfpgan_mapping = {
        "https://huggingface.co/xjyplayer/stable-diffusion-models/resolve/bd90619e26e9acf4629018bacc93b8815cbcbb74/detection_Resnet50_Final.pth?download=true": "detection_Resnet50_Final.pth",
        "https://huggingface.co/gmk123/GFPGAN/resolve/main/GFPGANv1.4.pth?download=true": "GFPGANv1.4.pth",
        "https://huggingface.co/gmk123/GFPGAN/resolve/main/parsing_parsenet.pth?download=true": "parsing_parsenet.pth",
        "https://huggingface.co/gmk123/GFPGAN/resolve/main/alignment_WFLW_4HG.pth?download=true": "alignment_WFLW_4HG.pth"
    }
    
    for url, filename in dfpgan_mapping.items():
        destination = os.path.join(directories['dfpgan'], filename)
        if not os.path.exists(destination):
            download_file(url, destination)
        else:
            print(f"File already exists: {destination}")

def download_realesrgan(directories):
    """Download RealESRGAN models"""
    realesrgan_mapping = {
        "https://huggingface.co/lllyasviel/Annotators/resolve/main/RealESRGAN_x4plus.pth?download=true": "RealESRGAN_x4plus.pth",
        "https://huggingface.co/ac-pill/upscale_models/resolve/main/RealESRGAN_x4plus_anime_6B.pth?download=true": "RealESRGAN_x4plus_anime_6B.pth"
    }
    
    for url, filename in realesrgan_mapping.items():
        destination = os.path.join(directories['realesrgan'], filename)
        if not os.path.exists(destination):
            download_file(url, destination)
        else:
            print(f"File already exists: {destination}")

def download_loras(directories):
    """Download all LORAs with proper filenames"""
    lora_mapping = {
        "https://civitai.com/api/download/models/382152?type=Model&format=SafeTensor": "ExpressiveH.safetensors",
        "https://civitai.com/api/download/models/244808?type=Model&format=SafeTensor": "All Disney Princess XL LoRA Model.safetensors"
    }
    
    headers = {}
    if CIVITAI_API_KEY:
        headers = {"Authorization": f"Bearer {CIVITAI_API_KEY}"}
    
    for url, filename in lora_mapping.items():
        destination = os.path.join(directories['loras'], filename)
        if not os.path.exists(destination):
            success = download_file(url, destination, headers)
            if not success and CIVITAI_API_KEY:
                print(f"Failed to download with API key, trying without...")
                download_file(url, destination)  # Try without auth headers
        else:
            print(f"File already exists: {destination}")

def install_extensions(directories):
    """Install all extensions using git"""
    extension_urls = [
        "https://github.com/Bing-su/adetailer.git",
        "https://github.com/Avaray/lora-keywords-finder.git",
        "https://github.com/Mikubill/sd-webui-controlnet.git",
        "https://github.com/tritant/sd-webui-creaprompt.git",
        "https://github.com/MINENEMA/sd-webui-quickrecents.git"
    ]
    
    for url in extension_urls:
        try:
            # Extract repository name from URL
            repo_name = url.split('/')[-1].replace('.git', '')
            extension_dir = os.path.join(directories['extensions'], repo_name)
            
            if os.path.exists(extension_dir):
                print(f"Extension already exists: {repo_name}")
                continue
                
            print(f"Installing extension: {repo_name}")
            
            # Clone the repository
            result = subprocess.run([
                'git', 'clone', '--depth', '1', url, extension_dir
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"Successfully installed: {repo_name}")
            else:
                print(f"Failed to install {repo_name}: {result.stderr}")
                
        except Exception as e:
            print(f"Error installing extension {url}: {e}")

def main():
    print("Setting up Automatic1111 downloader for /workspace...")
    
    if CIVITAI_API_KEY:
        print("CivitAI API key detected")
    else:
        print("No CivitAI API key found. Some models may require authentication.")
    
    # Setup directories
    directories = setup_directories()
    
    print("\n=== Downloading Stable-diffusion Models ===")
    download_models(directories)
    
    print("\n=== Downloading Codeformer Models ===")
    download_codeformer(directories)
    
    print("\n=== Downloading ControlNet Models ===")
    download_controlnet(directories)
    
    print("\n=== Downloading ESRGAN Models ===")
    download_esrgan(directories)
    
    print("\n=== Downloading Remacri Models ===")
    download_remacri(directories)
    
    print("\n=== Downloading DFPGAN Models ===")
    download_dfpgan(directories)
    
    print("\n=== Downloading RealESRGAN Models ===")
    download_realesrgan(directories)
    
    print("\n=== Downloading LORAs ===")
    download_loras(directories)
    
    print("\n=== Installing Extensions ===")
    install_extensions(directories)
    
    print("\n=== Download and installation completed! ===")
    print("Files are located in /workspace/stable-diffusion-webui/")
    
    # List failed downloads
    print("\nNote: Some models may have failed to download due to authentication requirements.")
    print("You may need to:")
    print("1. Set the CIVITAI_API_KEY environment variable with your CivitAI API key")
    print("2. Or manually download these models from CivitAI and place them in the appropriate folders")

if __name__ == "__main__":
    main()
