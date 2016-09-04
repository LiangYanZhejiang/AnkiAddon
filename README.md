# AnkiAddon

---
## 材料
### Anki的源码地址：https://github.com/dae/anki
### Anki插件开发资料地址：http://ankisrs.net/docs/addons.html
### Anki已有的媒体导入插件源码地址：https://github.com/hssm/media-import



### Activity Graph

[![Throughput Graph](https://graphs.waffle.io/LiangYanZhejiang/AnkiAddon/throughput.svg)](https://waffle.io/LiangYanZhejiang/AnkiAddon/metrics/throughput)

===
### 使用说明
######  插件名称为：'Words Import...'
		format填充：
		获取的资料有：					填充格式
		1、单词英音						%(pr_En)
		2、英音发音						%(en)
		3、单词美音						%(pr_US)
		4、美音发音						%(us)
		5、单词的意思					%(mean)
		6、单词的第三人称等附加的信息	%(addition)
		7、单词的同义词					%(同义词)
		8、单词的反义词					%(反义词)
		9、单词的搭配					%(搭配)
		10、权威英汉双解				%(权威英汉双解)
		11、带例句的权威英汉双解		%(权威英汉双解_lis)
		12、英汉						%(英汉)
		13、英英						%(英英)

		14、例句						%(Voice_lis_1)    指仅选取一个例句
		15、例句的发音					%(Voice_pr_2)     指选取两个例句，切带读音。14与15仅能选取一项
		16、图片						%(Picture_3)  指的是最多选取三张图片
		17、单词                        %(Word)
		以上%(xxx)为卡片导入的格式自定义，区分大小写，只有数字可以更改。
		
		打开Anki的插件目录，将整个Anki_Import.py及AnkiImport文件夹拷贝至插件目录。
		删除AnkiImport/Words文件夹下的数据，将需要导入的单词列表放到该目录下。-->这个是为了运行DownLoad.exe下载单词用的
		
		单词量比较多时，请先用DownLoad.exe下载单词。
		
