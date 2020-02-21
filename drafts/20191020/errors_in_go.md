# Go中的error
在Golang中，我们知道error作为内建类型之一，时常被使用到，最常见的就是如下：

	if err != nil {
	    return err
	}
	
而在定义方法是，一般这样：

	func (s *Scanner) Scan() (token []byte, error)	
通过Golang提供多返回值的特性，来判断一个函数返回成功与否，而不用像C中一样，再单独弄一个全局变量errno。这个是error在Go中最开始
的呈现形式。然后errors包的出现，使得error的使用更方便，通过一个errror.New方法即可创建一个最简单的error。除此之外还可以定义自定义的
error，只要实现了"Error() string"方法即可。但是这样的error错误就够了么？

> Regardless of whether this explanation fits, it is clear that these Go programmers miss a fundamental point about errors: Errors are values.
>
> Values can be programmed, and since errors are values, errors can be programmed.
> 

在三爹之一"Rob Pike"的[Errors are values](https://blog.golang.org/errors-are-values) 说到。

所以在慢慢的实践中，对error值属性的使用中 。"pkg/errors" 为error提供了出错trance堆栈信息。而Go1.13则升级了errors，
使其支持了error层链，让error可以包含其他error。

## normoral error
在Go中的error，Go誉其为“errors as values ”，可以通过两个方法来创建：

	errors: 	func New(text string) error
	fmt: 		func Errorf(format string, a ...interface{}) error
	
这样即可创建一个error，其"Error() string"返回的就是上面的字符串。对于一般的简单错误，这样的操作其实就已经足够了，比如定义一个打开文件的操作，有这么几种错误

	ErrNotFound := errors.New("Can not find the path")
	ErrNoOp		:= errors.New("Don not have the ")

这样的错误信息就够了。

而如果需要跟多的信息时，比如os包里面的os.PathError:


	type PathError struct {
	    Op   string
	    Path string
	    Err  error
	}
	
	func (e *PathError) Error() string { return e.Op + " " + e.Path + ": " + e.Err.Error() }
	
这里自定义了一个结构体，然后这个结构体实现了"Error() string"的方法，其也就是error对象了。但是这个对象里面包含了 文件路径的操作 ”Op“已经操作的对象
文件"Path"。这样就比上面简单的文件ErrNotFound更加详细了，并且还可以根据需要进行相关信息的打印。

所以也就有了Pike老爹说的，要把error当成一个值来用，其可以存储error对象，也可以对该对象进行一些相关的操作，比如找出是哪个文件路径的错误。

## >= go1.3
在Go1.3中，包errors得到了新的设计，新增了一些接口，同时也给fmt包的fmt.Errorf函数格式化增加了一个新的格式选项。

首先errors包提供了:

	func Unwrap(err error) error

方法，来看标准库的源码：

	func Unwrap(err error) error {
		u, ok := err.(interface {
			Unwrap() error
		})
		if !ok {
			return nil
		}
		return u.Unwrap()
	}	
	
如果要Unwrap的error实现了Unwrap方法，那么就返回该实现的结果，否则就返回nil。所以在Go1.3以后，我们的自定义error 除了和以前一样要实现
`Error() string`	 方法为，最好还要实现`Unwrap() error`方法，默认返回自身。这样的核心作用就是在一个比较深的逻辑中，error可以一层一层
的进行收集传递。而"fmt"包为了简化这一操作，对 `func Errorf(format string, a ...interface{}) error` 提供了一个格式化标志"%w"用于
对这个error的Wrap操作，其返回的值是一个实现了`Unwrap() error`新error对象，其Unwrap返回的就是"%w"格式化的参数。比如

	err := fmt.Errorf("Old error")
	newErr := fmt.Errorf("new error wrap the error: %w", err)
	fmt.Printf("old error:%v\n", err)
	fmt.Printf("new error:%v\n", newErr)
	fmt.Printf("unwap error:%v\n", errors.Unwrap(newErr))

运行输出为：

	old error:Old error
	new error:new error wrap the error: Old error
	unwap error:Old error		
	
这里的newErr是一个新的error对象，其"Error()" 返回值为 "new error wrap the error: Old error"。他含有一个"Unwrap"方法，返回的对象
就是上面的老的err。

除此之外还新增了：

	func As(err error, target interface{}) bool
	func Is(err, target error) bool
	
两个方法。其中Is方法，会对err持续的调用Unwrap，直到返回的类型和target是相等的，此时返回true。或者直到Unwrap返回nil，此时返回false。简单理解就是
测试err	的Unwrap链上是否有target这个错误。核心代码为：
	
		for {

			if x, ok := err.(interface{ Is(error) bool }); ok && x.Is(target) {
				return true
			}
			if err = Unwrap(err); err == nil {
				return false
			}
		}
		
而As方法，则在Is的基础上，不是判等，而是判类型，如果其Unwrap链上有个类型为target类型，那么就将target赋值为该Unwrap之后的error。

看个例子：

	package main
	
	import (
		"errors"
		"fmt"
		"os"
	)
	
	func main() {
		if _, err := os.Open("non-existing"); err != nil {
			var pathError *os.PathError
			if errors.As(err, &pathError) {
				fmt.Println("Failed at path:", pathError.Path)
			} else {
				fmt.Println(err)
			}
		}
	
	}		

这里Open函数返回的是个error对象，而通过As将其细分成了os.PathError对象后，就可以取得其中os.PathError.Path成员了。

所以Go1.3中的Error通过Wrap(fmt.Errorf+%w)/UnWrap来实现error包error。这样来应对error归纳。想象一下Java中的异常：

			try {
            first();
       } catch (FileNotFoundException e) {
            // TODO Auto-generated catch block
       } catch (ClassNotFoundException e) {
            // TODO Auto-generated catch block
       }

函数first可以定义为可能抛出一个Exception的方法，而具体是什么错误，则通过其Wrap的是什么错误来定。


## pkg/errors

> Add context using "pkg/errors".Wrap so that the error message provides more context and "pkg/errors".
> Cause can be used to extract the original error.

在[Uber Go Style Guide](https://github.com/uber-go/guide/blob/master/style.md#error-wrapping)的错误处理章节中推荐
使用"pkg/errors"包中的"Wrap"函数来封装错误，这样的错误会携带出错时的上下文，也就是调用堆栈信息。

这个包提供了这样一些主要接口：

	
	func Cause(err error) error
	func Errorf(format string, args ...interface{}) error
	func New(message string) error
	func Wrap(err error, message string) error

为了兼容Go1.13中error包提出来的新接口，又新增了几个接口：

	func As(err error, target interface{}) bool
	func Is(err, target error) bool
	func Unwrap(err error) error


用来兼容标准库中的errors.As、errors.Is、errors.Unwrap。

这个包最大的作用就是，给error增加了一层调用stack层级信息，这样查看error的就不仅仅是一条意义上的信息，同时还携带出错位置的调用信息。

错误信息如官方示例中的：

	err := fn()
	fmt.Printf("%+v\n", err)
	
	// Example output:
	// error
	// github.com/pkg/errors_test.fn
	//         /home/dfc/src/github.com/pkg/errors/example_test.go:47
	// github.com/pkg/errors_test.ExampleCause_printf
	//         /home/dfc/src/github.com/pkg/errors/example_test.go:63
	// testing.runExample
	//         /home/dfc/go/src/testing/example.go:114
	// testing.RunExamples
	//         /home/dfc/go/src/testing/example.go:38
	// testing.(*M).Run
	//         /home/dfc/go/src/testing/testing.go:744
	// main.main
	//         /github.com/pkg/errors/_test/_testmain.go:104
	// runtime.main
	//         /home/dfc/go/src/runtime/proc.go:183
	// runtime.goexit
	//         /home/dfc/go/src/runtime/asm_amd64.s:2059
	// github.com/pkg/errors_test.fn
	// 	  /home/dfc/src/github.com/pkg/errors/example_test.go:48: inner
	// github.com/pkg/errors_test.fn
	//        /home/dfc/src/github.com/pkg/errors/example_test.go:49: middle
	// github.com/pkg/errors_test.fn
	//      /home/dfc/src/github.com/pkg/errors/example_test.go:50: outer
	
通过fmt的"+v"，可以格式化出堆栈信息。

当调用"pkg/errors.New()"时，返回的是一个error对象，其定义为：

	type fundamental struct {
		msg string
		*stack
	}

stack的定义为：

	type stack []uintptr	
是一串指针地址， 其真实存储的是"runtime.Callers()"中返回的调用trace堆栈：

> Callers fills the slice pc with the return program counters of function invocations on the calling goroutine's stack.

也就是"pkg/errors"最核心的内容： 给error套上一层调用trace信息。

除了和"errors.New"方法一样，给定一串字符串，还可以用"pkg/errors.Errorf"用一串格式化的字符串来作为出错信息。

而Uber推荐的"pkg/errors.Wrap"函数返回的error对象是：

	type withStack struct {
		error
		*stack
	}

和上面的New相比，将字符串替换成了一个error。而这个error也不是普通的error，而是：

	type withMessage struct {
		cause error
		msg   string
	}	
	
相当于内嵌了一个普通的error和一段msg。因为这里是Wrap，语义上可以认为是将普通的error包了一层，备注信息为msg，对应Go1.13中的"fmt.Errorf()+%w"。
而这里的cause则对应Go1.13中error
改变的原因。 这个cause对应一个Cause方法：

	func (w *withStack) Cause() error { return w.error }
	

这个"Cause"接口，就如同Go1.3中的errors.Unwrap，会递归的取error的类型，如果其Cause()方法返回了一个Cause类型，则继续获取其Cause()方法。
直到不是Cause的时候，返回其中的error。大概意思就是找到那个最终的出错源头，最开始没有用pkg.errors包过的错误，或者说是原始的错误。



## Go2
error 作为Go2主要的三大改造点中的两个，参考[Go2 Draft](https://go.googlesource.com/proposal/+/master/design/go2draft.md)中《Error handling》和《Error values》 已经 Russ Cox在《GopherCon 2019》上关于新error的描述 [Experiment, Simplify, Ship](https://blog.golang.org/experiment)
以及。

## 参考
1. [Working with Errors in Go 1.13](https://blog.golang.org/go1.13-errors)
2. [Errors are values](https://blog.golang.org/errors-are-values)
3. [Package errors](http://docs.golang.org/pkg/errors/)
4. [pkg/errors](https://github.com/pkg/errors)
5. [Uber Go Style Guide:Error](https://github.com/uber-go/guide/blob/master/style.md#error-wrapping)
6. [Error handling in Upspin](https://commandcenter.blogspot.com/2017/12/error-handling-in-upspin.html)