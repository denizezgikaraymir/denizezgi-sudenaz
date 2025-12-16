"""
utils.py
Kontrol/barkod (parity, 2D parity, CRC16-CCITT, Hamming(7,4) for nibbles, IP checksum)
Basit string tabanlı kontrol bilgi formatları üretilir ve parse edilebilir.
"""
from typing import List, Tuple
import binascii

def bytes_of_text(text: str) -> bytes:
    return text.encode('ascii', errors='replace')


def parity_bits(data: bytes) -> str:
    bits = []
    for b in data:
        ones = bin(b).count('1')
        bits.append('1' if ones % 2 else '0')
    return ''.join(bits)


def parity_2d(data: bytes, cols: int = 8) -> str:
    if cols <= 0:
        cols = 8
    rows = [data[i:i+cols] for i in range(0, len(data), cols)]
    row_parities = []
    for r in rows:
        row_parities.append(parity_bits(r))

    col_parities = []
    for c in range(cols):
        acc = 0
        for r in rows:
            if c < len(r):
                acc ^= r[c]
        col_parities.append('1' if bin(acc).count('1') % 2 else '0')
    rows_hex = ''.join(binascii.hexlify(r).decode() for r in rows)
    return f"ROWSHEX:{rows_hex};ROWPAR:{','.join(row_parities)};COLPAR:{''.join(col_parities)};C={cols}"

def crc16_ccitt(data: bytes, poly: int = 0x1021, init_val: int = 0xFFFF) -> str:
    crc = init_val
    for b in data:
        crc ^= (b << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ poly) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return format(crc, '04X')

def hamming_7_4_check(data: bytes) -> str:
    def hamming_parity_for_nibble(n):
        d = [(n >> i) & 1 for i in range(4)]
       
        p1 = d[0] ^ d[1] ^ d[3]
        p2 = d[0] ^ d[2] ^ d[3]
        p3 = d[1] ^ d[2] ^ d[3]
        
        return (p1 << 2) | (p2 << 1) | p3
    out = []
    for b in data:
        hi = (b >> 4) & 0xF
        lo = b & 0xF
        out.append(hamming_parity_for_nibble(hi))
        out.append(hamming_parity_for_nibble(lo))
    return ''.join(format(x, '02X') for x in out)


def ip_checksum(data: bytes) -> str:
    if len(data) % 2 == 1:
        data = data + b'\x00'
    s = 0
    for i in range(0, len(data), 2):
        w = (data[i] << 8) + data[i+1]
        s += w
    
    while (s >> 16):
        s = (s & 0xFFFF) + (s >> 16)
    s = ~s & 0xFFFF
    return format(s, '04X')


def compute_control(method: str, text: str, **kwargs) -> str:
    data = bytes_of_text(text)
    method = method.lower()
    if method == 'parity':
        return parity_bits(data)
    if method == '2d':
        cols = kwargs.get('cols', 8)
        return parity_2d(data, cols=cols)
    if method == 'crc16':
        return crc16_ccitt(data)
    if method == 'hamming':
        return hamming_7_4_check(data)
    if method == 'ip':
        return ip_checksum(data)
    raise ValueError("Unknown method")