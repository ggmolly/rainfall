# level0

The `level0` binary present in the home directory of the user `level0` is a simple binary that takes a string as first argument (otherwise it segfaults).

If we try to run it with a random string, we get the following output:

```bash
$ ./level0 AAAAAAAAAAAAAAAAAAA
No !
```

So we have to find the secret string to get the flag?

Disassembling the binary using `ghidra`, we can see that the binary is doing something like that :
```c

int main(int argc, char **argv)
{
    int i = atoi(argv[1]);
    if (i == 0x1a7) // 423 in decimal
    {
        system("/bin/sh");
    }
    else
    {
        puts("No !");
    }
}
```

Since the binary has a setuid bit set, the `/bin/sh` command will be executed as the user `level1`.

```bash
$ ./level0 423
$ whoami
level1
$ cd /home/user/level1/
$ ls -la
...
-rw-r--r--+ 1 level1 level1   65 Sep 23  2015 .pass
...
$ cat .pass
1fe8a524fa4bec01ca4ea2a869af2a02260d4a7d5fe7e7c24d8617e6dca12d3a
```


