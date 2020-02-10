---
title: "string未必不可修改"
date: 2019-05-25T22:07:36+08:00
categories:
  - "奇技淫巧"
tags:
  - "golang"

description: "string的本质是一个包含`void *`指向的内存地址和一个表示字符串长度`int`的struct"
---

golang中的string作为一种内置类型，在Golang的["Language Specification"](http://docs.golang.org/ref/spec)
是这样描述的：

> ##String types
> A string type represents the set of string values. A string value is a (possibly empty) sequence of bytes. 
> The number of bytes is called the length of the string and is never negative. Strings are immutable: 
> once created, it is impossible to change the contents of a string. The predeclared string type is string;
> it is a defined type.

如Spec所述，string对象是不可修改的，所以我这里的标题严格来说是错误的。

但是为何要其这样一个标题呢？当然是有点标题党的意思，初衷呢还是想从Golang中的string的本质入手，详细介绍string对象。

<!--more-->

string的结构如下：
![string](../images/string.png)

string的本质是一个包含"void *"指向的内存地址和一个表示字符串长度"int"的struct,如果这个内存指向的是SRODATA只读数据段
则，此时无论什么办法都无法修改这段内存中的内容，而如果这内存地址指向的是一段可以修改的普通内存地址，则可以通过本文中的方法
进行修改，而且不会消耗多余的内存。



## 1. string类型
Golang中的string不同于其他语言中的string，Golang中的string是一串变长字符序列。这里的字符不同于C中的"char",而是UTF-8
编码的字符，因此每个字符根据编码需要，长度可能并不想同。由于这里定义的就是UTF-8编码，所以我们在Golang的官方上看到了类似：

	println("你好，世界")
	
字样的代码，在字符串中可以直接使用宽字符。

字符串指定值可以通过两种方式，一种是如上面的用双引号括起来的如：

	"abc"
	"Hello World!"
	"你好，世界！"
	
双引号中支持时候用"\"反斜杠进行转义：

转义字符|意义
--- | ---
\\ | 反斜杠(\)
\000 | 使用三个数字表示的8个bit的8进制数表示的Unicode代码
\’	 | 单引号(‘)
\” | 双引号(“)
\a	 | ASCII 字符，响铃 (BEL)
\b	 | ASCII 回车(BS)
\f	 | ASCII 制表符 (FF)
\n | ASCII 换行符 (LF)
\r	 | ASCII 回车(CR)
\t	 | ASCII 制表符 (TAB)
\uhhhh | 四个数字16个bit的16进制Unicode代码
\v	 | ASCII 垂直制表符 (VT)
\xhh | 两个数字8bit的16进制Unicode代码

	
还可以用"`"	反引号扩起来的，支持多行字符串的形式：

	`ab
		c
		 d
	`
但是这种格式并不支持转义字符，如需使用，还要和""进行拼接配合。

而字符串的长度，则可以通过`len(str)`来计算出字符串str的长度。


## 2. runtime中的string
在runtime的代码src/runtime/string.go中有个结构体的定义：

	type stringStruct struct {
		str unsafe.Pointer
		len int
	}

结合开篇的结构图就比较好理解了，这里的str就好比C里面的"void *"指向一段内存，而len则表示这段内存的长度。

str的类型为unsafe.Pointer，根据src/unsafe/unsafe.go的定义

	type ArbitraryType int
	type Pointer *ArbitraryTyp
	
这里就不得不说下Go中的int了，int实际上是个变长的类型，在不同的平台上会有不同的定义，如果是32位机器则为int32
如果是64位机器则为int64	，所以基本就可以认为是C中的intptr。

知道了这个结构，我们来写一段CGO代码，通过C来dump出Golang中的string的内存：

	package main
	
	import (
		"fmt"
		"unsafe"
	)
	
	// #include <stdio.h>
	//
	// void dump(void *ptr, int len) {
	//  char *p = (char *)ptr;
	// 	printf("dump:\n");
	//  for(int i=0; i< len; i++) {
	//      printf("    [%d]:%c \n", i, p[i]);
	//  }
	// }
	//
	//
	import "C"
	
	type stringStruct struct {
		str unsafe.Pointer
		len int
	}
	
	func main() {
		s := "abc"
	
		fmt.Printf("s string:%v\n", s)
		p := (*stringStruct)(unsafe.Pointer(&s))
		C.dump(p.str, C.int(p.len))
	}
	
代码中写了一个C函数，该函数接受一个地址指针prt和一个内存长度len，然后依次将内存中的字符打印出来。在Go的代码中，首先定义一个
字符串s，然后根据runtime中对stringStruct的定义（PS:因为runtime中没有导出这个结构，所以自己定义了一个）取得string中的内存
地址p.str和对应的长度p.len。然后将其传入给上面定义的C函数，运行结果为：

	s string:abc
	dump:
	    [0]:a
	    [1]:b
	    [2]:c
	    
这也就证实了开篇的内存结构图，str中存储的正是存放string的byte序列的内存的地址。	    

## 3. 修改string
并不是所有的string都可以被修改，如果string是"literal string"时，也就是我们上面说的用""或者"`"扩起来的直接赋值后的字符串，
则其内容是无法修改的，因为这些"literal string"是在数据段中只读区域预先分配好的，这样，如果两个变量内容相同时，可以指向同一个
区域。

假设这样一段程序：

	package main
	
	import (
		"fmt"
	)
	
	func main() {
		s := "abc"
		fmt.Printf("new string:%v\n", s)
	}
	
编译构建出汇编结果：

	go tool compile -N -l -S main.go  > main.S	
在main.S中:

	98 go.string."abc" SRODATA dupok size=3
	99     0x0000 61 62 63	

其中s的str指向的地址就是这里的`go.string."abc"`,其为SRODATA，因此是无法修改的。

但是对于动态产生的字符串，比如说对[]byte进行string强转或者用"+"拼接的字符串：

	package main
	
	import (
		"fmt"
		"unsafe"
	)
	
	type stringStruct struct {
		str unsafe.Pointer
		len int
	}
	
	func main() {
		s1 := "a"
		s2 := "bc"
		s := s1 + s2
		fmt.Printf("s is :%v \n", s)
		p := (*stringStruct)(unsafe.Pointer(&s))
		b := (*byte)(p.str)
		*b = 'e'
		fmt.Printf("after s is :%v \n", s)
	}
	
得到的结果为：

	s is :abc
	after s is :ebc		

这样就将原来的字符串"abc"的第一个字符修改成了"e"。代码中，先取得指向连接后新的字符串内存地址的"unsafe.Pointer"的指针str。
然后将该指针转换成byte后再行赋值，这样就实现了修改string中存储的byte序列的内存中的值了。

## 总结
string的本质是一个包含"void *"指向的内存地址和一个表示字符串长度"int"的struct。所谓string是不可以修改，是从string是
个内置数据类型，没有提供修改操作的层面来表达，或者说是从语言设计层面进行的一个约束。而这里提供的方法则可以认为是一种奇技淫巧。
从string的实现出发，反推出修改保存string内容也就是Spec中的"A string value is a (possibly empty) sequence of bytes"
byte数组的内容。

## 引用
1. [Strings in Golang](https://www.geeksforgeeks.org/strings-in-golang/)
2. [Language Specification](http://docs.golang.org/ref/spec)
3. [src:src/runtime/string.go](https://github.com/golang/go/blob/master/src/runtime/string.go)