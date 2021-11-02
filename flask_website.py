from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)
database = r"db\test.db"

@app.route("/")
def index():
    headings = ["Name", "Website", "Currency", "Price", "Secondary Price", "Last Check", "Link", "Delete"]
    import db_module
    conn = db_module.create_connection(database)
    response = db_module.get_main_db(conn)
    price_changes = db_module.get_price_change(conn)
    return render_template("index.html", headings=headings, data=response, price_change=price_changes[0], price_percentage_change=price_changes[1], secondary_price_change=price_changes[2], secondary_price_percentage_change=price_changes[3])

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
        return redirect(url_for('link_page', link_id=link_id))
    elif(request.form.get('update-btn') != None):
        import scraper
        scraper.update_db()
        return redirect(url_for('index'))

@app.route("/new-link")
def new_link():
    link = request.args['link']
    headings = ["Name", "Website", "Currency", "Price", "Secondary Price", "Date", "Link"]
    global data
    import scraper
    data = scraper.parse_link(link)
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

if __name__ == "__main__":
    app.run(host='0.0.0.0')