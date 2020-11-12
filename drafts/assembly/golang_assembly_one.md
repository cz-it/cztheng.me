# 一文Golang汇编
*学习Golang汇编的目的*

## 1. Golang汇编由来

## 2. AT&T汇编风格
Golang汇编承袭与Plan9汇编，都是采用了AT&T汇编语法。AT&T汇编语法区别于Intel汇编语法，常见于
Linux世界，如GAS(GNU as 汇编器)。而一般学校里面和诸多汇编大作都是采用Intel汇编语法，如使用
MASM或者Linux上的NASM/YASM。AT&T汇编语法主要特性包括：



## 3. X86-64汇编

## 4. Plan9 汇编

## 5. Golang汇编

### 变量

### 数据结构

### 控制

### 函数

### 堆栈结构



### .go 和 .s

### 试用案例
通过汇编扩展一些内容

## 参考
* [A Quick Guide to Go's Assembler](https://golang.org/doc/asm)
* [A Manual for the Plan 9 assembler](https://9p.io/sys/doc/asm.html)
* [Plan 9 C Compilers](https://9p.io/sys/doc/compiler.html)
* [AT&T Assembly Syntax](https://csiflabs.cs.ucdavis.edu/~ssdavis/50/att-syntax.htm)
* [Go语言高级编程](https://chai2010.cn/advanced-go-programming-book/ch3-asm/readme.html)
* [plan9 assembly 完全解析](https://github.com/cch123/golang-notes/blob/master/assembly.md#plan9-assembly-%E5%AE%8C%E5%85%A8%E8%A7%A3%E6%9E%90)
* [Go functions in assembly language](https://lrita.github.io/images/posts/go/GoFunctionsInAssembly.pdf)
* [A Foray Into Go Assembly Programming](https://blog.sgmansfield.com/2017/04/a-foray-into-go-assembly-programming/)
* [Contiguous stacks](https://docs.google.com/document/d/1wAaf1rYoM4S4gtnPh0zOlGzWtrZFQ5suE8qr2sD8uWQ/pub)
* [go-internals/chapter-i-go-assembly](https://cmc.gitbook.io/go-internals/chapter-i-go-assembly)