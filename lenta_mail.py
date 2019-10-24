import requests
from lxml import html
from pprint import pprint
import re
import pandas as pd
import openpyxl

# ___________________________________________ MAIL.RU___________________________________________
def mail_news():
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'}
    main_link_mail = 'https://mail.ru'
    req = requests.get(main_link_mail, headers=header).text
    root = html.fromstring(req)

    # ------------------------------------------------------------------------------------------------
    # наименование источника
    source_mail = root.xpath('//a[@class="x-ph__link x-ph__link_first x-ph__link_selected"]/text()')

    # ------------------------------------------------------------------------------------------------
    # наименование новости
    # определяем название новости в главном блоке
    name_main = root.xpath('//h3[@class="news-item__title i-link-deco"]/text()')
    # определяем названия новостей в основном блоке
    name_tech = root.xpath('//div[@class="news-item__inner"]/a/text()')[:-6]

    # заменяем символы \xa0 на пробелы
    name_other = []
    for each in name_tech:
        name_other.append(each.replace(u'\xa0', u' '))

    # собираем все в один список
    name = name_main + name_other

    # ------------------------------------------------------------------------------------------------
    # ссылка на новость
    # определяем ссылку в главном блоке
    link_main = root.xpath('//div[@class="news-item o-media news-item_media news-item_main"]/a/@href')
    # определяем ссылки в основном блоке (кроме новостей по спец.рубрикам)
    link_tech = root.xpath('//div[@class="news-item__inner"]/a/@href')[:-6]
    # собираем все в один список
    link = link_main + link_tech

    # ------------------------------------------------------------------------------------------------
    # дата публикации

    # определяем дату в главном блоке
    req_d_m = requests.get(link_main[0], headers=header).text
    root_d_m = html.fromstring(req_d_m)
    date_main = root_d_m.xpath('//span[@class="note"]/span[@class="note__text breadcrumbs__text js-ago"]/@datetime')

    # определяем даты в основном блоке (кроме новостей по спец.рубрикам)
    date_other = []

    for each_link in link_tech:
        req_d_t = requests.get(each_link, headers=header).text
        root_d_t = html.fromstring(req_d_t)
        date_each_link = root_d_t.xpath(
            '//span[@class="note"]/span[@class="note__text breadcrumbs__text js-ago"]/@datetime')
        date_other.append(date_each_link[0])

    # собираем все в один список
    date = date_main + date_other

    mail_dict = {'Название источника': source_mail*len(link), 'Наименование новости': name, 'Ссылка на новость': link,
                 'Дата публикации': date}

    return mail_dict

# ___________________________________________ LENTA.RU___________________________________________

def lenta_news():
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'}
    main_link_lenta = 'https://lenta.ru'
    req = requests.get(main_link_lenta, headers=header).text
    root = html.fromstring(req)

    # ------------------------------------------------------------------------------------------------
    # наименование источника
    source_tech = root.xpath('//div[@class="b-footer__copyrights"]/text()')[0]
    x = re.findall(r'\D+[а-я]', source_tech)
    source_lenta = x[0].replace(' ', '')

    # ------------------------------------------------------------------------------------------------
    # наименование новости
    # определяем название новости в главном блоке
    name_main = root.xpath('//div[@class="span4"]/div[@class="first-item"]/*/*/text()')

    # определяем названия новостей в основном блоке
    name_tech = root.xpath('//div[@class="span4"]/div[@class="item"]/*/text()')
    # заменяем символы \xa0 на пробелы
    tech = name_main + name_tech

    name = []
    for each in tech:
        name.append(each.replace(u'\xa0', u' '))


    # ------------------------------------------------------------------------------------------------
    # ссылка на новость
    # определяем ссылку в главном блоке
    link_main = root.xpath('//div[@class="span4"]//a[@class="topic-title-pic__link js-dh"]/@href')
    # определяем ссылки в основном блоке (кроме новостей по спец.рубрикам)
    link_tech = root.xpath('//div[@class="span4"]/div[@class="item"]/a/@href')
    # собираем все в один список
    link_tech = link_main + link_tech
    link = []
    for each_link in link_tech:
        link.append(main_link_lenta+each_link)



    # ------------------------------------------------------------------------------------------------
    # дата публикации
    #время
    date_main = root.xpath('//div[@class="span4"]//div[@class="first-item"]//time[@class="g-time"]/@datetime')

    # определяем даты в основном блоке (кроме новостей по спец.рубрикам)
    date_other = root.xpath('//div[@class="span4"]//div[@class="item"]//time[@class="g-time"]/@datetime')

    # собираем все в один список
    date = date_main + date_other

    lenta_dict = {'Название источника': source_lenta, 'Наименование новости': name, 'Ссылка на новость': link,
                  'Дата публикации': date}
   # *len(link)
    return lenta_dict


# формируем датафреймы
mail = mail_news()
df_mail = pd.DataFrame(mail)
lenta = lenta_news()
df_lenta = pd.DataFrame(lenta)

# объединяем датафреймы в один
news = pd.concat((df_mail, df_lenta))

# и складываем всё в один файл
news.to_excel('news.xlsx')