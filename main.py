import time
import pickle

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup as bs


class Methods:
    # возвращает html страницы
    @staticmethod
    def get_selenium(link):
        options = webdriver.ChromeOptions()
        # отключаем изображения
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)

        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        # безголовый режим
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(15)
        driver.get(link)
        return driver


class Parsers(Methods):

    def __init__(self):
        super().__init__()

    def list_of_events(self):
        link_start = 'https://photo.thai.run/'
        driver = self.get_selenium(link_start)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            html = driver.page_source

            # если находим самый первый турнир, то прерываем цикл
            if '2558' in html:
                break

            # Нажимаем кнопку More Races
            print('Нажимаем на кнопку, ждем несколько секунд')
            driver.find_element_by_xpath("//button[contains(@class, 'ant-btn styles__OrangeAltButton')]").click()
            time.sleep(4)

        # список турниров
        list_events = []
        list_events_driver = driver.find_elements_by_xpath("//div[contains(@class, 'ant-col styles__EventCard-sc')]")
        for event in list_events_driver:
            html_event = event.get_attribute('innerHTML')
            bs_obj = bs(html_event, 'lxml')
            link = bs_obj.find('a').get('href')
            name = bs_obj.find('div', {'class': 'card-label'}).get_text()
            list_events.append({
                'name': name,
                'link': link_start + link,
            })

        with open('events.pickle', 'wb') as file:
            pickle.dump(list_events, file)

        driver.close()

    def parse_photo_event(self, link):
        driver = self.get_selenium(link)
        # Название турнира
        title = driver.find_element_by_xpath("//div[@class='title']").text
        # список с ссылками на фото
        list_photo = []
        while True:
            try:
                list_photo_driver = driver.find_element_by_xpath("//div[@class='react-photo-gallery--gallery']")
                html = list_photo_driver.get_attribute('innerHTML')
                bs_obj = bs(html, 'lxml')
                for photo in bs_obj.find_all('img'):
                    link_photo = photo.get('src')
                    list_photo.append({
                        'title': title,
                        'link_photo': link_photo,
                    })
            # если нет фотографий закрываем драйвер
            except NoSuchElementException:
                driver.close()
                break

            # проходим на следующую страницу
            try:
                driver.find_element_by_xpath("//li[@class=' ant-pagination-next']").click()
            # если страниц больше нет, закрываем driver
            except NoSuchElementException:
                print('Страницы кончились')
                driver.close()
                break

        # сохраняем в файл, если есть фотографии
        if len(list_photo) > 1:
            name_file = title.replace(' ', '').lower()
            with open(name_file[:10], 'wb') as file:
                pickle.dump(list_photo, file)


if __name__ == "__main__":
    obj = Parsers()
    # собираем турниры
    obj.list_of_events()
    # открываем список турниров
    with open('events.pickle', 'rb') as file:
        events = pickle.load(file)
    # проходим по списку турниров
    for event in events[:4]:
        obj.parse_photo_event(event.get('link'))
