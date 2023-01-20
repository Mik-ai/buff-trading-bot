import time

import pickle

from multiprocessing import Queue, Pipe, connection
from random import randint

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import re
import json

from webdriver_manager.chrome import ChromeDriverManager
from tenacity import retry, stop_after_attempt


class SkinScraper:
    driver: webdriver.Chrome
    running = False
    message_queue: Queue
    # scrape_flag_pipe: Pipe\
    running_flag_q: Queue

    def __init__(self, message_q, flag_queue):
        service = Service(executable_path=ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.message_queue = message_q
        self.running_flag_q = flag_queue
        # self.scrape_flag_pipe = scraping_flag
        self.authentication()

    def authentication(self):
        self.driver.get('https://buff.163.com/')
        cookies = pickle.load(open("cookies.pkl", "rb"))
        for cookie in cookies:
            self.driver.add_cookie(cookie)
        time.sleep(1)
        self.driver.get('https://buff.163.com/')

    def load_page(self, url):
        if url is not None:
            self.driver.get(url)
            time.sleep(2)

    def scrape_skins_pages(self):

        with open('json_skins.json', 'r') as skins_json:
            skins = json.load(skins_json)

        for skin in skins:
            # break parsing by flag
            if self.running_flag_q.empty():
                break

            # getting skin page
            self.load_page(skin['url'])

            # getting skin_list
            skin_table = self.driver.find_elements(By.CLASS_NAME, "selling")

            # check_skins
            self.check_skins(skin_table, skin)

            # antibot
            time.sleep(randint(2, 5))

    def check_skins(self, skin_table, skin):
        for skin_html in skin_table[1:]:
            # scraping text data
            skin_float_text = skin_html.find_element(By.CLASS_NAME, "wear-value").text
            skin_prise = skin_html.find_element(By.CLASS_NAME, "f_Strong").text
            skin_prise_ru_text = skin_html.find_element(By.CLASS_NAME, "hide-cny").text

            # converting text to numeric
            skin_float_numeric = float(re.sub('[^0-9.]', '', skin_float_text))
            prise_ru_numeric = float(re.sub('[^0-9.]', '', skin_prise_ru_text))

            # checking for condition
            if skin['float']['float_down'] < skin_float_numeric < skin['float']['float_up'] \
                    and prise_ru_numeric < skin['price_up']:
                if skin['buy'] is True:
                    self.buy_skin(skin_html, skin)
                else:
                    self.message_queue.put(
                        f"name={skin['name']} float={skin_float_numeric} price={prise_ru_numeric} url={skin['url']}")

    def buy_skin(self, skin_html, skin):

        skin_float_text = skin_html.find_element(By.CLASS_NAME, "wear-value").text
        skin_prise_ru_text = skin_html.find_element(By.CLASS_NAME, "hide-cny").text

        try:
            # buy skin
            button_btn_buy_order = skin_html.find_element(By.CLASS_NAME, "btn-buy-order")
            webdriver.ActionChains(self.driver).move_to_element(button_btn_buy_order).click(
                button_btn_buy_order).perform()
            # button_btn_buy_order.click()

            # how long it will wait until window is opened
            for i in range(10):
                try:
                    # check if buy offer window opened
                    if self.driver.find_element(By.ID, "j_popup_epay").is_displayed():
                        button_pay_btn = self.driver.find_element(By.CLASS_NAME, "pay-btn")
                        webdriver.ActionChains(self.driver).move_to_element(button_pay_btn).click(
                            button_pay_btn).perform()
                        # button_pay_btn.click()

                        for i in range(10):
                            try:
                                # check window "where to send" buff offer
                                if self.driver.find_element(By.ID, "j_popup_payed").is_displayed():
                                    button_j_popup_payed_close = self.driver.find_element(By.ID,
                                                                                          "j_popup_payed").find_element(
                                        By.CLASS_NAME, 'popup-close')
                                    webdriver.ActionChains(self.driver).move_to_element(
                                        button_j_popup_payed_close).click(
                                        button_j_popup_payed_close).perform()
                                    # button_j_popup_payed_close.click()
                                    # bought message send
                                    self.message_queue.put(
                                        f"bought skin ={skin['name']}, price ={skin_float_text}, float ={skin_prise_ru_text}")
                                    break
                                elif self.driver.find_element(By.CLASS_NAME, 'w-Toast_warning').is_displayed():
                                    print(
                                        f"can't buy skin ={skin['name']}, price ={skin_float_text}, float ={skin_prise_ru_text}")
                                    break
                            except:
                                print("window j_popup_payed is not appeared")

                            time.sleep(0.4)
                        break

                    elif self.driver.find_element(By.ID, 'j_w-Toast').is_displayed():
                        print(f"can't buy skin ={skin['name']}, price ={skin_float_text}, float ={skin_prise_ru_text}")
                        break
                except:
                    print("window j_popup_epay is not appeared")
                time.sleep(0.4)
        except:
            self.message_queue.put(f"can't buy skin ={skin['name']}")

    def start_scraping(self):
        while True:
            if not self.running_flag_q.empty():
                print("starting scraper")
                self.scrape_skins_pages()
            time.sleep(randint(1, 3) * 30)


if __name__ == '__main__':
    message_q = Queue()
    run_f = Queue()
    run_f.put(True)
    scrapper = SkinScraper(message_q, run_f)
    scrapper.start_scraping()
    print("initialized")
    time.sleep(60)
