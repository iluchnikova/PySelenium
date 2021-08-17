'''
Представим, что Вы готовите слайд для презентации об актуальных трендах в англоязычных новостях, касающихся России.

С сайта google news (https://news.google.com) (язык и регион - English | United States) необходимо
прокачать все статьи за последний месяц (на момент прокачки) с ключевым словом Russia.
Затем для скачанных статей необходимо рассчитать топ-50 упоминаемых тем и представить их в виде word (tag) cloud.

Данное задание необходимо выполнить с помощью Python.
Для представления в виде word cloud можно использовать уже существующие библиотеки.
Пример word cloud можно посмотреть по ссылке -
https://altoona.psu.edu/sites/altoona/files/success-word-cloud.jpg
'''

# Для корректной работы необходимо предварительно:
# 1) установить selenium через командную строку: python -m pip install -U selenium
# 2) установить wordcloud через командную строку: python -m pip install -U wordcloud
# 3) скачать и распаковать драйвер для выбранного браузера с учетом его версии (в данном случае chromedriver), добавить его директорию в PATH

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime, timedelta
from threading import Thread
import wordcloud
from scipy.misc import imread
import math
import re
import sys

class Driver:
    def __init__(self):
        self.driver = webdriver.Chrome()

    def go_to_page(self, page: str):
        self.driver.get(page)

    def get_element(self, css_element: str):
        return self.driver.find_element_by_css_selector(css_element)

    def get_elements(self, css_element: str):
        return self.driver.find_elements_by_css_selector(css_element)

    def click_on_element(self, element):
        element.click()

    def insert_into_element(self, element, text: str):
        element.send_keys(text)

    def get_value(self, element, attribute: str):
        return element.get_attribute(attribute)

    def text_from_element(self, element):
        return element.text

    def text_from_elements(self, element_list):
        l = []
        for i in element_list:
            l.append(i.text)
        return l

    def wating(self, seconds: int):
        WebDriverWait(self.driver, seconds)

    def get_page_URL(self) -> str:
        return self.driver.current_url

    def forward(self):
        self.driver.forward()

    def back(self):
        self.driver.back()

    def close(self):
        self.driver.quit()

def convert_to_datetime(d: str):
    return datetime.strptime(' '.join(d[:-1].split('T')), '%Y-%m-%d %H:%M:%S')

def get_text_from_article(text_list: list, url_list):
    d = Driver()
    for u in url_list:
        d.go_to_page(u)
        text_list.extend(d.text_from_elements(d.get_elements('p')))
    return text_list

if __name__ == "__main__":

    is_getting_words = False
    searching_word = 'Russia'
    requared_period = 30
    url = "https://news.google.com/topstories?hl=en-US&gl=US&ceid=US:en"
    year_news = None
    all_p = []
    all_words = []
    urls = []

    while (is_getting_words == False):
        try:
            driver = Driver()
            driver.go_to_page(url)

            # Searching:
            driver.insert_into_element(driver.get_elements('input.Ax4B8.ZAGvjd'), searching_word + ' when:1y')
            driver.click_on_element(driver.get_element('button.gb_nf'))

            #Waiting loading all news with searching_word in title
            is_include_searching_word = False
            while(is_include_searching_word == False):
                titles = driver.text_from_elements(driver.get_elements('a.DY5T1d.RZIKme'))
                titles = [x for x in titles if x!='']
                if len(titles) != len(list(filter(lambda x: x.find(searching_word)!=-1, titles))):
                    driver.wating(1)
                else:
                    year_news = driver.get_elements('article.MQsxIb.xTewfe.R7GTQ.keNKEd.j7vNaf.Cc0Z5d.EjqUne')
                    is_include_searching_word = True

            month_news = [x for x in year_news if
                          convert_to_datetime(driver.get_value(driver.get_element('time.WW6dff.uQIVzc.Sksgp'), 'datetime')) >= (
                                      datetime.now() - timedelta(days=requared_period))]

            for m in month_news:
                urls.append(m.find_element_by_css_selector('a.VDXfz').get_attribute('href'))

            #Threads:
            threads_count = math.floor(len(urls)/math.log(len(urls), 2))
            start_index = 0
            end_index = -1
            for c in range(threads_count):
                name = c
                start_index += end_index + 1
                end_index += math.floor(len(urls) / threads_count)
                if c == threads_count - 1:
                    end_index = threads_count
                t = Thread(target=get_text_from_article, args=(all_p, url[start_index:end_index]))
                t.start()
                t.join()

            is_getting_words = True
        except TypeError as err:
            print('TypeError: {0}'.format(err))
        except AttributeError as err:
            print('AttributeError: {0}'.format(err))
        except:
            print('Unexpected error: ', sys.exc_info()[0])
        finally:
            driver.close()

    for p in all_p:
        p = re.sub(r'[^\w\s]', '', p)  # delete punctuation marks
        all_words.extend(p.split(' '))

    all_words_dict = {key: all_words.count(key) for key in set(all_words)}
    most_populas_words = sorted(all_words_dict, key=all_words_dict.get)  # sorted ascending list of keys
    most_populas_words = most_populas_words[:50:-1]

    mask = imread('russiamap.jpg')
    picture = wordcloud.Wordcloud(mask=mask)
    picture.generate(' '.join(most_populas_words))
    picture.to_file('wordcloud.png')