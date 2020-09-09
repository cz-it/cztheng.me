# Golang汇编

## 1. 汇编语言
### 汇编种类
汇编根据不同的目标架构平台而独立，比如ARM汇编、MIPS汇编、i386汇编等

### 汇编语法风格
汇编主要有两种语法风格

* Intel 风格
* AT&T 风格

### 主流汇编器

* MASM : windows上的主流，微软提供
* NASM/YASM : linux世界的masm
* AS : GNU的汇编器，采用AT&T语法

### AMD64汇编
AMD64又称X86_64汇编，主要由AMD研发，兼容IA32指令，与Intel的IA64做区别

### Golang编译器历史

|||||
| --- | --- | --- | --- | 
| SPARC | kc | kl | ka |
|PowerPC|qc  |ql  |qa|
|MIPS   |vc  |vl  |va|
|MIPS   |little-endian  |0c |0l|
|ARM    |5c  |5l  |5a|
|AMD64  |6c  |6l  |6a|
|Intel  |386  |8c |8l|
|PowerPC|64-bit |9c |9l|


### 引用

* [A Manual for the Plan 9 assembler](https://9p.io/sys/doc/asm.html)
* [Plan 9 C Compilers](https://9p.io/sys/doc/compiler.html)
* [A Quick Guide to Go's Assembler](https://golang.org/doc/asm)
* [AT&T Assembly Syntax](https://csiflabs.cs.ucdavis.edu/~ssdavis/50/att-syntax.htm)


## 2. Golang编译过程

### 引用

* [How a Go Program Compiles down to Machine Code](https://getstream.io/blog/how-a-go-program-compiles-down-to-machine-code/)
* [Go: Overview of the Compiler](https://medium.com/a-journey-with-go/go-overview-of-the-compiler-4e5a153ca889)
* [Go 语言设计与实现:编译原理](https://draveness.me/golang/docs/part1-prerequisite/ch02-compile/golang-compile-intro/)



