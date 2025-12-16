"""
client1.py
Gönderici:
- Kullanıcıdan metin alır
- Yöntem seçer: parity, 2d, crc16, hamming, ip
- Hesaplanan kontrol bilgisini server'a paket formatında gönderir: DATA|METHOD|CONTROL
Kullanım: python client1.py [server_host] [port]
"""
import sys
from utils import compute_control
import socket

HOST = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 9000

def send_line(conn, s: str):
    conn.sendall(s.encode('utf-8') + b'\n')

def main():
    print("Client1 (Data Sender)")
    text = input("Enter text to send: ")
    print("Methods: parity, 2d, crc16, hamming, ip")
    method = input("Choose method: ").strip().lower()
    extra = {}
    if method == '2d':
        cols = input("Enter columns for 2D parity (default 8): ").strip()
        try:
            extra['cols'] = int(cols) if cols else 8
        except:
            extra['cols'] = 8
    control = compute_control(method, text, **extra)
    packet = f"{text}|{method.upper()}|{control}"
    print("Computed control:", control)
    # connect to server and register as CLIENT1
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    send_line(s, "CLIENT1")
    send_line(s, packet)
    print("Packet sent. Exiting.")
    s.close()

if __name__ == '__main__':
    main()