导入单词前需运行Anki.py,该操作用于收集资料
资料来源：单词的解释，发音，图片来自Bing：
          句子的发音来自有道

获取的资料有：					填充格式
1、单词英音						%(pr_En)
2、英音发音						%(en)
3、单词美音						%(pr_US)
4、美音发音						%(us)
5、单词的意思					%(mean)
6、单词的第三人称等附加的信息	%(addition)
----搭配、同义、反义可能不存在
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

---14与15选取一项的原因为由于网络或各方面问题，可能导致最后下载的句子不是很完整，故选择例句中相对完整的句子进行导入
---不一定能做到~

卡片的正反面的定义按照填充格式进行%(XX)会被填充成相应的意思，不能填充则...


导入的单词列表应该比较大，最后的导出结果除非有特殊情况，一般显示为完成，但是具体的完成与否的情况将在日志里说明。请在单词导入完成后参考日志来了解真正的导入结果