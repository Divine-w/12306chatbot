from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from utils import getVerifyResult
from PIL import Image
from time import sleep
import datetime
import re


class Demo:
    def __init__(self, slot):
        self.usrname = None
        self.password = None
        self.fromStation = slot["from_city"]
        self.toStation = slot["to_city"]
        self.train_date = slot['date']
        self.target_time = slot['time']
        self.train = None
        self.seat_code = {'一等座': 'M', '二等座': 'O', '硬座': '1',
                          '硬卧': '3', '软卧': '4', '商务座': '9'}
        self.choice = '二等座'
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(executable_path='./chromedriver.exe', chrome_options=chrome_options)

    def login(self):
        self.driver = webdriver.Chrome(executable_path='./chromedriver.exe')
        self.driver.get('https://kyfw.12306.cn/otn/login/init')
        sleep(2)
        self.driver.save_screenshot('main.png')
        img_tag = self.driver.find_element_by_xpath('//*[@id="loginForm"]/div/ul[2]/li[4]/div/div/div[3]/img')
        location = img_tag.location
        size = img_tag.size
        rangle = (int(location['x']) * 1.25, int(location['y']) * 1.25, int(location['x'] + size['width']) * 1.25,
                  int(location['y'] + size['height']) * 1.25)
        print(rangle)
        img = Image.open('main.png')
        frame = img.crop(rangle)
        frame.save('code.png')
        result = getVerifyResult('code.png')
        for xy in result:
            x = xy[0]
            y = xy[1]
            ActionChains(self.driver).move_to_element_with_offset(img_tag, x, y).click().perform()
            sleep(1)
        self.driver.find_element_by_id('username').send_keys(self.usrname)
        sleep(1)
        self.driver.find_element_by_id('password').send_keys(self.password)
        sleep(1)
        self.driver.find_element_by_id('loginSub').click()
        while self.driver.current_url == 'https://kyfw.12306.cn/otn/login/init' \
                or self.driver.current_url == 'https://kyfw.12306.cn/otn/login/init#':
            print('等待登陆中...')
            sleep(3)

    def manual_login(self):
        self.driver = webdriver.Chrome(executable_path='./chromedriver.exe')
        self.driver.get('https://kyfw.12306.cn/otn/login/init')
        self.driver.find_element_by_id('username').send_keys(self.usrname)
        sleep(1)
        self.driver.find_element_by_id('password').send_keys(self.password)
        sleep(1)
        print('客服：请手动点击验证码登陆')
        while self.driver.current_url == 'https://kyfw.12306.cn/otn/login/init' \
                or self.driver.current_url == 'https://kyfw.12306.cn/otn/login/init#':
            print('等待登陆中...')
            sleep(3)

    def queryTicket(self):
        today = datetime.datetime.today()
        dep_date = datetime.datetime.strptime(self.train_date, '%Y-%m-%d')
        if (dep_date - today).days > 29:
            return []
        self.driver.get("https://kyfw.12306.cn/otn/leftTicket/init")
        fromStation = self.driver.find_element_by_id('fromStationText')
        fromStation.click()
        fromStation.clear()
        fromStation.send_keys(self.fromStation + '\n')
        toStation = self.driver.find_element_by_id('toStationText')
        toStation.click()
        toStation.clear()
        toStation.send_keys(self.toStation + '\n')
        self.driver.execute_script("document.getElementById('train_date').removeAttribute('readonly')")
        trainDate = self.driver.find_element_by_id("train_date")
        trainDate.clear()
        trainDate.send_keys(self.train_date)
        self.driver.find_element_by_id("query_ticket").click()
        WebDriverWait(self.driver, 100).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'number')))
        train_tags = self.driver.find_elements_by_xpath('//div[@class="train"]//a')
        trains = []
        for train_tag in train_tags:
            trains.append(train_tag.get_attribute('textContent'))
        time_tags = self.driver.find_elements_by_xpath('//strong[@class="start-t"]')
        times = []
        for time_tag in time_tags:
            times.append(time_tag.get_attribute('textContent'))
        seat_tags = self.driver.find_elements_by_xpath('//div[@class="t-list"]//tr/td[4]')
        seats = []
        for seat_tag in seat_tags:
            seats.append(seat_tag.get_attribute('textContent'))
        train_list = []
        assert len(trains) == len(times) == len(seats)
        for i, time in enumerate(times):
            if time != '-----':
                target_time = datetime.datetime.strptime(self.target_time, '%H:%M:%S')
                date_time = datetime.datetime.strptime(time, '%H:%M')
                time_dif = (date_time - target_time).seconds
                if re.findall(r'\d+|有', seats[i]) and (time_dif < 3600 or time_dif > 82800):
                    while len(trains[i]) < 5:
                        trains[i] = trains[i] + ' '
                    train_list.append('车次：' + trains[i] + '，发时：' + time)
        return train_list

    def orderTicket(self):
        sleep(3)
        self.driver.get("https://kyfw.12306.cn/otn/leftTicket/init")
        fromStation = self.driver.find_element_by_id('fromStationText')
        fromStation.click()
        fromStation.clear()
        fromStation.send_keys(self.fromStation + '\n')
        toStation = self.driver.find_element_by_id('toStationText')
        toStation.click()
        toStation.clear()
        toStation.send_keys(self.toStation + '\n')
        self.driver.execute_script("document.getElementById('train_date').removeAttribute('readonly')")
        trainDate = self.driver.find_element_by_id("train_date")
        trainDate.clear()
        trainDate.send_keys(self.train_date)
        self.driver.find_element_by_id("query_ticket").click()
        WebDriverWait(self.driver, 100).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'number')))
        trains = self.driver.find_elements_by_class_name("number")
        for i, item in enumerate(trains):
            name = item.text
            if name == self.train:
                tr_tag = self.driver.find_elements_by_xpath(f"//tr[contains(@id,'ticket')]")[i]
                tr_tag.find_elements_by_xpath(".//a[@class='btn72']")[0].click()
                break
        else:
            print('客服：该日没有指定的车次')
            return
        ul = WebDriverWait(self.driver, 100).until(
            EC.presence_of_element_located((By.ID, 'normal_passenger_id')))
        sleep(1)
        lis = ul.find_elements_by_tag_name('li')
        for i, item in enumerate(lis):
            print("客服：【{}】{}".format(i, item.find_elements_by_tag_name("label")[0].text))
        num = int(input('客服：请选择乘车人：'))
        ul.find_elements_by_tag_name('input')[num].click()
        code = self.seat_code[self.choice]
        seatSelect = self.driver.find_element_by_id("seatType_1")
        print('客服：正在为您查询余票')
        count = 1
        flag = False
        while True:
            print('客服：第{}次查询'.format(count))
            count += 1
            for i, item in enumerate(seatSelect.find_elements_by_tag_name("option")):
                if item.get_attribute("value") == code:
                    flag = True
                    item.click()
                    break
            if flag:
                break
            self.driver.back()
            sleep(1)
            self.driver.forward()
            ul = WebDriverWait(self.driver, 100).until(
                EC.presence_of_element_located((By.ID, 'normal_passenger_id')))
            sleep(1)
            ul.find_elements_by_tag_name('input')[num].click()
            seatSelect = self.driver.find_element_by_id("seatType_1")
        self.driver.find_element_by_id('submitOrder_id').click()
        WebDriverWait(self.driver, 100).until(
            EC.visibility_of_element_located((By.ID, 'qr_submit_id')))
        self.driver.find_element_by_id('qr_submit_id').click()

    def __call__(self, *args, **kwargs):
        print('请选择登陆方式：1、自动登陆 2、手动登陆')
        option = input('请选择:')
        if option == '1':
            self.login()
        else:
            self.manual_login()
        self.orderTicket()


if __name__ == '__main__':
    demo = Demo()
    demo()
