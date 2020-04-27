# 使用go编译go
Go从1.4之后，开始实现自举，也就是可以自己编译自己，具体是什么意思呢？通俗的来说就是Go的编译逻辑都切换成Go来写的了
并且可以通过之前的版本的Go（>=Go1.4)来构建出Go的编译工具链，包括了：

* go go命令的入口
* cmd/asm : go的汇编器
* cmd/cgo : cgo编译器（go和c混合编程时）
* cmd/compile : gc(golang compile)编译器
* cmd/link : 连接器



## 参考
1. [Installing Go from source](https://golang.org/doc/install/source)