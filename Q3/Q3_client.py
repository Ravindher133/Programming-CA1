
import socket
import ssl
import json
import struct

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8443
CA_CERT = None  #we will skip verifying

def send_message(sock, payload_bytes):
    msg = struct.pack(">I", len(payload_bytes)) + payload_bytes
    sock.sendall(msg)

def recvall(sock, n):
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            raise ConnectionError("Connection closed while receiving data")
        data += packet
    return data

def recv_message(sock):
    raw_len = recvall(sock, 4)
    (msg_len,) = struct.unpack(">I", raw_len)
    if msg_len == 0:
        return b''
    return recvall(sock, msg_len)

def collect_input():
    print("=== DBS Application Client ===")
    name = input("Full name: ").strip()
    address = input("Address: ").strip()
    qualifications = input("Educational qualifications: ").strip()
    print("Choose course: ")
    print("1) MSc Cyber Security")
    print("2) MSc Information Systems & computing")
    print("3) MSc Data Analytics")
    course_sel = input("Enter 1/2/3: ").strip()
    course_map = {"1": "MSc Cyber Security",
                  "2": "MSc Information Systems & computing",
                  "3": "MSc Data Analytics"}
    course = course_map.get(course_sel, "")
    start_year = input("Intended start year (e.g. 2025): ").strip()
    start_month = input("Intended start month (1-12): ").strip()

    payload = {
        "name": name,
        "address": address,
        "qualifications": qualifications,
        "course": course,
        "start_year": start_year,
        "start_month": start_month
    }
    return payload

def main():
    payload = collect_input()
    data_bytes = json.dumps(payload).encode('utf-8')

    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    if CA_CERT:
        context.load_verify_locations(CA_CERT)
    else:
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

    with socket.create_connection((SERVER_HOST, SERVER_PORT)) as sock:
        with context.wrap_socket(sock, server_hostname=SERVER_HOST) as ssock:
            send_message(ssock, data_bytes)
            resp_bytes = recv_message(ssock)
            resp = json.loads(resp_bytes.decode('utf-8'))
            if resp.get("status") == "ok":
                print(f"Application submitted successfully! Your application number: {resp.get('application_number')}")
            else:
                print("Server returned error:", resp.get("message"))

if __name__ == "__main__":
    main()
