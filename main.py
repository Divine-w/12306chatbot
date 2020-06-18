import pandas as pd
import fool
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from autoTicket import Demo
from utils import normalize_date, normalize_time

# -----------------------------------------------------
# 加载停用词词典
stopwords = {}
with open(r'stopword.txt', 'r', encoding='utf-8') as fr:
    for word in fr:
        stopwords[word.strip()] = 0


# -----------------------------------------------------


# 定义类
class clf_model:
    """
    该类将所有模型训练、预测、数据预处理、意图识别的函数包括其中
    """

    # 初始化模块
    def __init__(self):
        self.model = ""  # 成员变量，用于存储模型
        self.vectorizer = ""  # 成员变量，用于存储tfidf统计值

    # 训练模块
    def train(self):
        """
        训练结果存储在成员变量中，没有return
        """
        # 从excel文件读取训练样本
        d_train = pd.read_excel("data_train.xlsx")
        # 对训练数据进行预处理
        d_train.sentence_train = d_train.sentence_train.apply(self.fun_clean)
        print("训练样本 = %d" % len(d_train))
        # 利用sklearn中的函数进行tifidf训练
        self.vectorizer = TfidfVectorizer(analyzer="word",
                                          token_pattern=r"(?u)\b\w+\b")  # 注意，这里自己指定token_pattern，否则sklearn会自动将一个字长度的单词过滤筛除
        features = self.vectorizer.fit_transform(d_train.sentence_train)
        print("训练样本特征表长度为 " + str(features.shape))
        # 使用逻辑回归进行训练和预测
        self.model = LogisticRegression(C=10)
        self.model.fit(features, d_train.label)

    # 预测模块（使用模型预测）
    def predict_model(self, sentence):
        # --------------
        # 对样本中没有点特殊情况做特别判断
        if sentence in ["好的", "需要", "是的", "要的", "好", "要", "是"]:
            return 1, 0.8
        # --------------

        sent_features = self.vectorizer.transform([sentence])
        pre_test = self.model.predict_proba(sent_features).tolist()[0]
        clf_result = pre_test.index(max(pre_test))
        score = max(pre_test)
        return clf_result, score

    # 预测模块（使用规则）
    def predict_rule(self, sentence):
        """
        如果模型训练出现异常，可以使用规则进行预测，同时也可以让学员融合"模型"及"规则"的预测方式
        :param sentence:
        :return 预测结果:
        """
        sentence = sentence.replace(' ', '')
        if re.findall(r'不需要|不要|停止|终止|退出|不买|不定|不订', sentence):
            return 2, 0.8
        elif re.findall(r'订|定|预定|买|购', sentence) or sentence in ["好的", "需要", "是的", "要的", "好", "要", "是"]:
            return 1, 0.8
        else:
            return 0, 0.8

    # 预处理函数
    def fun_clean(self, sentence):
        """
        预处理函数
        :输入 用户输入语句:
        :输出 预处理结果:
        """
        # 使用foolnltk进行实体识别
        words, ners = fool.analysis(sentence)
        # 对识别结果按长度倒序排序
        ners = ners[0].sort(key=lambda x: len(x[-1]), reverse=True)
        # 如果有实体被识别出来，就将实体的字符串替换成实体类别的字符串（目的是看成一类单词，看成一种共同的特征）
        if ners:
            for ner in ners:
                sentence = sentence.replace(ner[-1], ' ' + ner[2] + ' ')
        # 分词，并去除停用词
        word_lst = [w for w in fool.cut(sentence)[0] if w not in stopwords]
        output_str = ' '.join(word_lst)
        output_str = re.sub(r'\s+', ' ', output_str)
        return output_str.strip()

    # 分类主函数
    def fun_clf(self, sentence):
        """
        意图识别函数
        :输入 用户输入语句:
        :输出 意图类别，分数:
        """
        # 对用户输入进行预处理
        sentence = self.fun_clean(sentence)
        # 得到意图分类结果（0为“查询”类别，1为“订票”类别，2为“终止服务”类别）
        clf_result, score = self.predict_model(sentence)  # 使用训练的模型进行意图预测
        # clf_result, score = self.predict_rule(sentence)  # 使用规则进行意图预测（可与用模型进行意图识别的方法二选一）
        return clf_result, score


def fun_replace_num(sentence):
    """
    替换时间中的数字（目的是便于实体识别包fool对实体的识别）
    :param sentence:
    :return sentence:
    """
    # 定义要替换的数字
    time_num = {"一": "1", "二": "2", "三": "3", "四": "4", "五": "5", "六": "6", "七": "7", "八": "8", "九": "9", "十": "10",
                "十一": "11", "十二": "12", "两": "2"}
    week_num = {"周1": "周一", "周2": "周二", "周3": "周三", "周4": "周四", "周5": "周五", "周6": "周六", "周7": "周七"}
    date = None
    if '日' in sentence:
        date, sentence = sentence.split('日')
    if '号' in sentence:
        date, sentence = sentence.split('号')
    for k, v in time_num.items():
        sentence = sentence.replace(k, v)
    if '周' in sentence:
        for k, v in week_num.items():
            sentence = sentence.replace(k, v)
    if date:
        return date + '日' + sentence
    else:
        return sentence


def slot_fill(sentence, key=None):
    """
    填槽函数（该函数从sentence中寻找需要的内容，完成填槽工作）
    :param sentence:
    :return slot: （填槽的结果）
    """
    slot = {}
    # 进行实体识别
    words, ners = fool.analysis(sentence)
    to_city_flag = 0  # flag为1代表找到到达城市（作用：当找到到达城市时，默认句子中另一个城市信息是出发城市）
    for ner in ners[0]:
        # 首先对time类别的实体进行信息抽取填槽工作
        if ner[2] == 'time':
            # --------------------
            # 寻找日期的关键词
            date_content = re.findall(
                r'后天|明天|今天|大后天|周末|周一|周二|周三|周四|周五|周六|周日|本周一|本周二|本周三|本周四|本周五|本周六|本周日|下周一|下周二|下周三|下周四|下周五|下周六|下周日|这周一|这周二|这周三|这周四|这周五|这周六|这周日|\d{,2}月\d{,2}号|[\d一二三四五六七八九十]{,2}月[\d一二三四五六七八九十]{,3}日',
                ner[-1])
            slot["date"] = normalize_date(date_content[0]) if date_content else ""
            # 完成日期的填槽
            # --------------------

            # --------------------
            # 寻找具体时间的关键词
            time_content = re.findall(r'\d{,2}点\d{,2}分|\d{,2}点钟|\d{,2}点', ner[-1])
            # 寻找上午下午的关键词
            pmam_content = re.findall(r'上午|下午|早上|晚上|中午|早晨', ner[-1])
            slot["time"] = normalize_time(pmam_content[0], time_content[0]) if pmam_content and time_content else ""
            # 完成时间的填槽
            # --------------------
        # 对location类别对实体进行信息抽取填槽工作
        if ner[2] == 'location' or ner[2] == 'company':
            # --------------------
            # 开始对城市填槽
            # 如果没有指定槽位
            if key is None:
                if re.findall(r'(到|去|回|回去)%s' % (ner[-1]), sentence):
                    to_city_flag = 1
                    slot["to_city"] = ner[-1]
                    continue
                if re.findall(r'从%s|%s出发' % (ner[-1], ner[-1]), sentence):
                    slot["from_city"] = ner[-1]
                elif to_city_flag == 1:
                    slot["from_city"] = ner[-1]
            # 如果指定了槽位
            elif key in ["from_city", "to_city"]:
                slot[key] = ner[-1]
            # 完成出发城市、到达城市的填槽工作
            # --------------------

    return slot


def fun_wait(clf_obj):
    """
    等待询问函数
    :输入 None:
    :输出 用户意图类别:
    """
    # 等待用户输入
    print("\n\n\n")
    print("-------------------------------------------------------------")
    print("-------------------------------------------------------------")
    print("Starting ...")
    sentence = input("客服：请问需要什么服务？(时间请注明上午下午）\n")
    # 对用户输入进行意图识别
    clf_result, score = clf_obj.fun_clf(sentence)
    return clf_result, score, sentence


def fun_search(sentence):
    """
    为用户查询余票
    :param clf_result:
    :param sentence:
    :return: 是否有票
    """
    # 定义槽存储空间
    name = {"time": "出发时间", "date": "出发日期", "from_city": "出发城市", "to_city": "到达城市"}
    slot = {"time": "", "date": "", "from_city": "", "to_city": ""}
    # 使用用户第一句话进行填槽
    sentence = fun_replace_num(sentence)
    slot_init = slot_fill(sentence)
    for key in slot_init.keys():
        slot[key] = slot_init[key]
    # 对未填充对槽位，向用户提问，进行针对性填槽
    while "" in slot.values():
        for key in slot.keys():
            if slot[key] == "":
                sentence = input("客服：请问%s是？\n" % (name[key]))
                sentence = fun_replace_num(sentence)
                slot_cur = slot_fill(sentence, key)
                for key in slot_cur.keys():
                    if slot[key] == "":
                        slot[key] = slot_cur[key]
    print("客服：请稍等，系统正在为您查询...")
    demo = Demo(slot)
    train_list = demo.queryTicket()
    # 查询是否有票，并答复用户（本次查询是否有票使用随机数完成）
    if train_list:
        print("客服：%s %s从%s到%s的票充足，具体车次如下：" % (slot["date"], slot["time"], slot["from_city"], slot["to_city"]))
        print("客服：")
        print('———————————————————————————————————————————————————————————————————————————')
        print('———————————————————————————————————————————————————————————————————————————')
        answer = []
        for i, train in enumerate(train_list):
            answer.append(train)
            if (i + 1) % 3 == 0:
                print(' | '.join(answer))
                print('———————————————————————————————————————————————————————————————————————————')
                answer = []
        print('———————————————————————————————————————————————————————————————————————————')
        # 返回1表示有票
        return 1, demo
    else:
        print("客服：%s %s从%s到%s无票" % (slot["date"], slot["time"], slot["from_city"], slot["to_city"]))
        print("End !!!")
        print("-------------------------------------------------------------")
        print("-------------------------------------------------------------")
        # 返回0表示无票
        return 0, demo


def fun_book(demo):
    """
    为用户订票
    """
    demo = demo
    demo.train = input('客服：请输入你要预定的车次（格式：G1228）\n')
    option = input('客服：请选择登陆方式：1、自动登陆 2、手动登陆 \n')
    demo.usrname = input('客服：请输入账号： \n')
    demo.password = input('客服：请输入密码： \n')
    if option == '1':
        demo.login()
    else:
        demo.manual_login()
    demo.orderTicket()
    print("客服：已为您完成订票。\n\n\n")
    print("End !!!")
    print("-------------------------------------------------------------")
    print("-------------------------------------------------------------")


if __name__ == "__main__":
    # 实例化对象
    clf_obj = clf_model()
    clf_obj.train()
    threshold = 0.55  # 用户定义阈值（当分类器分类的分数大于阈值才采纳本次意图分类结果，目的是排除分数过低的意图分类结果）
    while 1:
        clf_result, score, sentence = fun_wait(clf_obj)
        # -------------------------------------------------------------------------------
        # 状态转移条件（等待-->等待）：用户输入未达到“查询”、“订票”类别的阈值 OR 被分类为“终止服务”
        # -------------------------------------------------------------------------------
        if score < threshold or clf_result == 2:
            continue

        # -------------------------------------------------------------------------------
        # 状态转移条件（等待-->查询）：用户输入分类为“查询” OR “订票”
        # -------------------------------------------------------------------------------
        else:
            search_result, demo = fun_search(sentence)
            if search_result == 0:
                continue
            else:
                # 等待用户输入
                sentence = input("客服：需要为您订票吗？\n")
                # 对用户输入进行意图识别
                clf_result, score = clf_obj.fun_clf(sentence)
                # -------------------------------------------------------------------------------
                # 状态转移条件（查询-->订票）：FUN_SEARCH返回有票 AND 用户输入分类为“订票”
                # -------------------------------------------------------------------------------
                if clf_result == 1:
                    fun_book(demo)
                    continue
