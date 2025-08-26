import os
import requests
import subprocess
import urllib.parse
from pathlib import Path

def download_file(url, destination):
    """Download a file from URL to destination with progress tracking"""
    try:
        print(f"Downloading: {url}")
        response = requests.get(url, stream=True)
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

def get_filename_from_url(url):
    """Extract filename from URL"""
    parsed_url = urllib.parse.urlparse(url)
    if 'content-disposition' in requests.head(url).headers:
        content_disp = requests.head(url).headers['content-disposition']
        if 'filename=' in content_disp:
            return content_disp.split('filename=')[1].strip('"')
    
    # For Civitai URLs, try to extract from query parameters or path
    if 'civitai.com' in url:
        path_parts = parsed_url.path.split('/')
        if 'models' in path_parts:
            model_index = path_parts.index('models')
            if len(path_parts) > model_index + 1:
                model_id = path_parts[model_index + 1]
                return f"model_{model_id}.safetensors"
    
    # Fallback: use last part of path
    return os.path.basename(parsed_url.path) or "downloaded_file.safetensors"

def setup_directories():
    """Create necessary directories in /workspace"""
    base_dir = "/workspace"
    webui_dir = os.path.join(base_dir, "stable-diffusion-webui")
    
    directories = {
        'models': os.path.join(webui_dir, "models", "Stable-diffusion"),
        'loras': os.path.join(webui_dir, "models", "Lora"),
        'extensions': os.path.join(webui_dir, "extensions")
    }
    
    for dir_path in directories.values():
        os.makedirs(dir_path, exist_ok=True)
        print(f"Created directory: {dir_path}")
    
    return directories

def download_models(directories):
    """Download all models"""
    model_urls = [
        "https://civitai.com/api/download/models/351306?type=Model&format=SafeTensor&size=full&fp=fp16",
        "https://civitai.com/api/download/models/146134?type=Model&format=SafeTensor&size=pruned&fp=fp16",
        "https://civitai.com/api/download/models/222240?type=Model&format=SafeTensor&size=pruned&fp=fp16",
        "https://civitai.com/api/download/models/1920896?type=Model&format=SafeTensor&size=full&fp=fp16",
        "https://civitai.com/api/download/models/2071650?type=Model&format=SafeTensor&size=pruned&fp=fp16",
        "https://civitai.com/api/download/models/1767402?type=Model&format=SafeTensor&size=pruned&fp=fp16",
        "https://civitai.com/api/download/models/770375?type=Model&format=SafeTensor&size=pruned&fp=fp16",
        "https://civitai.com/api/download/models/1366495?type=Model&format=SafeTensor&size=full&fp=fp16",
        "https://civitai.com/api/download/models/1075446?type=Model&format=SafeTensor&size=pruned&fp=fp16"
    ]
    
    for url in model_urls:
        filename = get_filename_from_url(url)
        destination = os.path.join(directories['models'], filename)
        download_file(url, destination)

def download_loras(directories):
    """Download all LORAs"""
    lora_urls = [
        "https://civitai.com/api/download/models/382152?type=Model&format=SafeTensor",
        "https://civitai.com/api/download/models/244808?type=Model&format=SafeTensor"
    ]
    
    for url in lora_urls:
        filename = get_filename_from_url(url)
        destination = os.path.join(directories['loras'], filename)
        download_file(url, destination)

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
    
    # Setup directories
    directories = setup_directories()
    
    print("\n=== Downloading Models ===")
    download_models(directories)
    
    print("\n=== Downloading LORAs ===")
    download_loras(directories)
    
    print("\n=== Installing Extensions ===")
    install_extensions(directories)
    
    print("\n=== Download and installation completed! ===")
    print("Files are located in /workspace/stable-diffusion-webui/")

if __name__ == "__main__":
    main()
