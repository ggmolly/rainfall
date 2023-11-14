# bonus3

The binary seems to do nothing at a first glance :

```sh
$ ./bonus3 
$ ./bonus3 qwe

$ ./bonus3 ""
$ qweqwewqe
sh: 1: qweqwewqe: not found
$ id
uid=2013(bonus3) gid=2013(bonus3) euid=2014(end) egid=100(users) groups=2014(end),100(users),2013(bonus3)
```

So, it seems like I found the solution but this is a fluke, let's understand instead.

```sh
$ ltrace ./bonus3 qwe
__libc_start_main(....)  <unfinished ...>
fopen("/home/user/end/.pass","r")
+++ exited (status 255) +++
```

Note the `unfinished` on the `__libc_start_main`, the program called `exit` before the function returned.

Disassembling using `ghidra` :

```c

int main(int argc, char **argv)
{
    int returnCode;
    // size of the buffer deduced from the sum of both calls to `fread`
    char buffer[132] = {0}
    FILE *pass;

    pass = fopen("/home/user/end/.pass","r");
    if ((!pass) || (argc != 2))
        return (-1);

    fread(buffer, 1, 66, pass);
    buffer[65] = '\0';
    buffer[atoi(argv[1])] = '\0';
    fread(buffer+66, 1, 65, pass);
    fclose(pass);
    if (strcmp(buffer, argv[1]) == 0) {
        execl("/bin/sh", "sh", 0);
    } else {
        puts(buffer);
    }
    return (0);
}
```

And so, the empty argument is the intended solution.

This is because calling `atoi` on an empty strings return `0`, so `buffer[0]` is set to a NULL-byte, this results into a call to `strcmp` that compares nothing with nothing, and so the program calls `execl` and spawns a shell.