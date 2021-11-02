import requests
import re
from datetime import datetime

database = r"db\test.db"

def download_page(url, i):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
               "Accept-Encoding": "gzip, deflate",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT": "1",
               "Connection": "close", "Upgrade-Insecure-Requests": "1"}
    file = open("HtmlTests/" + i + ".txt", "w", encoding="utf-8")
    file.write(requests.get(url, headers=headers).text)
    file.close()


def get_page(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
               "Accept-Encoding": "gzip, deflate, br",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT": "1",
               "Connection": "close", "Upgrade-Insecure-Requests": "1"}
    return requests.get(url, headers=headers).text


def get_amazon_ca_data(link, website, date, currency):
    amazonPriceRegex = "data-a-color=\"price\"><span class=\"a-offscreen\">\$(.*?)<"
    amazonLowestPriceRegex = "</span><span class=\"a-size-base a-color-price\">\$(.*?)<"
    # amazonLowestPriceRegex = "id=\"price_inside_buybox\" class=\"a-size-medium a-color-price\">(.*?)<"
    amazonPriceRegexCut = "[0-9](.*?)<"
    amazonTitleRegex1 = "<title>(.*?): Amazon"
    html = get_page(link)

    file = open("HtmlTests/1.txt", "w", encoding="utf-8")
    file.write(html)
    file.close()

    try:
        title = re.search(amazonTitleRegex1, html).group()[7:]
    except:
        title = "Err"
    try:
        price = re.search(amazonPriceRegexCut, re.search(amazonPriceRegex, html).group()).group()[:-1]
    except:
        price = "Err"
    try:
        lowestPrice = re.search(amazonPriceRegexCut, re.search(amazonLowestPriceRegex, html).group()).group()[:-1]
    except:
        lowestPrice = "Err"
    return [title, website, currency, price, lowestPrice, date, link]


def parse_link(link):
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M")

    websiteRegex = "www.(.*?)\/"
    website = re.search(websiteRegex, link).group()[4:-1]
    currency = "NULL"
    if(website.find('ca') != -1):
        currency = "CAD"
    elif (website.find('com') != -1):
        currency = "USD"

    if(website.find('amazon') != -1):
        data = get_amazon_ca_data(link, "Amazon", dt_string, currency)
        return data
    return None


    # file = open(str(i) + ".txt", "w", encoding="utf-8")
    # file.write(data[3])
    # file.close()

def update_db():
    import db_module
    conn = db_module.create_connection(database)
    response = db_module.get_links(conn)
    for link in response:
        data = parse_link(link)
        # title, website, currency, price, lowestPrice, date, link
        db_module.price_update(conn, data[0], data[3], data[4], data[5], data[6])
