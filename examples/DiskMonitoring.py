import shutil
import os

def check_disk_usage():
    """Checks disk space and lists files in the temporary directory."""
    # Get disk usage for the root directory
    total, used, free = shutil.disk_usage("/")
    
    print(f"Total: {total // (2**30)} GB")
    print(f"Used: {used // (2**30)} GB")
    print(f"Free: {free // (2**30)} GB")

    # List files in /tmp to see if cleanup is needed
    temp_dir = "/tmp"
    if os.path.exists(temp_dir):
        print(f"\nContents of {temp_dir}:")
        files = os.listdir(temp_dir)
        for file in files[:10]: # Limit output
            print(f" - {file}")
    else:
        print("Temp directory not found.")

if __name__ == "__main__":
    check_disk_usage()