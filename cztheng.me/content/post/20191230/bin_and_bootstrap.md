---
title: "Go生成的二进制文件"
date: 2019-12-30T22:07:36+08:00
categories:
  - "golang源码"
tags:
  - "golang"

description: "当执行 go build 的时候，go会根据需要，索引当前需要的源文件，并执行编译连接操作，产生可以执行的二进制文件，
在linux平台上生成的是可执行的elf文件，而Mac上则是Mac-O文件，对应的Windows平台是PE文件格式"
---


当执行`go build`的时候，go会根据需要，索引当前需要的源文件，并执行编译连接操作，产生可以执行的二进制文件，
在linux平台上生成的是可执行的elf文件，而Mac上则是Mac-O文件，对应的Windows平台是PE文件格式。

那么go在编译一个"hello world"的.go文件的时候，仅仅只编译了这个文件里面的几行文件么？

## 二进组成

但凡引入了GC机制，一般认为多多少少都对性能会有影响，可以认为运行了个管理器在那边，随时可能会影响到我们应用逻辑
的执行，而这种管理有两种主要形式，一个是运行一个虚拟机类进行管理比如Java/Python/Lua,一个是将运行时编入到二进制中
比如Objective-C。其实还有一种是在编译器里面进行优化,生成代码编入二进制,本质也属于第二类，比如Rust。

<!--more-->

类似Java、Scala、Python这类语言，代码有个中间语言，比如JVM的字节码、Python的字节码pyc文件等。
其执行过程是先启动一个虚拟机，然后在用虚拟机去执行中间结果字节码：

![](../images/jvm.png)

Go没有类似Java/Python的虚拟机，而是和OC类似，每个可执行文件中 编译进去了一个runtime库，这个runtime
包含了GC内存管理、Groutine调度、系统调用等等功能。并且由于runtime的存在，一个Go编译的可执行文件，其甚至不依赖
libc库。Go编译的可执行文件可以认为由着几个部分组成：

![](../images/go.png)


## HelloWorld 可执行文件
既然Go的可执行文件是单独的，不依赖与运行时，那么其组成是怎样的呢？和一个传统的C程序相比有什么区别？

来看分别用两个语言实现的hello world：

    C

    #include <stdio.h>

    int main(int argc, char *argv[]) 
    {
            printf("hello world \n");
            return 0;
    }

    [root@centos ~/tmp/c]# ls -al
    total 840
    drwxr-xr-x 2 root root   4096 Apr 28 14:44 .
    drwxr-xr-x 3 root root   4096 Apr 28 13:11 ..
    -rwxr-xr-x 1 root root 844063 Apr 28 13:12 a.out
    -rw-r--r-- 1 root root     89 Apr 28 13:12 main.c

在来看一个Go的：

    Go

    package main

    func main() {
        println("hello world")
    }

    [root@centos bootstarp]# ls -al
    total 5644
    drwxr-xr-x 2 root root    4096 Apr 28 14:45 .
    drwxr-xr-x 4 root root    4096 Apr 28 13:16 ..
    -rwxr-xr-x 1 root root 1148861 Apr 28 14:45 bootstarp
    -rw-r--r-- 1 root root      57 Apr 28 14:45 main.go


上面的执行环境是ubuntu 16.04 LTS amd64 架构。可以看到使用C进行静态编译的二进制文件大小为884KB，而Go的静态编译
的可执行文件大小为1148KB，多了264KB。

那么Go在编译的过程中出了这个main.go还编译进去了哪些文件呢？

可以通过两种方式来确定， 一个是使用汇编，汇编直接会将编译的函数都用TEXT标签标示出来。

首先进行汇编：

    go tool objdump bootstarp > bootstrap.asm

然后对汇编结果进行过滤：

    cat bootstrap.asm |grep TEXT |grep "/home/cz" | awk '{print $3}' | sort | uniq

    /home/cz/go/src/internal/bytealg/compare_amd64.s
    /home/cz/go/src/internal/bytealg/equal_amd64.s
    /home/cz/go/src/internal/bytealg/index_amd64.go
    /home/cz/go/src/internal/bytealg/indexbyte_amd64.s
    ...
    /home/cz/go/src/runtime/timestub.go
    /home/cz/go/src/runtime/trace.go
    /home/cz/go/src/runtime/traceback.go
    /home/cz/go/src/runtime/type.go
    /home/cz/go/src/runtime/vdso_linux.go
    /home/cz/go_proj/src/localhost/test/bootstarp/main.go

加上main.go，总共大概80个文件，包含了原本的汇编文件和runtime的go实现文件。

真的就是这些文件么？

那肯定，汇编结果肯定就是最终编译进去的符号了。但是呢？实际上的文件还会跟多，因为有些文件可能没有具体的函数实现
而有的实现因为没有使用可能没有编译进去。

这个时候就要根据前面的《使用go编译go》中诉说的，我们自己重新编译下go的编译toolchain，然后在使用文件的位置进行日志打印

首先找到gc编译器的代码，go/src/cmd/compile/internal/gc/noder.go:

    func parseFiles(filenames []string) uint {
        var noders []*noder
        // Limit the number of simultaneously open files.
        sem := make(chan struct{}, runtime.GOMAXPROCS(0)+10)

        for _, filename := range filenames {
            p := &noder{
                basemap: make(map[*syntax.PosBase]*src.PosBase),
                err:     make(chan syntax.Error),
            }
            noders = append(noders, p)

            go func(filename string) {
                sem <- struct{}{}
                defer func() { <-sem }()
                defer close(p.err)
                base := syntax.NewFileBase(filename)
                println("CZ compile.gc.noder.parseFile:", filename) // 增加这行

                ...

增加一行日志打印。然后找到汇编器asm的代码， go/src/cmd/asm/internal/lex/lex.go:

    func NewLexer(name string) TokenReader {
        input := NewInput(name)
        println("CZ asm.lex.NewLexer:", name) // 增加这行
        ...

和 go/src/cmd/asm/internal/lex/input.go:

    func (in *Input) include() {
        // Find and parse string.
        tok := in.Stack.Next()
        if tok != scanner.String {
            in.expectText("expected string after #include")
        }
        name, err := strconv.Unquote(in.Stack.Text())
        if err != nil {
            in.Error("unquoting include file name: ", err)
        }
        in.expectNewline("#include")
        // Push tokenizer for file onto stack.
        println("CZ asm.input.include:", name) // 增加这行
        ...

也各增加一行日志.

这样使用上面修改代码重新构建go,然后再用这个新的go编译toolchain来编译bootstrap（编译过程参考：使用go编译go）

会看到：

    # runtime/internal/sys
    CZ compile.gc.noder.parseFile: ../../../../../gosrc/go/src/runtime/internal/sys/zversion.go
    CZ compile.gc.noder.parseFile: ../../../../../gosrc/go/src/runtime/internal/sys/arch.go
    CZ compile.gc.noder.parseFile: ../../../../../gosrc/go/src/runtime/internal/sys/stubs.go
    ...

    # runtime
    CZ asm.lex.NewLexer: ../../../../../gosrc/go/src/runtime/asm.s
    CZ asm.input.include: textflag.h
    # runtime
    CZ asm.lex.NewLexer: ../../../../../gosrc/go/src/runtime/asm_amd64.s
    CZ asm.input.include: go_asm.h
    CZ asm.input.include2: ../../../../../gosrc/go/src/runtime/go_asm.h
    ...
    # bootstrap
    CZ compile.gc.noder.parseFile: $WORK/b001/_gomod_.go
    CZ compile.gc.noder.parseFile: ./main.go


这里就列出了所有使用到的文件了。

## 引导进main.main
那么编译了这么多的文件，Go的可执行文件是如何进入到main.go的`main()`函数的呢？

在传统的C程序中，Linux平台下我们知道是从"__libc_start_main" libc的入口进去的，而对于Go编译的二进制，我们来看
ELF文件:

	~/go_proj/src/test/bootstrap$ readelf -h bootstrap
	ELF Header:
	  Magic:   7f 45 4c 46 02 01 01 00 00 00 00 00 00 00 00 00
	  Class:                             ELF64
	  Data:                              2's complement, little endian
	  Version:                           1 (current)
	  OS/ABI:                            UNIX - System V
	  ABI Version:                       0
	  Type:                              EXEC (Executable file)
	  Machine:                           Advanced Micro Devices X86-64
	  Version:                           0x1
	  Entry point address:               0x455220
	  Start of program headers:          64 (bytes into file)
	  Start of section headers:          456 (bytes into file)
	  Flags:                             0x0
	  Size of this header:               64 (bytes)
	  Size of program headers:           56 (bytes)
	  Number of program headers:         7
	  Size of section headers:           64 (bytes)
	  Number of section headers:         25
	  Section header string table index: 3
	  
可以看到二进制的入口点在地址：0x455220

然后因为Go不是用的GNU一套的编译工具，所以addr2line工具没法找到该地址对应的文件内容，但是可以通过Go的反汇编
来找到该地址所在的TEXT段的代码：

	~/go_proj/src/test/bootstrap$ go tool objdump bootstrap |grep 0x455220
  rt0_linux_amd64.s:8	0x455220		e94bc4ffff		JMP _rt0_amd64(SB)
  
实则为"rt0_os_arch.s"汇编文件的位置，rt0表示runtime0，os这里是linux，arch这里是amd64。我们来看下定义：

	TEXT _rt0_amd64_linux(SB),NOSPLIT,$-8
		JMP	_rt0_amd64(SB)

这里调用了"_rt0_amd64"函数，其在文件"asm_amd64.s"中：

	// _rt0_amd64 is common startup code for most amd64 systems when using
	// internal linking. This is the entry point for the program from the
	// kernel for an ordinary -buildmode=exe program. The stack holds the
	// number of arguments and the C-style argv.
	TEXT _rt0_amd64(SB),NOSPLIT,$-8
		MOVQ	0(SP), DI	// argc
		LEAQ	8(SP), SI	// argv
		JMP	runtime·rt0_go(SB)
		
如果是其他arch架构的，则在对应的asm_arch.s中。比如arm64的asm_arm64.s:

	// _rt0_arm is common startup code for most ARM systems when using
	// internal linking. This is the entry point for the program from the
	// kernel for an ordinary -buildmode=exe program. The stack holds the
	// number of arguments and the C-style argv.
	TEXT _rt0_arm(SB),NOSPLIT|NOFRAME,$0
		MOVW	(R13), R0	// argc
		MOVW	$4(R13), R1		// argv
		B	runtime·rt0_go(SB）
		
入口函数为"_rt0_arm"

不论哪种架构，最后都走到对应架构的"runtime·rt0_go",依然在asm_amd64.s:

	TEXT runtime·rt0_go(SB),NOSPLIT,$0
		// copy arguments forward on an even stack
		MOVQ	DI, AX		// argc
		MOVQ	SI, BX		// argv
		SUBQ	$(4*8+7), SP		// 2args 2auto
		ANDQ	$~15, SP
		MOVQ	AX, 16(SP)
		MOVQ	BX, 24(SP)
		...
		
	ok:
		...
	
		MOVL	16(SP), AX		// copy argc
		MOVL	AX, 0(SP)
		MOVQ	24(SP), AX		// copy argv
		MOVQ	AX, 8(SP)
		CALL	runtime·args(SB)
		CALL	runtime·osinit(SB)
		CALL	runtime·schedinit(SB)
	
		// create a new goroutine to start program
		MOVQ	$runtime·mainPC(SB), AX		// entry
		PUSHQ	AX
		PUSHQ	$0			// arg size
		CALL	runtime·newproc(SB)
		POPQ	AX
		POPQ	AX
	
		// start this M
		CALL	runtime·mstart(SB)
	
		CALL	runtime·abort(SB)	// mstart should never return
		RET
		
这里的汇编和以前熟悉的Intel(Windows) 或者AT&T（Linux)都不一样，这里是Go自创的一套汇编语法，承自Plan9汇编。

暂且不用了解详细语法，大概意义是:做完一些准备工作后，跳转到ok的token，然后依次执行 runtime·args、runtime·osinit、
runtime·schedinit，最后通过	runtime·newproc来启一个Goroutine运行runtime·mainPC。

![](../images/bootstrap.png)

这里如果全文去搜"mainPC",可能会发现找不到定义，其实是：

	DATA	runtime·mainPC+0(SB)/8,$runtime·main(SB)
	GLOBL	runtime·mainPC(SB),RODATA,$
	
这里是个变量定义，将	runtime·main 定义成了runtime·mainPC。在gosrc/src/runtime/proc.go中有定义：

	func main() {
		g := getg()

		// Racectx of m0->g0 is used only as the parent of the main goroutine.
		// It must not be used for anything else.
		g.m.g0.racectx = 0
		
		...
		
		doInit(&main_inittask)

		close(main_init_done)
	
		needUnlock = false
		unlockOSThread()
	
		if isarchive || islibrary {
			// A program compiled with -buildmode=c-archive or c-shared
			// has a main, but it is not executed.
			return
		}
		fn := main_main // make an indirect call, as the linker doesn't know the address of the main package when laying down the runtime
		fn()
		...
		
		
这里进行了runtime的 init，然后执行了main_main函数。

那么这个main_main函数又是什么呢？

	//go:linkname main_main main.main
	func main_main()
	
这里通过"go:linkname" 将main_main指定为main.main。而main.main也就是我们写的 "package main"里面的"func main"。

至此，Go程序进入到了我们写的业务代码了。



## 总结
Go采用了和OC类似的，将runtime和业务代码都同级别的编译成相应的机器码可执行代码。在编译期间，除了会编译业务代码，还会
将"go/src/runtime"中的代码编译进可执行文件中。可执行文件执行时，首先会初始化runtime,然后开启一个新的Goroutine来
运行业务逻辑代码中的main.main函数。因为runtime是在编译期间同时引用代码的，所以想了解runtime的特性，可以直接在GO的
安装包里面修改runtime代码，然后构建执行来看差别。

## 引用
1. [go](https://github.com/golang/go/tree/master/src/runtime/)
2. [使用go编译go](http://cztheng.me/post/20191228/build_go_from_source/)
