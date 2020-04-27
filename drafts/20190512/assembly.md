# Go中使用的amd64汇编

Go1.13的编译器总共支持9种指令集：

|架构|说明|
| --- | --- |
|amd64 (also known as x86-64)|A mature implementation.|
|386 (x86 or x86-32)|Comparable to the amd64 port.|
|arm (ARM)|Supports Linux, FreeBSD, NetBSD, OpenBSD and Darwin binaries. Less widely used than the other ports.|
|arm64 (AArch64)|Supports Linux and Darwin binaries. New in 1.5 and not as well exercised as other ports.|
|ppc64, ppc64le (64-bit PowerPC big- and little-endian)|Supports Linux binaries. New in 1.5 and not as well exercised as other ports.|
|mips, mipsle (32-bit MIPS big- and little-endian)|Supports Linux binaries. New in 1.8 and not as well exercised as other ports.|
|mips64, mips64le (64-bit MIPS big- and little-endian)|Supports Linux binaries. New in 1.6 and not as well exercised as other ports.|
|s390x (IBM System z)|Supports Linux binaries. New in 1.7 and not as well exercised as other ports.|
|wasm (WebAssembly)|Targets the WebAssembly platform. New in 1.11 and not as well exercised as other ports.|

在Go的源码src/runtime中有：

	asm_386.s
	asm_amd64.s
	asm_amd64p32.s
	asm_arm.s
	asm_arm64.s
	asm_mips64x.s
	asm_mipsx.s
	asm_ppc64x.s
	asm_s390x.s
	asm_wasm.s
	
总共10个文件，其中asm_amd64p32是amd64移植到x86-32平台的实现。这些runtime中的文件和上面的9个目标平台指令集一一对应。

而在目前Go的使用中，生产环境下最多的还是Linux+amd64这样的组合，呈如上面所述："amd64 is A mature implementation"。amd64指令集也是Go最成熟的实现。
## 参考
1. [A Quick Guide to Go's Assembler](https://9p.io/sys/doc/asm.html)
2. [https://9p.io/sys/doc/asm.html](http://golang.org/doc/asm)
