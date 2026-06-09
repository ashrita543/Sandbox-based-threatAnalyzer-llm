import os
import shutil
from glob import glob

def simulate_ransomware():
    """Simulates the file encryption behavior of ransomware. IT DOES NOT ENCRYPT. It overwrites."""
    # Using a directory in /tmp/ to keep it safe for sandbox testing.
    # IN YOUR SANDBOX, ENSURE THIS DIRECTORY IS CREATED AND HAS TEST FILES.
    # Ex: mkdir -p /tmp/sandbox_test_files/ && touch /tmp/sandbox_test_files/{doc1.docx,data.xlsx,pic.png}
    target_dir = "/tmp/sandbox_test_files"
    extensions_to_lock = ['*.docx', '*.xlsx', '*.jpg', '*.pdf', '*.txt']
    ransom_note_name = "RANSOM_NOTE_DEMO.txt"
    ransom_note_content = """!!! ALL YOUR FILES HAVE BEEN LOCKED !!!

This is a simulation of ransomware behavior. 
For a real infection, your files would be encrypted.

This text file is a signal your sandbox should detect.

"""

    print(f"Ransomware simulation starting in: {target_dir}")
    
    if not os.path.isdir(target_dir):
        print(f"Error: Target directory {target_dir} not found. Create it with test files.")
        return

    # Counter for files "processed"
    files_processed = 0

    # Walk through the directory and its subdirectories
    for root, _, _ in os.walk(target_dir):
        # Drop a ransom note in every directory - a loud signal
        note_path = os.path.join(root, ransom_note_name)
        try:
            with open(note_path, "w") as note_file:
                note_file.write(ransom_note_content)
        except Exception as e:
            print(f"Failed to write ransom note in {root}: {e}")

        # Find files matching our target extensions
        # glob works differently with full paths, os.walk + simple string manipulation is better for matching extensions here.
        for file in os.listdir(root):
            # Combine root path and filename
            file_path = os.path.join(root, file)
            # Skip directories and our own ransom notes
            if os.path.isdir(file_path) or file == ransom_note_name:
                continue
            
            # Check if file has one of our target extensions
            if any(file.endswith(ext.replace('*', '')) for ext in extensions_to_lock):
                print(f"Processing file: {file_path}")
                try:
                    # In a safe simulation, we just read the file content to generate file-read hooks
                    with open(file_path, "rb") as f:
                        _ = f.read()
                    
                    # To simulate encryption/overwriting:
                    # Instead of actual encryption, we overwrite the first 1024 bytes with dummy data.
                    # This will trigger file modification hooks.
                    # CRITICAL SAFETY NOTE: This OVERWRITES data. Only run in a sandbox on disposable files.
                    with open(file_path, "wb") as f:
                        f.write(b'SANDBOX_SIMULATION_ENCRYPTION_MARKER' + b'\0' * 1024)

                    # Step 2: Rename the file to have a new extension - another very loud signal.
                    new_file_path = file_path + ".simulated_lock"
                    shutil.move(file_path, new_file_path)
                    
                    files_processed += 1
                except Exception as e:
                    print(f"Failed to process file {file_path}: {e}")

    print(f"Simulation complete. {files_processed} files processed, ransom notes dropped.")

if __name__ == "__main__":
    simulate_ransomware()