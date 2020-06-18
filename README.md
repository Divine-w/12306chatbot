# 12306智能客服系统
这是一个基于python和selenium实现的12306智能客服系统，可以通过意图识别模型从对话中判断用户的意图，并通过命名实体识别从用户对话中获取关键信息（出发地、目的地、出发日期和出发时间），
这些信息会被用来进行余票查询和订票功能。
## 依赖库
 - python 3.7.5
 - pandas 1.0.3
 - sklearn 0.22.1
 - foolnltk 0.1.7
 - requests 2.23.0
 - selenium 3.141.0
 - pillow 7.0.0
## 使用说明
直接运行main.py即可开始与智能客服对话，订票时支持自动登陆和手动登录，自动登录会利用第三方打码平台进行验证码识别，从模拟登录到订票全程自动实现但是速度可能比手动登录慢一些，手动登录需要在登录时手动进行验证码识别
## 文件说明
 - main.py python执行脚本
 - autoTicket.py 查票和订票的功能库
 - utils.py 工具库
 - data_train.xlsx 意图分类训练数据
 - stopword.txt 停用词
 ## 对话示例

 <img src="https://github.com/Divine-w/12306chatbot/blob/master/%E5%AF%B9%E8%AF%9D%E7%A4%BA%E4%BE%8B.png" width="200"  alt="对话示例"/>
