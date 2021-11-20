from flask import Flask, request, render_template, redirect, url_for, jsonify, session
import threading

app = Flask(__name__)
app.secret_key = 'SECRET_KEY'
database = r"db\test.db"

@app.route("/")
def index():
    try:
        sorting_index = session['sorting_data'][0]
        sorting_way = session['sorting_data'][1]
    except:
        sorting_index = 0
        sorting_way = "asc"
    headings = ["Name", "Website", "Currency", "Price", "Secondary Price", "Last Check", "Link", "Delete"]
    import db_module
    conn = db_module.create_connection(database)
    response = db_module.get_main_db(conn)
    price_changes = db_module.get_price_change(conn)
    return render_template("index.html", headings=headings, data=response, price_change=price_changes[0], price_percentage_change=price_changes[1], secondary_price_change=price_changes[2], secondary_price_percentage_change=price_changes[3], sorting_index=sorting_index, sorting_way=sorting_way)

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
    elif ('entry-name-edit-btn' in str(request.form.keys())):
        print(str(request.form.keys()))
        entryNum = str(request.form.keys())[32:-3]
        return redirect(url_for('edit_entry_name', entry_id=entryNum))
    elif ('entry-link' in str(request.form.keys())):
        link_id = str(request.form.keys())[23:-3]
        return redirect(url_for('link_page', link_id=link_id))
    elif(request.form.get('update-btn') != None):
        return redirect(url_for('index'))
    return redirect(url_for('index'))

@app.route("/update-db", methods=['POST'])
def update_db():
    import scraper
    #threading.Thread(target=scraper.update_db).start()
    scraper.update_db()
    return jsonify(status="success")

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
    import db_module
    conn = db_module.create_connection(database)
    response = db_module.get_link_db(conn, link_id)
    name = db_module.get_entry_name(conn, link_id)
    link = db_module.get_entry_link(conn, link_id)
    labels = []
    price = []
    secondary_price = []
    for row in response:
        labels.append(row[4])
        price.append(row[2])
        secondary_price.append(row[3])
    print(response)
    return render_template("entry.html", name=name, link=link, data=response, x_axis=labels, price=price, secondary_price=secondary_price)

@app.route("/link", methods=['POST'])
def link_page_post():
    if (request.form.get('main-menu-btn') != None):
        return redirect(url_for('index'))

@app.route("/entry-name-editor")
def edit_entry_name():
    entry_id = str(request.args['entry_id'])
    import db_module
    conn = db_module.create_connection(database)
    response = db_module.get_entry_name(conn, entry_id)

    return render_template("editName.html", name=response)

@app.route("/entry-name-editor", methods=['POST'])
def edit_entry_name_post():
    new_name = request.form['new-name-input']
    if (request.form.get('change-name-btn') != None):
        import db_module
        conn = db_module.create_connection(database)
        entry_id = str(request.args['entry_id'])
        old_name = db_module.get_entry_name(conn, entry_id)
        if (new_name != "" and new_name != None and new_name != old_name):
            import db_module
            conn = db_module.create_connection(database)
            db_module.change_entry_name(conn, entry_id, new_name)
        else:
            print("doing nothing")
    return redirect(url_for('index'))

@app.route("/save-sorting-preference", methods=['POST'])
def save_sorting_preference():
    sorting_data = request.get_json()[0]
    session['sorting_data'] = sorting_data
    return jsonify(status="success")

@app.route("/test")
def test():
    link_id = request.args['link_id']
    import db_module
    conn = db_module.create_connection(database)
    name = db_module.get_entry_name(conn, link_id)
    link = db_module.get_entry_link(conn, link_id)
    return render_template("test.html", name=name, link=link,)

if __name__ == "__main__":
    app.run()