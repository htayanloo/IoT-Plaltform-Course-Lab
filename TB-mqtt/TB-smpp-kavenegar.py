import socket
import struct

def parse_pdu(data):
    # SMPP PDU parsing is more complex in real scenarios.
    # This is a simplified version that assumes the PDU is a submit_sm and tries to extract the message.
    try:
        # Extracting length and command_id from PDU header
        command_length, command_id = struct.unpack('>II', data[:8])
        
        # Just a basic check to print the message for submit_sm (command_id 0x00000004)
        if command_id == 0x00000004:
            # Extract short_message from the submit_sm PDU
            # This is oversimplified and assumes fixed positions, which may not hold for all PDUs.
            sm_length = data[-1]  # Last byte is the short message length
            message = data[-1 - sm_length:-1].decode()  # Extracting message
            print("Received message:", message)
    except Exception as e:
        print("Error parsing PDU:", e)

def start_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Server listening on {host}:{port}")

        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    parse_pdu(data)

if __name__ == "__main__":
    start_server('0.0.0.0', 2775)
