import os
import platform
import json

def get_system_summary():
    """Gathers basic system information without making connections."""
    try:
        info = {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "hostname": platform.node(),
            "username": os.getlogin() if hasattr(os, 'getlogin') else 'unknown',
            "processor": platform.processor(),
            "current_working_dir": os.getcwd()
        }
        # In a sandbox, writing this to a file would create a strong signal
        with open("system_summary_log.txt", "w") as f:
            json.dump(info, f, indent=4)
        print("System summary logged to system_summary_log.txt")
    except Exception as e:
        print(f"Error gathering info: {e}")

if __name__ == "__main__":
    get_system_summary()