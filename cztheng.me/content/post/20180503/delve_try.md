---
title: "Debug Golang With Delve"
date: 2018-05-03T22:07:36+08:00
categories:
  - "工程实践"
tags:
  - "debug"
  - "golang"

description: "Delve更适合于Golang程序的Debug操作，为了这句官方的推荐，我们也应该去尝试一下Delve。"
---


Golang在其官方[文档](https://golang.google.cn/doc/gdb) 说明

> Note that Delve is a better alternative to GDB when debugging Go programs built with the standard toolchain. It understands the Go runtime, data structures, and expressions better than GDB. Delve currently supports Linux, OSX, and Windows on amd64. For the most up-to-date list of supported platforms, please see the Delve documentation.

相比于GDB，Delve更适合于Golang程序的Debug操作，为了这句官方的推荐，我们也应该去尝试一下Delve。当前Delve可以支持Linux/OSX/Windows这几个主流平台，基本可以替代GDB的使用。

<!--more-->

## 安装
安装Delve可以参考[官方文档](https://github.com/derekparker/delve/tree/master/Documentation/installation),这里以Mac为例。

首先确保xcode以及其插件已经安装好：

    xcode-select --install

Delve本身也是用Golang写的，所以接着通过`go get`安装Delve。

$ go get -u github.com/derekparker/delve/cmd/dlv

安装好之后，通过

    dlv version


可以看到当前版本号：

    [cz@air_11:delve]$dlv version
    Delve Debugger
    Version: 1.0.0
    Build: 8ce88095c6ea40a1d10ac2e07b7ce950f6dfaa2f

## 调试程序

现在开始写个简单求和程序

	package main

	import (
		"fmt"
	)

	func sum(a, b int) int {
		s := a + b
		return s
	}

	func main() {
		s := sum(1, 2)
		fmt.Printf("1 + 2 = %d \n", s)
	}

在代码目录下执行：

    dlv debug

看到：

    [cz@air_11:delve]$dlv debug
    Type 'help' for list of commands.
    (dlv)

进入到debug界面，这里基本和`gdb abc_exe`一样。这里会自动编译当前目录中的main包并类似gcc一样加上`-g`选项。

首先在main函数的地方设个断点：

    (dlv) b main.main
    Breakpoint 1 set at 0x10b4228 for main.main() ./main.go:18

然后，执行到该断点：

	(dlv) c
	> main.main() ./main.go:18 (hits goroutine(1):1 total:1) (PC: 0x10b4228)
	Warning: debugging optimized function
		13:	func sum(a, b int) int {
		14:		s := a + b
		15:		return s
		16:	}
		17:
	=>  18:	func main() {
		19:		s := sum(1, 2)
		20:		fmt.Printf("1 + 2 = %d \n", s)
		21:	}


这里"b"是"break"的缩写，"c"是"continue" 的缩写。如果熟悉GDB（做后台的别说不熟悉）这里会
有点不同，这里没有"run"命令，而直接是"continue"到第一个断点。如果不带参数的话，其实"run"和“continue”并没有使用上的区别。

在设置断点到sum函数，并运行到该断点：

	(dlv) b main.sum
	Breakpoint 2 set at 0x10b41d0 for main.sum() ./main.go:13
	(dlv) c
	> main.sum() ./main.go:13 (hits goroutine(1):1 total:1) (PC: 0x10b41d0)
	Warning: debugging optimized function
		 8:
		 9:	import (
		10:		"fmt"
		11:	)
		12:
	=>  13:	func sum(a, b int) int {
		14:		s := a + b
		15:		return s
		16:	}
		17:
		18:	func main() {

这里看到执行到了sum函数。

接着单步进入函数内：

	(dlv) s
	> main.sum() ./main.go:14 (PC: 0x10b41e7)
	Warning: debugging optimized function
		 9:	import (
		10:		"fmt"
		11:	)
		12:
		13:	func sum(a, b int) int {
	=>  14:		s := a + b
		15:		return s
		16:	}
		17:
		18:	func main() {
		19:		s := sum(1, 2)


在函数内部，单步下一句：

	(dlv) n
	> main.sum() ./main.go:15 (PC: 0x10b41f5)
	Warning: debugging optimized function
		10:		"fmt"
		11:	)
		12:
		13:	func sum(a, b int) int {
		14:		s := a + b
	=>  15:		return s
		16:	}
		17:
		18:	func main() {
		19:		s := sum(1, 2)
		20:		fmt.Printf("1 + 2 = %d \n", s)

如果想查看相关代码。

	(dlv) l 13
	Showing /Users/cz/Proj/golang/src/test.air/delve/main.go:13 (PC: 0x10b41d0)
	   8:
	   9:	import (
	  10:		"fmt"
	  11:	)
	  12:
	  13:	func sum(a, b int) int {
	  14:		s := a + b
	  15:		return s
	  16:	}
	  17:
	  18:	func main() {

查看指定行号，或者查看函数：

	(dlv) l sum
	Showing /Users/cz/Proj/golang/src/test.air/delve/main.go:13 (PC: 0x10b41d0)
	   8:
	   9:	import (
	  10:		"fmt"
	  11:	)
	  12:
	  13:	func sum(a, b int) int {
	  14:		s := a + b
	  15:		return s
	  16:	}
	  17:
	  18:	func main() {


最后退出：

    quit

总的来说。整个操作过程和GDB基本类似。只要熟悉Debug过程，可以很快的上手使用。

## 指定debug程序

上面的`dlv debug`是直接编译并开始debug。还可以直接传递包的路径，来指定debug那个程序。

比如：

    dlv debug github.com/nsqio/nsq/apps/nsqd

不论在哪个位置，执行上面的命令都会去debug nsqd程序。

因为Golang工具链的test和trace属性，Delve还支持debug 指定的test和trace程序，其实就是和Golang的test机制很好的结合在一起。

比如在相关目录执行：

    dlv test

就可以调试这个目录下的单元测试代码，即"_test.go"的代码。同样如果传递一个包目录，就会执行指定目录下的test. 而`dlv trace`则是执行trace代码。

比如我们到Golang的源码目录下的string包:

    cd $GOROOT/src/strings

让后执行：

        [cz@air_11:strings]$dlv test
        Type 'help' for list of commands.
        (dlv) funcs ExampleToUpper
        strings_test.ExampleToUpper
        (dlv) b strings_test.ExampleToUpper
        Breakpoint 1 set at 0x1150fe8 for strings_test.ExampleToUpper() ./example_test.go:270
        (dlv) c
        > strings_test.ExampleToUpper() ./example_test.go:270 (hits goroutine(1):1 total:1) (PC: 0x1150fe8)
        Warning: debugging optimized function
           265:		r := strings.NewReplacer("<", "&lt;", ">", "&gt;")
           266:		fmt.Println(r.Replace("This is <b>HTML</b>!"))
           267:		// Output: This is &lt;b&gt;HTML&lt;/b&gt;!
           268:	}
           269:
        => 270:	func ExampleToUpper() {
           271:		fmt.Println(strings.ToUpper("Gopher"))
           272:		// Output: GOPHER
           273:	}
           274:
           275:	func ExampleToLower() {
        (dlv)


这里可以看到是在测试代码的`ExampleToUpper`函数中断了下来，我们来调试字符串中转换大写的源码。

这里一路"s"下去（split)，会看到，最终执行了：

        (dlv) s
        > strings.Map() ./strings.go:518 (PC: 0x10e2aad)
        Warning: debugging optimized function
           513:		var b []byte
           514:		// nbytes is the number of bytes encoded in b.
           515:		var nbytes int
           516:
           517:		for i, c := range s {
        => 518:			r := mapping(c)
           519:			if r == c {
           520:				continue
           521:			}
           522:
           523:			b = make([]byte, len(s)+utf8.UTFMax)
        (dlv) p c
        71

可以看到string包源码中，最终是将"Gopher"中的每个字符去到`mapping`函数中找到其对应的大写字母，这里打印第一个字符c为71也就是ASCII表示的"G"，查表得到为其本身。这样我们就可以单步的去看
Golang标准库源码了。

当然，除了指定debug二进制文件，Delve还和gdb一样可以attach到一个正在运行的进程上面，使用：

    dlv attach pid 

以及加载一个coredump文件：

    dlv core <executable> <core>

这个操作起来和gdb基本没有任何区别。


