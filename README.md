# 12306智能客服对话系统
这是一个基于python和selenium实现的12306智能客服对话系统，在对话过程中对用户意图进行识别触发状态间的切换，并通过命名实体识别从对话中获取关键信息进行槽位填充（出发地、目的地、出发日期和出发时间），依靠这些信息从12306官网进行余票查询和车票预定。
## 依赖库
 - python 3.7.5
 - pandas 1.0.3
 - sklearn 0.22.1
 - foolnltk 0.1.7
 - requests 2.23.0
 - selenium 3.141.0
 - pillow 7.0.0
## 使用说明
直接运行main.py即可开始与智能客服对话，订票时支持自动登陆和手动登录，自动登录会利用第三方打码平台进行验证码识别，手动登录需要在登录时手动进行验证码识别，余票查询默认查询二等座余票。
## 文件说明
 - main.py python执行脚本
 - autoTicket.py 实现查票和订票功能
 - utils.py 工具库
 - data_train.xlsx 意图分类训练数据
 - stopword.txt 停用词
 ## 对话示例

 <img src="https://github.com/Divine-w/12306chatbot/blob/master/%E5%AF%B9%E8%AF%9D%E7%A4%BA%E4%BE%8B.png" width="600"  alt="对话示例"/>
