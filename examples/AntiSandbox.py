import psutil
import os

def check_environment():
    """Checks for common sandbox/VM indicators to decide whether to run."""
    # 1. Check for low RAM (Sandboxes often have < 4GB)
    vm_detected = False
    mem = psutil.virtual_memory()
    if mem.total / (1024**3) < 4:
        vm_detected = True

    # 2. Check for low CPU count (Sandboxes often have 1 or 2 cores)
    if os.cpu_count() < 2:
        vm_detected = True

    # 3. Check for common sandbox filenames
    sandbox_files = ["C:\\windows\\System32\\Drivers\\Vmmouse.sys", "/usr/bin/cuckoo"]
    for f in sandbox_files:
        if os.path.exists(f):
            vm_detected = True

    if vm_detected:
        print("Analysis environment detected. Terminating.")
        return True
    
    print("Environment appears to be a physical machine. Proceeding...")
    return False

if __name__ == "__main__":
    check_environment()