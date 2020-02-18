---
title: "pprof of golang"
date: 2018-06-18T22:07:36+08:00
categories:
  - "工程实践"
tags:
  - "pprof"
  - "golang"

description: "而Golang因为runtime的存在，从语言层面就提供了prof工具，提供出来的接口都是`pprof`，所以我们管他叫做pprof"
---


prof这个没有明确定义的软件开发术语，但是作为软件开发行业的一员，大家应该都知道有这么一个东西，也知道他主要是解决哪块问题的，
否则也不会来看我这篇文章了。在c++界，有个知名的产品叫gperf，是Google大厂出品的，其形成了一系列的工具集
[gperftools](https://github.com/gperftools/gperftools)。如果你是传统Linux下做C或者C-Like开发的对gprof肯定也
不陌生,其是[GNU Binutils](https://sourceware.org/binutils/)工具集的一个工具。而Golang因为runtime的存在，从语言层面
就提供了prof工具，提供出来的接口都是"pprof"，所以我们管他叫做pprof。

Golang提供内置prof主要提供了如下几个功能：

|项目|含义|
|---|---|
|"allocs" | "A sampling of all past memory allocations"|
|"block" | "Stack traces that led to blocking on synchronization primitives"|
|"cmdline" | "The command line invocation of the current program"|
|"goroutine" | "Stack traces of all current goroutines"|
|"heap" | "A sampling of memory allocations of live objects. You can specify the gc GET parameter to run GC before taking the heap |sample."|
|"mutex" | "Stack traces of holders of contended mutexes"|
|"profile" | "CPU profile. You can specify the duration in the seconds GET parameter. After you get the profile file, use the go tool pprof command to investigate the profile."|
|"threadcreate" | "Stack traces that led to the creation of new OS threads"|
|"trace" | "A trace of execution of the current program. You can specify the duration in the seconds GET parameter. After you get the trace file, use the go tool trace command to investigate the trace."|

通过关注对应性能项目的统计，就可以针对性的进行一些调优工作。

<!--more-->

## 1. 生成pprof文件

和其他prof工具一样，要想进行prof分析，首先要运行程序并生成对应prof文件，以供其他工具解析并进行分析，比如排序统计、火焰图分析等。Golang提供
的pprof支持两种生成prof文件的方法，一种是在代码里面打桩，在需要prof开始的地方和结束的地方手动调用相关接口，并生成相关的prof文件。另一种是
开启一个常驻分析进程，并开通一个web api供实时获取当前的prof统计状态。

### 1.1 片段代码分析
在"runtime/pprof"包中有两套接口：

	func StartCPUProfile(w io.Writer) error
	func StopCPUProfile
	
	func WriteHeapProfile(w io.Writer) error
	w.Close()

分别用于统计CPU的性能和内存的性能，在需要开始统计的地方调用"StartCPUProfile",在执行完需要分析的逻辑后执行"WriteHeapProfile"。比如：

	func main() { 
		cpuprofile := "myapp.pprof"
		f, err := os.Create(*cpuprofile) 
		if err != nil {
			log.Fatal(err) 
		}
		pprof.StartCPUProfile(f)
		defer pprof.StopCPUProfile()
		...
	}
	
这里就是对整个main的生命周期进行了CPU的性能统计，并在程序运行后，将结果存储于文件"myapp.pprof"中。切记`pprof.StopCPUProfile()`一定
要被调用，比如在这之前直接用os.Exit或者什么信号通知结束了程序，那么最后的结果可能还没有flush到文件。

同样的，如果需要对main函数的整个生命周期做内存统计，则可以有：


	func main() {
		memprofile := "myapp.mprof"
		f, err := os.Create(*memprofile) 
		if err != nil {
			log.Fatal(err) 
		}
		
		...
		pprof.WriteHeapProfile(f) 
		f.Close()
		
	}

这里一样，在统计后，写入到文件	"myapp.mprof"。统计数据是从调用pprof.WriteHeapProfile开始，直到关闭该文件。

### 1.2 常驻性服务分析
上面的片段统计，对于具体到某个模块时，可以聚焦。但是我们一般的服务器端程序是一个deamon的常驻程序，最开始也不知道是哪个模块的问题，
对于这样的，Golang提供了一个实时统计的并有Web API接口的服务。只需要在代码中引入：

	import _ "net/http/pprof"  
	
	go func() {  
		log.Println(http.ListenAndServe("localhost:6060", nil))  
	}()
	
既隐式引用	"net/http/pprof" ，然后在开一个Web 服务就可以了。在"src/net/http/pprof"中会注册handler:

	func init() {
		http.HandleFunc("/debug/pprof/", Index)
		http.HandleFunc("/debug/pprof/cmdline", Cmdline)
		http.HandleFunc("/debug/pprof/profile", Profile)
		http.HandleFunc("/debug/pprof/symbol", Symbol)
		http.HandleFunc("/debug/pprof/trace", Trace)
	}
	
这样上面启的HTTP服务"/debug/pprof"路径下就会得到多出如下几个页面：

![debug_pprof](../images/debug_pprof.png)

点击响应的路径地址，可以看到对应的详细的统计。这些接口还可以加上"?seconds=30",表示统计最近30s的结果，通过参数seconds参数来设定统计
间隔，单位为秒。

那么如何获得和上面一样的pprof和mprof文件呢？只需要访问如下两个地址，就可以获得相应文件了：

	http://127.0.0.1:6060/debug/pprof/profile    // CPU的prof文件
	http://127.0.0.1:6060/debug/pprof/heap     // 内存的prof文件


## 2. 理解pprof结果
无论用上面的哪种方法得到的prof文件，只要有了这个文件，我们就可以对文件进行分析了。具体的分析方法有：

* go tool pprof 工具，该工具产生一个类似命令行的交互界面，使用上类似top命令
* go tool pprof -svg 生成调用关系图，这个图上展示了函数之间的调用关系以及消耗
* 第三方可视化工具如：[FlameGraph](https://github.com/brendangregg/FlameGraph)
、[Speedscope](https://www.speedscope.app/)、[go-torch](https://github.com/uber/go-torch)


### 2.1 命令行
Golang提供解析prof文件的工具，在`go tool pprof`中，使用方式为：

	go tool pprof your_bin_file your_pprof_file
	
比如：

	go tool pprof pprofdemo pprofdemo.pprof
	
这里的pprofdemo为我们的demo程序，pprofdemo.pprof为web接口"/debug/pprof/profile"或者"pprof.StartCPUProfile"产生的
CPU的profile文件。

	cz$ go tool pprof pprofdemo pprofdemo.pprof
	File: pprofdemo
	Type: cpu
	Duration: 1.23s, Total samples = 1.04s (84.47%)
	Entering interactive mode (type "help" for commands, "o" for options)
	(pprof)
	
这里会出现一个类似gdb的交互界面，执行top命令可以按函数自身消耗时间进行排序：

	(pprof) top
	Showing nodes accounting for 1.04s, 100% of 1.04s total
	Showing top 10 nodes out of 15
	      flat  flat%   sum%        cum   cum%
	     0.61s 58.65% 58.65%      0.61s 58.65%  crypto/md5.block
	     0.12s 11.54% 70.19%      0.12s 11.54%  runtime.nanotime
	     0.09s  8.65% 78.85%      0.09s  8.65%  runtime.memmove
	     0.06s  5.77% 84.62%      0.89s 85.58%  crypto/md5.Sum
	     0.05s  4.81% 89.42%      0.75s 72.12%  crypto/md5.(*digest).Write
	     0.04s  3.85% 93.27%      0.77s 74.04%  crypto/md5.(*digest).checkSum
	     0.03s  2.88% 96.15%      0.92s 88.46%  main.optimizCPU
	     0.02s  1.92% 98.08%      0.02s  1.92%  crypto/md5.(*digest).Reset
	     0.01s  0.96% 99.04%      0.01s  0.96%  encoding/binary.littleEndian.PutUint64
	     0.01s  0.96%   100%      0.01s  0.96%  runtime.duffzero	
其中"flat"表示函数自身消耗时间，不包含其内部函数调用，比如这里的crypto/md5.block耗时0.61s。而"flat%"表示该函数花费时间占总共时间的百分比。
而"sum%"则表示从上到下的总和，比如"crypto/md5.Sum"的"sum%"为84.62%,其值是上面三行的flat%加上本行之和。"cum"表示该函数及其内部调用的其他
函数总共耗时，比如这里的"main.optimizCPU"内部调用了"crypto/md5.Sum"，所以"main.optimizCPU"的cum为0.92s，其包含了"crypto/md5.Sum"
花费的0.89s。而"cum%"则表示其在所有时间中的占比。

同样的方法我们再用一个内存的profile文件尝试下：

	cz$ go tool pprof pprofdemo pprofdemo.mprof
	File: pprofdemo
	Type: inuse_space
	Entering interactive mode (type "help" for commands, "o" for options)
	(pprof)

这里将pprofdemo.pprof换成pprofdemo.mprof文件，该文件是从"/debug/pprof/heap"或者"pprof.WriteHeapProfile"产生的。和上面一样，
也会得到一个交互式命令行，我们执行top命令：

(pprof) top
Showing nodes accounting for 8696.01kB, 100% of 8696.01kB total
      flat  flat%   sum%        cum   cum%
    8184kB 94.11% 94.11%  8696.01kB   100%  main.optimizMemory
  512.01kB  5.89%   100%   512.01kB  5.89%  main.newByte
         0     0%   100%  8696.01kB   100%  main.main
         0     0%   100%  8696.01kB   100%  runtime.main
         
这里的flat/cum/sum和上面的定义一样，只是其值表示的不是CPU耗时，而是实际内存消耗。

除了top命令，还可以用list命令，来查看具体 的函数代码和其内部消耗，比如这里我们想看看 `main.newByte` 的实现：

	(pprof) list main.newByte
	Total: 8.49MB
	ROUTINE ======================== main.newByte in pprofdemo/main.go
	  512.01kB   512.01kB (flat, cum)  5.89% of Total
	         .          .      6:	"os"
	         .          .      7:	"runtime/pprof"
	         .          .      8:)
	         .          .      9:
	         .          .     10:func newByte() *byte {
	  512.01kB   512.01kB     11:	i := new(byte)
	         .          .     12:	return i
	         .          .     13:}
	         .          .     14:
	         .          .     15:func optimizMemory() []*byte {
	         .          .     16:	const s int = 1024 * 1023

这里看到，实际消耗内存的，就是这个内建的内存分配函数"new"。

### 2.2 调用关系图
这个`go tool pprof`工具不仅提供了交互式界面，还提供了一个依赖graphviz生成svg格式图片的工具。图片是一个调用关系图，
每个节点都展示了该函数的消耗，跟交互界面的top命令+list命令类似。只需要执行：

	go tool pprof -svg pprofdemo.pprof
	Generating report in profile001.svg
	
生成的文件	profile001.svg 为结果，可以用chrome浏览器打开：

![profile001.svg](../images/pprof.png)

每个节点里面展示了耗时和所占百分比，与上面top命令的前三列意义雷同，箭头上的时间表示
从这节点往下所有的总消耗时间。

### 2.3 可视化工具

如果觉得上面的文字结果还不够直观，社区内还有很多图形化的分析工具，这里就不一一介绍使用方式，可以自行在其官网查看如何使用。

#### FlameGraph
[FlameGraph](https://github.com/brendangregg/FlameGraph)是一个很强大的栈分析工具，可以绘制火焰图，并支持Linux prof、DTrace等多种格式数据，当然也支持Golang的pprof格式，
来看下效果图:
![flame](../images/flame.png)

#### speedscope
[speedscope](https://www.speedscope.app/) 提供了一个在线的prof分析界面，只要把prof文件拖拽到界面上就可以生成类似xcode的Instruments的
界面。除了在线使用外，也可以离线使用，离线使用从[https://github.com/jlfwong/speedscope/releases](https://github.com/jlfwong/speedscope/releases)
下载最新版本的speedscope，然后解压打开index.html文件即可：

![speedscope](../images/speedscope.gif)

speedscope不仅支持Golang的pprof，甚至支持:

![scope2](../images/scope2.png)

好多种，具体使用可以参见[Github](https://github.com/jlfwong/speedscope/)


## 3. 调优示例 

现在来看一个具体的示例：

	package main
	
	import (
		"crypto/md5"
		"log"
		"os"
		"runtime/pprof"
	)
	
	func newInt32() *int32 {
		i := new(int32)
		return i
	}
	
	func optimizMemory() []*int32 {
		const s int = 1024 * 1024
		var buf []*int32
		for i := 0; i < s; i++ {
			ii := newInt32()
			buf = append(buf, ii)
		}
		return buf
	}
	
	func optimizCPU() {
		for i := 0; i < 10000000; i++ {
			data := []byte("These pretzels are making me thirsty.")
			md5.Sum(data)
		}
	}
	
	func main() {
		cpuprofile := "pprofdemo.pprof"
		fc, err := os.Create(cpuprofile)
		if err != nil {
			log.Fatal(err)
		}
		pprof.StartCPUProfile(fc)
		optimizCPU()
		pprof.StopCPUProfile()
	
		memprofile := "pprofdemo.mprof"
		fm, err := os.Create(memprofile)
		if err != nil {
			log.Fatal(err)
		}
		buf := optimizMemory()
		println("buf len:", len(buf))
		pprof.WriteHeapProfile(fm)
		fm.Close()
	}
	
这里写了两个函数，一个是消耗CPU的`optimizCPU`,他里面实际上是调用md5算法进行CPU的消耗；另一个是"optimizMemory",里面通过分配int32
对象数组来消耗内存。

然后build进行运行：

	cz$ go build
	cz$ ./pprofdemo
	buf len: 1048576
	
会产生两个文件：

	pprofdemo.mprof	pprofdemo.pprof
	
然后用上面介绍的"go tool pprof"工具来解析：

	cz$ go tool pprof pprofdemo pprofdemo.pprof
	File: pprofdemo
	Type: cpu
	Duration: 1.23s, Total samples = 1.03s (83.67%)
	Entering interactive mode (type "help" for commands, "o" for options)
	(pprof) top10
	Showing nodes accounting for 1.03s, 100% of 1.03s total
	Showing top 10 nodes out of 14
	      flat  flat%   sum%        cum   cum%
	     0.62s 60.19% 60.19%      0.62s 60.19%  crypto/md5.block
	     0.10s  9.71% 69.90%      0.77s 74.76%  crypto/md5.(*digest).Write
	     0.09s  8.74% 78.64%      0.09s  8.74%  runtime.nanotime
	     0.08s  7.77% 86.41%      0.82s 79.61%  crypto/md5.(*digest).checkSum
	     0.05s  4.85% 91.26%      0.05s  4.85%  runtime.memmove
	     0.04s  3.88% 95.15%      0.93s 90.29%  main.optimizCPU
	     0.03s  2.91% 98.06%      0.89s 86.41%  crypto/md5.Sum
	     0.01s  0.97% 99.03%      0.01s  0.97%  encoding/binary.littleEndian.PutUint64
	     0.01s  0.97%   100%      0.01s  0.97%  runtime.usleep
	         0     0%   100%      0.93s 90.29%  main.main
	         
直接执行一个`top10`的命令。如上面打印的，在我的main包中，main.optimizCPU这个函数里面调用的其他函数占据应该是

	90.29%-3.88% = 86.41%
	
在看这个函数里面	，直接调用的就是`md5.Sum`,从上面的数据来看，刚好是86.41%。所以基本就定位了是这个函数执行消耗了主要的CPU。

然后再来看内存的消耗，执行命令：

	cz$ go tool pprof pprofdemo pprofdemo.mprof
	File: pprofdemo
	Type: inuse_space
	Entering interactive mode (type "help" for commands, "o" for options)
	(pprof) top
	Showing nodes accounting for 10.99MB, 100% of 10.99MB total
	      flat  flat%   sum%        cum   cum%
	    9.99MB 90.90% 90.90%    10.99MB   100%  main.optimizMemory
	       1MB  9.10%   100%        1MB  9.10%  main.newByte
	         0     0%   100%    10.99MB   100%  main.main
	         0     0%   100%    10.99MB   100%  runtime.main
	         
从上面的prof来看，主要就是	"main.optimizMemory "这个函数消耗了这个程序使用的所有的内存，我们使用一个新的命令：

	(pprof) list main.optimizMemory
	Total: 10.99MB
	ROUTINE ======================== main.optimizMemory in pprofdemo/main.go
	    9.99MB    10.99MB (flat, cum)   100% of Total
	         .          .     14:
	         .          .     15:func optimizMemory() []*byte {
	         .          .     16:	const s int = 1024 * 1023
	         .          .     17:	var buf []*byte
	         .          .     18:	for i := 0; i < s; i++ {
	         .        1MB     19:		ii := newByte()
	    9.99MB     9.99MB     20:		buf = append(buf, ii)
	         .          .     21:	}
	         .          .     22:	return buf
	         .          .     23:}
	         .          .     24:
	         .          .     25:func optimizCPU() {
	         
list后面跟具体函数名，可以展示这个函数里面的统计情况。可以看到这里的for循环总共执行了1M次，而每次需要消耗1Byte,也就是newByte总共消耗了1MB，
而buildin函数的append则总共花费了9.99MB。如果你执行多次pprofdemo，你会发现每次这个append的消耗都是不一样的。这是因为append会触发slice的
动态内存分配。所以这里如果要优化，我们得改造这个append。假设我们预先分配好一个够大的数组，就可以优雅的解决问题了,先将代码改成：

	func optimizMemory() []*byte {
		const s int = 1024 * 1023
		var buf [1024 * 1023]*byte
		for i := 0; i < s; i++ {
			ii := newByte()
			buf[i] = ii
		}
		return buf[:]
	}

然后再来运行看prof文件

	cz$ go tool pprof pprofdemo pprofdemo.mprof
	File: pprofdemo
	Type: inuse_space
	Entering interactive mode (type "help" for commands, "o" for options)
	(pprof) top
	Showing nodes accounting for 8.99MB, 100% of 8.99MB total
	      flat  flat%   sum%        cum   cum%
	    7.99MB 88.88% 88.88%     8.99MB   100%  main.optimizMemory
	       1MB 11.12%   100%        1MB 11.12%  main.newByte
	         0     0%   100%     8.99MB   100%  main.main
	         0     0%   100%     8.99MB   100%  runtime.main
	(pprof) list main.optimizMemory
	Total: 8.99MB
	ROUTINE ======================== main.optimizMemory in pprofdemo/main.go
	    7.99MB     8.99MB (flat, cum)   100% of Total
	         .          .     12:	return i
	         .          .     13:}
	         .          .     14:
	         .          .     15:func optimizMemory() []*byte {
	         .          .     16:	const s int = 1024 * 1023
	    7.99MB     7.99MB     17:	var buf [1024 * 1023]*byte
	         .          .     18:	for i := 0; i < s; i++ {
	         .        1MB     19:		ii := newByte()
	         .          .     20:		buf[i] = ii
	         .          .     21:	}
	         .          .     22:	return buf[:]
	         .          .     23:}
	         .          .     24:
	(pprof)

这里buf数组就固定是8MB，因为这里存放的是一个指针，而我的机器是64bit的，所以1M个就是8MB大小了。这样总内存就优化了近2MB。

## 总结
在Golang的性能调优中，其实我们主要关心的就是内存分配和其使用产生的GC，以及CPU的消耗。其他类似mutex、threadcreate则可以做一些辅助
判断。调优的关键在于获得程序运行的prof文件，获得该文件后，有多种工具来进行解析，然后从中进行分析，协助我们判断有没有改进的空间，以及
怎么样去修改。

## 参考
1. [src:src/runtime/mprof.go](https://golang.org/src/runtime/mprof.go.)
2. [src:src/runtime/cpuprof.go](https://golang.org/src/runtime/cpuprof.go.)
3. [Profiling Go Programs](https://blog.golang.org/profiling-go-programs)
4. [runtime/pprof](http://docs.golang.org/pkg/runtime/pprof/)
5. [Profiling Go programs with pprof](https://jvns.ca/blog/2017/09/24/profiling-go-with-pprof/)
6. [Profiling your Golang app in 3 steps](https://coder.today/tech/2018-11-10_profiling-your-golang-app-in-3-steps/)