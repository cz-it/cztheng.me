---
title: "TOML Spec 脚注"
date: 2018-04-16T22:07:36+08:00
categories:
  - "工程实践"
tags:
  - "toml"

description: "TOML是什么？TOML:Tom's Obvious, Minimal Language。简单来说就是Github的一位创始人觉得YAML太复杂了，所以设计了一款简单的标记语言。"
---


TOML是什么？TOML:Tom's Obvious, Minimal Language。简单来说就是Github的一位创始人觉得YAML太复杂了，所以设计了一款简单的标记语言。 那么YAML又是嘛？YAML: YAML Ain't Makrup Language。又是玩骇客那一套递归缩写，类似GNU ：GNU's Not Unix! 这里说的“Markup Language”其实也不神秘，程序猿都知道XML、HTML就是这类语言。而标记语言YAML一般使用在配置文件、文本书写（类比Markdown，Sphinx就是用的YAML来写内容）。作者Tom就是觉得YAML太过复杂(Spec 84页),因此定义了这个新的标记语言。而他最常用的地方也就是在配置文件中，可以和INI文件做对比。

如果你用过JSON做配置文件，那肯定会遇到过一个问题就是各种大小括号和结尾的逗号，一旦不小心就会导致解析失败。再设想有强迫症的你，要是JSON配置文件被人改的格式不统一，或者不同编辑器（Linux/Windows）导致的换行问题是又多揪心。而TOML则更清晰简单，容易理解，格式整洁，不易出错。

<!--more-->

## 来看个例子

> 这个例子引自官方的v0.4.0的Spec

    # This is a TOML document. Boom.

	title = "TOML Example"

	[owner]
	name = "Lance Uppercut"
	dob = 1979-05-27T07:32:00-08:00 # First class dates? Why not?

	[database]
	server = "192.168.1.1"
	ports = [ 8001, 8001, 8002 ]
	connection_max = 5000
	enabled = true

	[servers]

	  # You can indent as you please. Tabs or spaces. TOML don't care.
	  [servers.alpha]
	  ip = "10.0.0.1"
	  dc = "eqdc10"

	  [servers.beta]
	  ip = "10.0.0.2"
	  dc = "eqdc10"

	[clients]
	data = [ ["gamma", "delta"], [1, 2] ]

	# Line breaks are OK when inside arrays
	hosts = [
	  "alpha",
	  "omega"
	]

相比较JSON是不是简单的多。

## 基本语法解析

### 注释

和Shell一样采用"#"做单行注释，没有JSON礼貌的"/**/"多行注释

    # I am a comment. Hear me roar. Roar.
	key = "value" # Yeah, you can do this.

### 字符串

TOML中的字符串只能包含UTF-8字符，有四种表达方式：基本字符串、多行基本字符串、字面字符串（Literal String)、多行字面字符串。

1. 基本字符串：使用双引号括起来一段字符串内容，如果内容中有双引号什么的需要使用反斜杠进行转义，这个就和一般编程语言中的字符串一样。

    "I'm a string. \"You can quote me\". Name\tJos\u00E9\nLocation\tSF."

这里的“\t”、“\u00E9”就是一般的UTF-8表示。

2. 多行基本字符串：跟Python一样，使用三个双引号括起来就可以了。

	key1 = """
	Roses are red
	Violets are blue"""

和C语言一样，如果希望多行内容不包含换行，可以用反斜杠放在一行的末尾：

	# The following strings are byte-for-byte equivalent:
	key1 = "The quick brown fox jumps over the lazy dog."

	key2 = """
	The quick brown \


	  fox jumps over \
		the lazy dog."""

	key3 = """\
		   The quick brown \
		   fox jumps over \
		   the lazy dog.\
		   """



3. 字面字符串（Literal String)
何为"Literal String"其实就是所见即所得，不用转义的。TOML用“'”单引号来表示，比如将Windows的路径放到单引号中：

	# What you see is what you get.
	winpath  = 'C:\Users\nodejs\templates'
	winpath2 = '\\ServerX\admin$\system32\'
	quoted   = 'Tom "Dubs" Preston-Werner'
	regex    = '<\i\c*\s*>'

4. 多行字面字符串
同样的，如果多行字符串里面不想转义，可以用三个单引号来引用：

	regex2 = '''I [dw]on't need \d{2} apples'''
	lines  = '''
	The first newline is
	trimmed in raw strings.
	   All other whitespace
	   is preserved.
	'''

### 整数
和一般程序语言中的整数一样，并支持现代化语言如Swift的中的西方千位置的助记符。

	+99
	42
	0
	-17
	1_000  # 千位助记符
	5_349_221

### 浮点数

和一般程序语言中的浮点数一样，同时也支持上面的千位助记符和科学计数法

	# fractional
	+1.0
	3.1415
	-0.01

	# exponent
	5e+22
	1e6
	-2E-2

	# both
	6.626e-34

    9_224_617.445_991_228_313
	1e1_000

### 布尔值
`true`表示真，`false`表示假

### 日期
TOML提供了日期类型，这种配置文件急需的类型，只要按照[RFC 3339](http://tools.ietf.org/html/rfc3339)标准格式写就可以了：

	1979-05-27T07:32:00Z
	1979-05-27T00:32:00-07:00
	1979-05-27T00:32:00.999999-07:00

### 数组
数组是通过"[]"括起来的*同一类型*的序列。并可以写在多行中：

	[ 1, 2, 3 ]
	[ "red", "yellow", "green" ]
	[ [ 1, 2 ], [3, 4, 5] ]
	[ "all", 'strings', """are the same""", '''type'''] # this is ok
	[ [ 1, 2 ], ["a", "b", "c"] ] # this is ok
	[ 1, 2.0 ] # note: this is NOT ok
	key = [
	  1, 2, 3
	]

	key = [
	  1,
	  2, # this is ok
	]


### 字典
字典通过一个"[]"中括号里面加上字典名表示，从这个中括号到下一个中括号或者文件结束表示一个字典的内容。

	[table]
	key = "value"
	bare_key = "value"
	bare-key = "value"

	"127.0.0.1" = "value"
	"character encoding" = "value"
	"ʎǝʞ" = "value"

这里Kye可以用引号也可以不用引号，如果不用引号，那么Key只能是数字、字符、下划线或者破折号的组合。其他如点号什么的则需要用双引号。

通过在字典名中加入"."号表示字典的字典：

    [dog."tater.man"]
    type = "pug"

表示JSON为

    { "dog": { "tater.man": { "type": "pug" } } }

这里字典名中的第一个“.”表示下一级字典，后面的句点用双引号括起来了，所以当做一般的Key对待。

既然是字典，那么key肯定不能重复，大家应该都理解，但是下面这种场景需要注意下：

	[a]
	b = 1  # key with "b"

	[a.b]  # another key with "b"
	c = 2


### 字典数组

上面基本介绍了TOML支持的所有格式，并且通过组合可以得到很多种数据内容。但是类似如下的JSON该怎么表示呢？

	{
	  "products": [
		{ "name": "Hammer", "sku": 738594937 },
		{ },
		{ "name": "Nail", "sku": 284758393, "color": "gray" }
	  ]
	}

TOML为此设计了一个专门的类型：字典数组

	[[products]]
	name = "Hammer"
	sku = 738594937

	[[products]]

	[[products]]
	name = "Nail"
	sku = 284758393
	color = "gray"

这里用两个"[["表示一个数组，一个元素是字典的数组

再来看一个超级复杂的：

	[[fruit]]
	  name = "apple"

	  [fruit.physical]
		color = "red"
		shape = "round"

	  [[fruit.variety]]
		name = "red delicious"

	  [[fruit.variety]]
		name = "granny smith"

	[[fruit]]
	  name = "banana"

	  [[fruit.variety]]
	  name = "plantain"

是不是有点晕，一点点拨开，其JSON表示为：

	{
	  "fruit": [
		{
		  "name": "apple",
		  "physical": {
			"color": "red",
			"shape": "round"
		  },
		  "variety": [
			{ "name": "red delicious" },
			{ "name": "granny smith" }
		  ]
		},
		{
		  "name": "banana",
		  "variety": [
			{ "name": "plantain" }
		  ]
		}
	  ]
  }


## 总结
上面是在阅读[TOML v4.0 Spec](https://github.com/toml-lang/toml/blob/master/versions/en/toml-v0.4.0.md)时的脚注，整个Spec才10页A4纸，基本看着就可以直接写内容了，不会像YAML一样，随便写就能写出语法错误。当然类似字典数组这些需要适应一下。总的来说TOML有INI的直观，也有JSON类似的灵活。
