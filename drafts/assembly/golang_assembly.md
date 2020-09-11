#Golang汇编
Golang汇编中寄存器、指令以及汇编命令一般都是大写。
## 寄存器
四大伪寄存器

* FP: Frame pointer: arguments and locals.
* PC: Program counter: jumps and branches.
* SB: Static base pointer: global symbols.
* SP: Stack pointer: top of stack.

所有用户定义的符号都是相对于FP(参数和局部变量)/SB(全局变量)的便宜量

SB寄存器可以认为是进程空间的起始地址，所以变量的表示为：foo(SB)表示内存中的一个地址，
名为foo。如果增加了 "<>"如foo<>(SB)则表示仅在该文件中可见的变量，好比C中的static变量。
而foo<>+4(SB),则表示变量foo往后便宜4个字节。

FP寄存器则主要用于函数参数，因此first_arg+0(FP)表示第一个参数而second_arg+8(FP)表示
第二个参数，这里区别于上面，这里的偏移量为从FP开始的偏移，而前面的label则仅仅是个助记符，
其实应该忽略。+8是因为目标平台为64bit，所以指针大小为8byte。

SP寄存器用于当前函数的栈，表示当前局部栈顶。所以一般变量表示为x-8(SP)， y-4(SP)同样，这里
表示的相对于SP的地址偏移，而x/y为变量名。这里的变量名不可随意省略，因为在有SP寄存器的
平台上，x-8(SP)和-8(SP)表示不同的两个值，后者为具体平台上对SP寄存器中值向后偏移。

## 函数声明
包名和函数名中间的"."替换成"·",比如"fmt.Printf"写成"fmt·Printf"，而" math/rand.Int"
写成" math/rand·Int"。

而函数的定义以TEXT指令开始，后接上特殊格式的Label。可以认为函数的定义以TEXT开始，RET结束
（PS：也包含其他跳转指令,如JMP）。

函数名遵循上面的标准，函数名后接上的是格式如"$s-a" s表示这个函数用的栈大小，a表示这个
函数用到的参数加返回值内存大小。如果a省略了，"$s",则需要用NOSPLIT表示参数大小通过推断生成。
函数名、标记、栈大小通过","来分割。比如：

    TEXT runtime·profileloop(SB),NOSPLIT,$8
        MOVQ	$runtime·profileloop1(SB), CX
        MOVQ	CX, 0(SP)
        CALL	runtime·externalthreadhandler(SB)
        RET

函数名为包runtime的profileloop函数，其参数大小省略了，通过NOSPLIT指定，其用栈大小为
8字节。

## Label
Golang汇编中的label仅可以在定义的函数中可见。

全局变量通过DATA和GLOBAL质量定义。格式为：

    DATA	symbol+offset(SB)/width, value

如：
    DATA divtab<>+0x00(SB)/4, $0xf4f8fcff

局部变量divtab，大小为4字节，值为0xf4f8fcff。

DATA是给地址赋值，还需要用GLOBAL来声明变量：

    GLOBAL symbol,flag,size

如：

    GLOBL divtab<>(SB), RODATA, $64

表示局部变量divtab为只读变量，大小总共为64字节。其中flag主要有这样几类：

|flag| value| |
|---|---|---|
|NOPROF |1||
|DUPOK |2||
|NOSPLIT |4||
|RODATA |8||
|NOPTR|16||
|WRAPPER|32||
|NEEDCTXT|64||
|LOCAL |128||
|TLSBSS |256||
|NOFRAME |512||
|TOPFRAME |2048||

## 寻址
Golang汇编的寻址和Plan9的一样，与AMD64不一样的是，把Base地址挪出来了。比如

* (DI)(BX*2) 表示 DI+BX*2
* 64(DI)(BX*2) 表示 DI+BX*2+64

## runtime兼容
在手写汇编的时候，可以包含#include "go_tls.h"和#include "go_asm.h"文件，里面定义了runtime中的g和m.

使用g和g里面的保存的m的用法如下：

    get_tls(CX)
    MOVL	g(CX), AX     // Move g into AX.
    MOVL	g_m(AX), BX   // Move g.m into BX.




