
import socket
import ssl
import threading
import json
import sqlite3
import struct
import datetime
import os

DB_PATH = "applicants.db"
CERTFILE = "server.crt"
KEYFILE = "server.key"
LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = 8443

#---- Database helpers ----------
def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS applicants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_number TEXT UNIQUE,
            name TEXT NOT NULL,
            address TEXT,
            qualifications TEXT,
            course TEXT,
            start_year INTEGER,
            start_month INTEGER,
            submitted_at TEXT
        )
    ''')
    conn.commit()
    return conn

def generate_application_number(conn, year, month):
    # Insert a stub row to get autoincrement id, then update application_number
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO applicants (application_number, name, address, qualifications, course, start_year, start_month, submitted_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', ("", "", "", "", "", year, month, datetime.datetime.utcnow().isoformat()))
    conn.commit()
    rowid = cur.lastrowid
    app_num = f"DBS-{year:04d}-{month:02d}-{rowid:06d}"
    cur.execute('UPDATE applicants SET application_number = ? WHERE id = ?', (app_num, rowid))
    conn.commit()
    return app_num, rowid

def store_applicant(conn, rowid, data):
    cur = conn.cursor()
    cur.execute('''
        UPDATE applicants
        SET name = ?, address = ?, qualifications = ?, course = ?, start_year = ?, start_month = ?, submitted_at = ?
        WHERE id = ?
    ''', (
        data.get("name"),
        data.get("address"),
        data.get("qualifications"),
        data.get("course"),
        int(data.get("start_year")),
        int(data.get("start_month")),
        datetime.datetime.utcnow().isoformat(),
        rowid
    ))
    conn.commit()

#----- Networking helpers ----------
def recvall(sock, n):
    """Receive exactly n bytes, or raise"""
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            raise ConnectionError("Connection closed while receiving data")
        data += packet
    return data

def recv_message(sock):
    # read 4-byte length prefix
    raw_len = recvall(sock, 4)
    (msg_len,) = struct.unpack(">I", raw_len)
    if msg_len == 0:
        return b''
    return recvall(sock, msg_len)

def send_message(sock, payload_bytes):
    # prefix with 4-byte big-endian length
    msg = struct.pack(">I", len(payload_bytes)) + payload_bytes
    sock.sendall(msg)

#----- Validation ----------
ALLOWED_COURSES = {
    "MSc Cyber Security",
    "MSc Information Systems & computing",
    "MSc Data Analytics"
}

def validate_applicant(data):
    required = ["name", "qualifications", "course", "start_year", "start_month"]
    for k in required:
        if k not in data or str(data[k]).strip() == "":
            return False, f"Missing required field: {k}"

    try:
        year = int(data["start_year"])
        month = int(data["start_month"])
        if not (2000 <= year <= 2100) or not (1 <= month <= 12):
            return False, "Invalid start year/month"
    except ValueError:
        return False, "start_year and start_month must be integers"

    if data["course"] not in ALLOWED_COURSES:
        return False, f"Invalid course. Allowed: {', '.join(ALLOWED_COURSES)}"

    # name length check as basic sanitization
    if len(data["name"]) > 200:
        return False, "Name too long"

    return True, "OK"

#--- Client handler ----------
def handle_client(connstream, client_addr, db_conn):
    try:
        raw = recv_message(connstream)
        req = json.loads(raw.decode('utf-8'))
    except Exception as e:
        resp = {"status": "error", "message": f"Invalid request: {e}"}
        send_message(connstream, json.dumps(resp).encode('utf-8'))
        connstream.close()
        return

    valid, msg = validate_applicant(req)
    if not valid:
        resp = {"status": "error", "message": msg}
        send_message(connstream, json.dumps(resp).encode('utf-8'))
        connstream.close()
        return

    # Generate application number (insert placeholder row and get id)
    year = int(req["start_year"])
    month = int(req["start_month"])
    try:
        app_num, rowid = generate_application_number(db_conn, year, month)
        # Store actual applicant details
        store_applicant(db_conn, rowid, req)
    except Exception as e:
        resp = {"status": "error", "message": f"Database error: {e}"}
        send_message(connstream, json.dumps(resp).encode('utf-8'))
        connstream.close()
        return

    resp = {"status": "ok", "application_number": app_num}
    send_message(connstream, json.dumps(resp).encode('utf-8'))
    connstream.close()

def main():
    if not os.path.exists(CERTFILE) or not os.path.exists(KEYFILE):
        print("TLS certificate or key not found. Create server.crt and server.key before running.")
        return

    db_conn = init_db()
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=CERTFILE, keyfile=KEYFILE)

    bindsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bindsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    bindsock.bind((LISTEN_HOST, LISTEN_PORT))
    bindsock.listen(5)
    print(f"Server listening on {LISTEN_HOST}:{LISTEN_PORT} (TLS)")

    try:
        while True:
            newsock, addr = bindsock.accept()
            try:
                connstream = context.wrap_socket(newsock, server_side=True)
            except ssl.SSLError as e:
                print(f"TLS handshake failed from {addr}: {e}")
                newsock.close()
                continue

            t = threading.Thread(target=handle_client, args=(connstream, addr, db_conn), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("Shutting down server.")
    finally:
        bindsock.close()
        db_conn.close()

if __name__ == "__main__":
    main()
