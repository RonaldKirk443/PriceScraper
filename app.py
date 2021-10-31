import requests
import re
from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)
database = r"db\test.db"

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

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


@app.route("/")
def index():
    headings = ["Name", "Website", "Currency", "Price", "Secondary Price", "Last Check", "Link", "Delete"]
    import db_module
    conn = db_module.create_connection(database)
    response = db_module.get_main_db(conn)
    price_changes = db_module.get_price_change(conn)
    print(price_changes)
    price_diff = price_changes[0]
    price_percentage_diff = price_changes[1]
    secondary_price_diff = price_changes[2]
    secondary_price_percentage_diff = price_changes[3]
    return render_template("index.html", headings=headings, data=response, price_change=price_diff, price_percentage_change=price_percentage_diff, secondary_price_change=secondary_price_diff, secondary_price_percentage_change=secondary_price_percentage_diff)

@app.route("/", methods=['POST'])
def index_post():
    if(request.form.get('link-input-btn') != None):
        link = request.form['link-input']
        return redirect(url_for('new_link', link=link))
    elif ('entry-delete-btn' in str(request.form.keys())):
        entryNum = str(request.form.keys())[29:-3]
        import db_module
        conn = db_module.create_connection(database)
        db_module.del_record_by_id(conn, entryNum)
        return redirect(url_for('index'))
    elif ('entry-link' in str(request.form.keys())):
        link_id = str(request.form.keys())[23:-3]
        print(link_id)
        return redirect(url_for('link_page', link_id=link_id))
    elif(request.form.get('update-btn') != None):
        update_db()
        return redirect(url_for('index'))

@app.route("/new-link")
def new_link():
    link = request.args['link']
    headings = ["Name", "Website", "Currency", "Price", "Secondary Price", "Date", "Link"]
    global data
    data = parse_link(link)
    return render_template("newItem.html", headings=headings, data=data)

@app.route("/new-link", methods=['POST'])
def new_link_post():
    if(request.form.get('yes_button') != None):
        import db_module
        conn = db_module.create_connection(database)
        response = db_module.create_sql_table(conn, data[0], data[1], data[2], data[3], data[4], data[5], data[6])
    return redirect(url_for('index'))

@app.route("/link")
def link_page():
    link_id = request.args['link_id']
    headings = ["Name", "Price", "Secondary Price", "Date"]
    import db_module
    conn = db_module.create_connection(database)
    response = db_module.get_link_db(conn, link_id)
    labels = []
    price = []
    secondary_price = []
    for row in response:
        labels.append(row[4])
        price.append(row[2])
        secondary_price.append(row[3])

    return render_template("entry.html", headings=headings, data=response, x_axis=labels, price=price, secondary_price=secondary_price)

@app.route("/link", methods=['POST'])
def link_page_post():
    if (request.form.get('main-menu-btn') != None):
        return redirect(url_for('index'))

