import requests
import re
import datetime

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
file = open("links.txt")
links = file.read()
links = links.split()
file.close()


def download_page(url, i):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
               "Accept-Encoding": "gzip, deflate",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT": "1",
               "Connection": "close", "Upgrade-Insecure-Requests": "1"}
    file = open(i + ".txt", "w", encoding="utf-8")
    file.write(requests.get(url, headers=headers).text)
    file.close()


def get_page(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
               "Accept-Encoding": "gzip, deflate",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT": "1",
               "Connection": "close", "Upgrade-Insecure-Requests": "1"}
    return requests.get(url, headers=headers).text


def get_amazon_ca_data(link):
    amazonPriceRegex = "class=\"a-size-medium a-color-price priceBlockBuyingPriceString\">\$(.*?)<"
    amazonLowestPriceRegex = "class=\"a-size-base a-color-base\">\$(.*?)<"
    # amazonLowestPriceRegex = "id=\"price_inside_buybox\" class=\"a-size-medium a-color-price\">(.*?)<"
    amazonPriceRegexCut = "[0-9](.*?)<"
    amazonTitleRegex1 = "<title>(.*?): Amazon"
    html = get_page(link)
    try:
        title = re.search(amazonTitleRegex1, html).group()[7:]
    except:
        title = "Error retrieving title"
    try:
        price = re.search(amazonPriceRegexCut, re.search(amazonPriceRegex, html).group()).group()[:-1]
    except:
        price = "Error retrieving price"
    try:
        lowestPrice = re.search(amazonPriceRegexCut, re.search(amazonLowestPriceRegex, html).group()).group()[:-1]
    except:
        lowestPrice = "Error retrieving lowest price"
    return [title, price, lowestPrice, html]


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    for link in links:
        data = get_amazon_ca_data(link)
        # file = open(str(i) + ".txt", "w", encoding="utf-8")
        # file.write(data[3])
        # file.close()
        print("Title: " + data[0] + "\n" + "Amazon Official Price: " + data[1] + "\n" + "Non-amazon seller Price: " +
              data[2] + "\n")