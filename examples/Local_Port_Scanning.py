import socket
import threading

def scan_port(target, port):
    """Attempts a single socket connection to a specific port."""
    try:
        # Create a TCP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        # Attempt to connect
        result = s.connect_ex((target, port))
        if result == 0:
            # We found an open port
            pass
        s.close()
    except:
        pass

def local_port_scan():
    """Scans common ports on localhost to find potential services."""
    target_ip = "127.0.0.1"
    # A list of common ports to check
    common_ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 443, 445, 1433, 3306, 3389, 8080]
    
    print(f"Starting local port scan on {target_ip}...")
    threads = []
    for port in common_ports:
        # Use threading to make the scan faster, which sandbox monitors might note
        t = threading.Thread(target=scan_port, args=(target_ip, port))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    print("Scan completed.")

if __name__ == "__main__":
    local_port_scan()