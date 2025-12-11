import socket
import json
import struct
import hmac
import hashlib
from datetime import datetime

# Client config (change host/port to match server)
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9000

# Shared secret must match server
SHARED_SECRET = b"very_secret_key_change_me"

def compute_hmac_for_applicant(applicant_obj: dict) -> str:
    # Use deterministic JSON: sorted keys, no spaces
    b = json.dumps(applicant_obj, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return hmac.new(SHARED_SECRET, b, hashlib.sha256).hexdigest()

def send_payload(payload: bytes):
    with socket.create_connection((SERVER_HOST, SERVER_PORT), timeout=10) as s:
        header = struct.pack(">I", len(payload))
        s.sendall(header + payload)
        # read 4-byte len
        raw_len = s.recv(4)
        if not raw_len:
            raise RuntimeError("No response from server")
        msg_len = struct.unpack(">I", raw_len)[0]
        data = b""
        while len(data) < msg_len:
            chunk = s.recv(msg_len - len(data))
            if not chunk:
                break
            data += chunk
        return json.loads(data.decode("utf-8"))

def collect_input(prompt, required=True):
    while True:
        v = input(prompt).strip()
        if v == "" and required:
            print("This field is required.")
            continue
        return v

def main():
    print("DBS Application Client\nPlease enter applicant information.")
    name = collect_input("Name: ")
    address = collect_input("Address: ")
    qualifications = collect_input("Educational qualifications: ")
    # course should be one of three choices
    courses = ["MSc in Cyber Security", "MSc Information Systems & computing", "MSc Data Analytics"]
    print("Choose course:")
    for i,c in enumerate(courses,1):
        print(f"{i}. {c}")
    while True:
        sel = input("Course (1-3): ").strip()
        if sel in ("1","2","3"):
            course = courses[int(sel)-1]
            break
        else:
            print("Invalid option, choose 1-3.")
    while True:
        start_year = input("Intended start year (e.g., 2025): ").strip()
        start_month = input("Intended start month (1-12): ").strip()
        try:
            sy = int(start_year)
            sm = int(start_month)
            if 1 <= sm <= 12:
                break
            else:
                print("Month must be 1-12.")
        except:
            print("Invalid year/month. Try again.")

    applicant = {
        "name": name,
        "address": address,
        "qualifications": qualifications,
        "course": course,
        "start_year": sy,
        "start_month": sm
    }

    client_id = f"cli-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    hmac_hex = compute_hmac_for_applicant(applicant)
    payload_obj = {"applicant": applicant, "client_id": client_id, "hmac": hmac_hex}
    payload_bytes = json.dumps(payload_obj, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

    print("\nConnecting to server...")
    try:
        resp = send_payload(payload_bytes)
    except Exception as e:
        print("Failed to contact server:", e)
        return

    if resp.get("status") == "ok":
        print("Application submitted successfully.")
        print("Your application number is:", resp.get("app_no"))
    else:
        print("Server returned error:", resp.get("message"))

if __name__ == "__main__":
 main()
