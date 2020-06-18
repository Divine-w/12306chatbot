import requests
import datetime
import calendar


def getVerifyResult(img_path):
    pic_name = img_path
    files = {'pic_xxfile': (pic_name, open(pic_name, 'rb'), 'image/png')}
    response = requests.post('http://littlebigluo.qicp.net:47720/', files=files)
    num = response.text.split('<B>')[1].split('<')[0]
    num_list = list(map(int, num.split()))
    all_list = []
    for i in num_list:
        if i <= 4:
            all_list.append([40 + 72 * (i - 1), 73])
        else:
            i -= 4
            all_list.append([40 + 72 * (i - 1), 145])

    return all_list


def deal_chinese_date(currentYear, month, day):
    """用来处理中文日期，例如三月五号格式的模块"""
    month_digit = 0
    day_digit = 0
    ch_date_dict = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}
    if len(month) > 1:
        ten, single = month[:-1], month[-1]
        month_digit = ch_date_dict.get(ten) + ch_date_dict.get(single)
    elif len(month) == 1:
        month_digit = ch_date_dict.get(month)
    if len(day) == 1:
        day_digit = ch_date_dict.get(day)
    elif len(day) > 1:
        if day.startswith('十'):
            ten, single = day[:-1], day[-1]
            day_digit = ch_date_dict.get(ten) + ch_date_dict.get(single)
        elif day.startswith('二'):
            if len(day) == 2:
                day_digit = 20
            else:
                single = day[-1]
                day_digit = 20 + ch_date_dict.get(single)
        elif day.startswith('三'):
            if len(day) == 2:
                day_digit = 30
            else:
                single = day[-1]
                day_digit = 30 + ch_date_dict.get(single)
    str_time = "{}-{}-{}".format(currentYear, month_digit, day_digit)
    return str(datetime.datetime.strptime(str_time, '%Y-%m-%d').date())


def deal_weektime(today, oneday, time):
    """用来处理这周或者下周的格式的模块"""
    if today.weekday() == 0:
        today += oneday
    if '这' in time:
        while today.weekday() != 0:
            today -= oneday
    if '下' in time:
        while today.weekday() != 0:
            today += oneday
    return today


def normalize_date(time):
    m_n = None
    today = datetime.date.today()
    currentYear = datetime.datetime.now().year

    """以下处理十一月六号 或者7月10日 两种格式的日期"""
    if '月' in time and ('日' in time or '号' in time):
        b = time.split('月')
        month, day = b[0], b[-1][:-1]
        if time.isalpha():
            return deal_chinese_date(currentYear, month, day)
        if month.isdigit() and day.isdigit():
            str_time = "{}-{}-{}".format(currentYear, int(month), int(day))
            return str(datetime.datetime.strptime(str_time, '%Y-%m-%d').date())

    """处理今天，明天，后天，等格式的日期"""
    if time in ['今天', '现在']:
        return str(today)
    oneday = datetime.timedelta(days=1)
    # if time == '昨天':
    #     return str(today - oneday)
    if time == '明天':
        return str(today + oneday)
    if time == '后天':
        return str(today + datetime.timedelta(days=2))
    # if time == '前天':
    #     return str(today - datetime.timedelta(days=2))
    if time == '大后天':
        return str(today + datetime.timedelta(days=3))

    """处理周一，周三，周日格式的日期"""
    m1 = calendar.MONDAY
    m2 = calendar.TUESDAY
    m3 = calendar.WEDNESDAY
    m4 = calendar.THURSDAY
    m5 = calendar.FRIDAY
    m6 = calendar.SATURDAY
    m7 = calendar.SUNDAY

    week_dict = {'一': m1, '二': m2, '三': m3, '四': m4, '五': m5, '六': m6, '日': m7, '末': m6, '天': m7}
    for num in ['一', '二', '三', '四', '五', '六', '日', '末', '天']:
        if num in time:
            m_n = week_dict.get(num)
    if m_n is not None:
        """处理这周三还是下周三的格式的日期"""
        today = deal_weektime(today, oneday, time)
        while today.weekday() != m_n:
            today += oneday
        return str(today)
    return str(today)


def normalize_time(pmam, time):
    hour_bias = 0
    if pmam in ['下午', '晚上']:
        hour_bias = 12
    if '分' in time:
        b = time.split('点')
        hour, minute = b[0], b[-1][:-1]
        str_time = "{}-{}".format(int(hour) + hour_bias, int(minute))
        return str(datetime.datetime.strptime(str_time, '%H-%M').time())
    else:
        hour = time[:-1]
        str_time = str(int(hour) + hour_bias)
        return str(datetime.datetime.strptime(str_time, '%H').time())
