import struct
import binascii

from Crypto.Cipher import ChaCha20
from Crypto.Random import get_random_bytes

"""Implement the encryption stream packet format (errors are checked with crc32)
"""

MAGIC = b"\xde\xad\xbe\xef\xca\xfe\xf0\x0d"

class PacketEncoder:
    def __init__(self, key=None, nonce=None):
        self.key = key if key is not None else get_random_bytes(32)
        self.nonce = nonce if nonce is not None else get_random_bytes(8)
        self.cipher = ChaCha20.new(key=self.key, nonce=self.nonce)
        self.off = 0

    def header(self, length):
        header = MAGIC + struct.pack("<i", length) + self.nonce + struct.pack("<Q", self.off)
        header_checksum = binascii.crc32(header)
        header += struct.pack("<I", header_checksum)
        print(f"creating header: length {length}, crc {header_checksum}")
        return header

    def encode(self, data):
        self.cipher.seek(self.off)
        length = len(data)
        header = self.header(length)
        enc_data = self.cipher.encrypt(data)
        self.off += length
        return header + enc_data + struct.pack("<I", binascii.crc32(enc_data))

class PacketDecoder:
    def __init__(self, key):
        self.key = key
        self.cipher = None

    def parse_header(self, data):
        header_off = 0
        if data[:len(MAGIC)] != MAGIC:
            raise ValueError("invalid magic number")
        header_off += len(MAGIC)
        length = struct.unpack("<i", data[header_off:header_off+4])[0]
        if length < 0:
            # TODO: error here may not be appropriate
            raise ValueError("invalid length")
        header_off += 4
        nonce = data[header_off:header_off+8]
        header_off += 8
        off = struct.unpack("<Q", data[header_off:header_off+8])[0]
        header_off += 8
        crc_computed = binascii.crc32(data[:header_off])
        crc_read = struct.unpack("<I", data[header_off:header_off+4])[0]
        if crc_computed != crc_read:
            raise ValueError(f"invalid CRC, expecting: {crc_read}, got: {crc_computed}")
        header_off += 4
        return length, nonce, off, data[header_off:]

    def decode(self, data):
        length, nonce, off, data = self.parse_header(data)
        if self.cipher is None:
            self.cipher = ChaCha20.new(key=self.key, nonce=nonce)
        self.cipher.seek(off)
        enc_data = data[:length]
        crc_computed = binascii.crc32(enc_data)
        dec_data = self.cipher.decrypt(enc_data)
        crc_read = struct.unpack("<I", data[length:length+4])[0]
        if crc_computed != crc_read:
            raise ValueError("invalid CRC")
        return dec_data
    
if __name__ == "__main__":
    key = get_random_bytes(32)

    pe = PacketEncoder(key=key)
    m1 = b"hello "
    m2 = b"world"
    
    e1 = pe.encode(m1)
    e2 = pe.encode(m2)

    pd = PacketDecoder(key=key)
    d1 = pd.decode(e1)
    d2 = pd.decode(e2)

    print(d1, d2)






