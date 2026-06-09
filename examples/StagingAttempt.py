import os
from glob import glob

def list_sensitive_files():
    """Searches for files with extensions that often contain sensitive data."""
    # Define interesting file extensions
    sensitive_extensions = ['*.docx', '*.xlsx', '*.pptx', '*.pdf', '*.txt', '*.p12', '*.pem', '*.sql']
    
    # Define paths to search, avoiding large system directories for this example
    search_paths = [
        os.path.expanduser('~'),              # User's Home directory
        os.path.join(os.path.expanduser('~'), 'Documents'),
        os.path.join(os.path.expanduser('~'), 'Downloads'),
        './'                                  # Current working directory
    ]
    
    found_files = []
    
    print("Starting sensitive file discovery...")
    for path in search_paths:
        if not os.path.isdir(path):
            continue
        for ext in sensitive_extensions:
            # os.walk can be slow, using glob for a faster approach that might look different
            # but is still file enumeration behavior.
            # Using glob with recursive=True is an efficient way to find files and will be
            # caught by file system hooks.
            found_files.extend(glob(os.path.join(path, '**', ext), recursive=True))
    
    if found_files:
        print(f"Found {len(found_files)} potentially sensitive files.")
        # In a sandbox, writing this list to a file or trying to read them
        # creates a huge signal of malicious intent.
        with open("sensitive_files_manifest.txt", "w") as f:
            for file_path in found_files:
                f.write(f"{file_path}\n")
        print("Manifest written to sensitive_files_manifest.txt")
    else:
        print("No sensitive files found in common directories.")

if __name__ == "__main__":
    list_sensitive_files()