import socket
import threading
import json
import struct
import sqlite3
import time
import hmac
import hashlib
import os
import random
from datetime import datetime

# Configuration
HOST = "0.0.0.0"      # listen on all interfaces (change to '127.0.0.1' for local-only)
PORT = 9000
DB_FILE = "applications.db"
# Shared secret for HMAC (change to a strong secret before submission)
SHARED_SECRET = b"very_secret_key_change_me"

# Ensure DB and table exist
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        app_no TEXT UNIQUE,
        name TEXT,
        address TEXT,
        qualifications TEXT,
        course TEXT,
        start_year INTEGER,
        start_month INTEGER,
        client_id TEXT,
        submitted_at TEXT
    )
    """)
    conn.commit()
    conn.close()

# Generate unique application number
def generate_app_no():
    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    rand4 = f"{random.randint(0, 9999):04d}"
    return f"DBS-{ts}-{rand4}"

# Verify HMAC (payload_bytes is the JSON bytes of applicant portion or whole payload without hmac)
def verify_hmac(payload_bytes: bytes, received_hmac_hex: str) -> bool:
    mac = hmac.new(SHARED_SECRET, payload_bytes, hashlib.sha256).hexdigest()
    return hmac.compare_digest(mac, received_hmac_hex)

# Load applicants into DB
def store_application(applicant: dict, client_id: str) -> str:
    # Validation (server-side)
    name = applicant.get("name", "").strip()
    addr = applicant.get("address", "").strip()
    quals = applicant.get("qualifications", "").strip()
    course = applicant.get("course", "").strip()
    try:
        start_year = int(applicant.get("start_year"))
        start_month = int(applicant.get("start_month"))
    except Exception:
        raise ValueError("Invalid start year/month")

    if not name or not course or not quals:
        raise ValueError("Name, course and qualifications are required")

    app_no = generate_app_no()
    submitted_at = datetime.utcnow().isoformat()

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO applications (app_no, name, address, qualifications, course, start_year, start_month, client_id, submitted_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (app_no, name, addr, quals, course, start_year, start_month, client_id, submitted_at))
    conn.commit()
    conn.close()
    return app_no

# Read exactly n bytes from a socket
def recv_all(conn: socket.socket, n: int) -> bytes:
    data = b""
    while len(data) < n:
        packet = conn.recv(n - len(data))
        if not packet:
            return b""  # connection closed
        data += packet
    return data

def handle_client(conn: socket.socket, addr):
    peer = f"{addr[0]}:{addr[1]}"
    print(f"[+] Connection from {peer}")
    try:
        # Read length prefix (4 bytes)
        raw_len = recv_all(conn, 4)
        if not raw_len:
            print("[-] No data (client closed).")
            return
        msg_len = struct.unpack(">I", raw_len)[0]
        payload = recv_all(conn, msg_len)
        if not payload:
            print("[-] Incomplete payload.")
            return

        # Parse JSON
        try:
            data = json.loads(payload.decode("utf-8"))
        except Exception as e:
            resp = {"status":"error","message":"Invalid JSON"}
            send_response(conn, resp)
            print("[-] Invalid JSON from", peer)
            return

        # Expected structure: {"applicant":{...}, "client_id": "...", "hmac":"..."}
        received_hmac = data.get("hmac", "")
        client_id = data.get("client_id", "unknown")
        applicant_obj = data.get("applicant")
        if applicant_obj is None or not isinstance(applicant_obj, dict):
            send_response(conn, {"status":"error","message":"No applicant data"})
            return

        # Recompute HMAC over the applicant JSON bytes (deterministic)
        # Use compact JSON encoding (sorted keys) to ensure same bytes as client
        applicant_bytes = json.dumps(applicant_obj, separators=(",", ":"), sort_keys=True).encode("utf-8")
        if not verify_hmac(applicant_bytes, received_hmac):
            send_response(conn, {"status":"error","message":"HMAC verification failed"})
            print("[-] HMAC failed for", peer)
            return

        # Store in DB (with validation)
        try:
            app_no = store_application(applicant_obj, client_id)
        except Exception as e:
            send_response(conn, {"status":"error","message":str(e)})
            print("[-] Store error:", e)
            return

        # Success -> send back application number
        send_response(conn, {"status":"ok","app_no":app_no})
        print(f"[+] Stored application {app_no} from {client_id} ({peer})")

    finally:
        conn.close()
        print(f"[.] Connection closed {peer}")

def send_response(conn: socket.socket, obj: dict):
    data = json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    header = struct.pack(">I", len(data))
    conn.sendall(header + data)

def start_server():
    init_db()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen(5)
    print(f"[i] Server listening on {HOST}:{PORT}")

    try:
        while True:
            conn, addr = sock.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("[i] Shutting down server.")
    finally:
        sock.close()

if __name__ == "__main__":
  start_server()