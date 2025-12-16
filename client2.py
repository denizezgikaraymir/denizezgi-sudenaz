"""
client2.py
Alıcı + Hata Kontrol:
- Server'a bağlanır ve "CLIENT2" olarak kayıt olur
- Server'dan gelen paketleri dinler, kendi yöntemiyle kontrol bilgisi hesaplar ve ekrana yazar
Kullanım: python client2.py [server_host] [port]
"""
import sys
from utils import compute_control
import socket

HOST = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 9000

def recv_line(conn):
    buf = b''
    while True:
        c = conn.recv(1)
        if not c:
            return None
        if c == b'\n':
            break
        buf += c
    return buf.decode('utf-8', errors='replace')

def send_line(conn, s: str):
    conn.sendall(s.encode('utf-8') + b'\n')

def main():
    print("Client2 (Receiver + Error Checker)")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    send_line(s, "CLIENT2")
    print("Connected to server, waiting for packets...")
    while True:
        line = recv_line(s)
        if line is None:
            print("Server disconnected.")
            break
        line = line.strip()
        print("\nReceived packet:", line)
        parts = line.split('|', 2)
        if len(parts) < 3:
            print("Malformed packet")
            continue
        data, method, incoming_control = parts[0], parts[1].lower(), parts[2]
        # parse method name back to lowercase token
        method_token = method.lower()
        # for 2d we try to parse columns from incoming_control if present; else default 8
        extra = {}
        if method_token.startswith('2'):
            # attempt to parse "C=cols" in control info
            cpos = incoming_control.find('C=')
            if cpos != -1:
                try:
                    cols = int(incoming_control[cpos+2:].split(';')[0])
                    extra['cols'] = cols
                except:
                    extra['cols'] = 8
            else:
                extra['cols'] = 8
        computed = compute_control(method_token, data, **extra)
        status = "DATA CORRECT" if computed == incoming_control else "DATA CORRUPTED"
        print("Received Data :", data)
        print("Method        :", method_token)
        print("Sent Check    :", incoming_control)
        print("Computed Check:", computed)
        print("Status        :", status)

if __name__ == '__main__':
    main()