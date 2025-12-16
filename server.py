"""
server.py
Aracı sunucu:
- İki client bekler: önce alıcı (CLIENT2) bağlanabilir, sonra gönderici (CLIENT1) bağlanır.
- CLIENT1'den gelen paket(ler)i alır, seçilen hata enjeksyonunu uygular (param ile)
  ve CLIENT2'ye iletir.
Kullanım: python server.py [port] [injection_mode]
 injection_mode options: none (default), bitflip, subst, delete, insert, swap, burst, multibit
"""
import socket
import threading
import sys
import random
import time

HOST = '0.0.0.0'
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9000
INJECT = sys.argv[2] if len(sys.argv) > 2 else 'none'

PROB = 0.3

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

def corrupt_text(text: str) -> str:
    if INJECT == 'none' or random.random() > PROB:
        return text
    t = list(text)
    n = len(t)
    if n == 0:
        return text
    if INJECT == 'bitflip':
     
        idx = random.randrange(n)
        b = ord(t[idx]) ^ (1 << random.randrange(7))
        t[idx] = chr(b % 256)
    elif INJECT == 'subst':
        idx = random.randrange(n)
        t[idx] = chr(random.randint(32, 126))
    elif INJECT == 'delete':
        idx = random.randrange(n)
        del t[idx]
    elif INJECT == 'insert':
        idx = random.randrange(n+1)
        t.insert(idx, chr(random.randint(32,126)))
    elif INJECT == 'swap' and n >= 2:
        idx = random.randrange(n-1)
        t[idx], t[idx+1] = t[idx+1], t[idx]
    elif INJECT == 'multibit':
        flips = random.randint(1, min(8, n*2))
        for _ in range(flips):
            idx = random.randrange(n)
            b = ord(t[idx]) ^ (1 << random.randrange(7))
            t[idx] = chr(b % 256)
    elif INJECT == 'burst':
        start = random.randrange(n)
        length = random.randint(1, min(8, n-start))
        for i in range(start, start+length):
            t[i] = chr((ord(t[i]) ^ 0xFF) % 256)
    return ''.join(t)

def handle_connections():
    print("Server listening on port", PORT)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(5)
    client1 = None
    client2 = None
    roles = {}
    while True:
        conn, addr = s.accept()
        print("Conn from", addr)
        role = recv_line(conn)
        if role is None:
            conn.close()
            continue
        role = role.strip().upper()
        print("Role:", role)
        if role == 'CLIENT1':
            client1 = conn
            roles['client1'] = addr
          
            threading.Thread(target=from_client1_to_client2, args=(conn,)).start()
        elif role == 'CLIENT2':
            client2 = conn
            roles['client2'] = addr
           
            global CLIENT2_CONN
            CLIENT2_CONN = conn
        else:
            send_line(conn, "UNKNOWN ROLE")
            conn.close()

def from_client1_to_client2(conn1):
    global CLIENT2_CONN
    print("Ready to forward from client1 to client2 (waiting for client2).")
    while True:
        line = recv_line(conn1)
        if line is None:
            print("Client1 disconnected")
            return
        print("Received packet from client1:", line.strip())
     
        parts = line.split('|', 2)
        if len(parts) < 3:
            print("Malformed packet, forwarding raw")
            packet_to_send = line
        else:
            data, method, control = parts[0], parts[1], parts[2].strip()
            corrupted = corrupt_text(data)
            packet_to_send = f"{corrupted}|{method}|{control}"
            print("After corruption:", packet_to_send)
       
        if 'CLIENT2_CONN' in globals() and CLIENT2_CONN:
            try:
                send_line(CLIENT2_CONN, packet_to_send)
                print("Forwarded to client2")
            except Exception as e:
                print("Failed to send to client2:", e)
        else:
            print("Client2 not connected yet; dropping or buffering not implemented.")

if __name__ == '__main__':
    try:
        handle_connections()
    except KeyboardInterrupt:
        print("Server exiting.")