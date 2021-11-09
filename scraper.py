import requests
import re
from datetime import datetime

from celery import Celery
celery = Celery(broker='redis://localhost:6379/0')

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


def get_amazon_data(link, website, date, currency):
    priceRegex = "data-a-color=\"price\"><span class=\"a-offscreen\">\$(.*?)<"
    lowestPriceRegex = "</span><span class=\"a-size-base a-color-price\">\$(.*?)<"
    # amazonLowestPriceRegex = "id=\"price_inside_buybox\" class=\"a-size-medium a-color-price\">(.*?)<"
    amazonPriceRegexCut = "[0-9](.*?)<"
    amazonTitleRegex = "<title>(.*?): Amazon"
    html = get_page(link)

    try:
        title = re.search(amazonTitleRegex, html).group()[7:-8]
    except:
        title = "Err"
    try:
        price = re.search(amazonPriceRegexCut, re.search(priceRegex, html).group()).group()[:-1]
    except:
        price = "Err"
    try:
        lowestPrice = re.search(amazonPriceRegexCut, re.search(lowestPriceRegex, html).group()).group()[:-1]
    except:
        lowestPrice = "Err"
    return [title, website, currency, price, lowestPrice, date, link]

def get_newegg_data(link, website, date):
    priceRegex = "\"price\":\"(.*?)\""
    lowestPriceRegex = "\"LowestOrderPrice\":\"(.*?)\""
    currencyRegex = "\"priceCurrency\":\"(.*?)\""
    priceRegexCut = "[0-9](.*?)\""
    amazonTitleRegex = "<title>(.*?) - Newegg"

    html = get_page(link)

    try:
        title = re.search(amazonTitleRegex, html).group()[7:-9]
    except:
        title = "Err"
    try:
        currency = re.search(currencyRegex, html).group()[17:-1]
    except:
        currency = "Err"
    try:
        price = re.search(priceRegexCut, re.search(priceRegex, html).group()).group()[:-1]
    except:
        price = "Err"
    try:
        lowestPrice = re.search(priceRegexCut, re.search(lowestPriceRegex, html).group()).group()[:-1]
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
        data = get_amazon_data(link, "Amazon", dt_string, currency)
        return data
    elif(website.find('newegg') != -1):
        data = get_newegg_data(link, "Newegg", dt_string)
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
    print("Finished")

if __name__ == "__main__":
    link = "https://www.newegg.ca/intel-core-i5-11600k-core-i5-11th-gen/p/N82E16819118235?Description=core%20i5-11600k&cm_re=core_i5-11600k-_-19-118-235-_-Product"
    print(parse_link(link))