import socket
import platform

def get_network_config():
    """Gathers local network interface information."""
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = "127.0.0.1"
        
    print(f"Hostname: {hostname}")
    print(f"Local IP: {local_ip}")
    print(f"Operating System: {platform.system()} {platform.release()}")
    
    # Check if we can reach a common DNS server (Google)
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        print("Internet connectivity: Connected")
    except OSError:
        print("Internet connectivity: Offline")

if __name__ == "__main__":
    get_network_config()