import sqlite3
from sqlite3 import Error

database = r"db\test.db"

def check_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def create_connection(db_file):
    # Create a database connection to a SQLite database
    connection = None
    try:
        connection = sqlite3.connect(db_file)
    except Error as e:
        print(e)
        connection.close()
    return connection

def execute_sql_command(connection, create_table_sql):
    try:
        c = connection.cursor()
        c.execute(create_table_sql)
        connection.commit()
    except Error as e:
        print(e)
        connection.close()


def create_sql_table(connection, name, website, currency, real_price, unreal_price, date, link):
    cursor = connection.cursor()

    sql_table_check = "SELECT Link FROM Main_Index WHERE Link = \"{}\"".format(link)
    cursor.execute(sql_table_check)
    if len(cursor.fetchall()) > 0:
        return

    # Get the amount of tables present to generate proper name for next table" (amount of tables + 1)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table_id = len(cursor.fetchall())
    table_name = "Link_" + str(table_id)

    # Create Table
    sql_create_table_command = "CREATE TABLE IF NOT EXISTS {} (ID INTEGER PRIMARY KEY," \
                               "Name TEXT," \
                               "Official_price REAL," \
                               "Unofficial_price REAL," \
                               "Date TEXT);".format(table_name)
    execute_sql_command(connection, sql_create_table_command)

    # Add the new table to the index table
    sql_add_to_index_command = """INSERT INTO "main"."Main_Index"("Name","Website","Currency","Official_price","Unofficial_price","Date","Link") """ \
                               """VALUES(?,?,?,?,?,?,?);"""
    cursor.execute(sql_add_to_index_command, (name, website, currency, real_price, unreal_price, date, link))
    connection.commit()
    price_update(connection, name, real_price, unreal_price, date, link)
    cursor.close()

def price_update(connection, name, real_price, unreal_price, date, link):
    cursor = connection.cursor()
    sql_update_index = """UPDATE "main"."Main_Index" SET Name = ?, Official_price = ?, Unofficial_price = ?, "Date" = ? WHERE Link = ?"""
    cursor.execute(sql_update_index, (name, real_price, unreal_price, date, link))
    sql_name_getter = """SELECT ID FROM Main_Index WHERE Link = ?"""
    cursor.execute(sql_name_getter, (link,))
    sql_id = cursor.fetchall()
    if(len(sql_id) <= 0):
        return

    table_name = "Link_" + str(sql_id[0][0])
    sql_insert_price = """INSERT INTO "main"."{}" ("Name","Official_price","Unofficial_price","Date") VALUES(?,?,?,?)""".format(table_name)
    cursor.execute(sql_insert_price, (name, real_price, unreal_price, date))
    connection.commit()
    cursor.close()

def del_record(connection, link):
    cursor = connection.cursor()
    sql_name_getter = """SELECT ID FROM Main_Index WHERE Link = ?"""
    cursor.execute(sql_name_getter, (link,))
    table_name = "Link_" + str(cursor.fetchall()[0][0])
    if(len(table_name) <= 0):
        return

    sql_insert_price = """DROP TABLE ?"""
    cursor.execute(sql_insert_price, (table_name,))
    connection.commit()
    cursor.close()

def get_links(connection):
    sql_links = "SELECT Link FROM Main_Index"
    cursor = connection.cursor()
    cursor.execute(sql_links)
    link_list = []
    result = cursor.fetchall()
    for i in range(len(result)):
        link_list.append(result[i][0])
    print(link_list)
    connection.commit()
    cursor.close()
    return link_list

def get_main_db(connection):
    sql_links = "SELECT * FROM Main_Index"
    cursor = connection.cursor()
    cursor.execute(sql_links)
    result = cursor.fetchall()
    connection.commit()
    cursor.close()
    return result

def get_price_change(connection):
    sql_links = "SELECT * FROM Main_Index"
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table_count = len(cursor.fetchall()) - 1
    output = []
    price_change = []
    percent_change = []
    secondary_price_change = []
    secondary_percent_change = []
    for i in range(table_count):
        table_name = "Link_" + str(i+1)
        sql_row_count = """SELECT COUNT(*) FROM {}""".format(table_name)
        cursor.execute(sql_row_count)
        last_row = cursor.fetchall()[0][0]
        sql_curr_price = """SELECT Official_price FROM {} WHERE ID = {}""".format(table_name, last_row)
        cursor.execute(sql_curr_price)
        get_cursor = cursor.fetchall()[0][0]
        curr_price = 0
        if(check_float(get_cursor)):
            curr_price = float(get_cursor)

        sql_secondary_curr_price = """SELECT Unofficial_price FROM {} WHERE ID = {}""".format(table_name, last_row)
        cursor.execute(sql_secondary_curr_price)
        get_cursor = cursor.fetchall()[0][0]
        secondary_price = 0
        if (check_float(get_cursor)):
            secondary_price = float(get_cursor)

        old_price = 0
        secondary_old_price = 0

        if(last_row > 1 and isinstance(curr_price, float)):
            sql_old_price = """SELECT Official_price FROM {} WHERE ID = {}""".format(table_name, last_row - 1)
            cursor.execute(sql_old_price)
            old_price = cursor.fetchall()[0][0]
            if(isinstance(old_price, float)):
                price_change.append(round(curr_price - old_price))
                percent_change.append(abs(round(((curr_price - old_price) / old_price) * 100)))
            else:
                price_change.append("ERR")
                percent_change.append("ERR")
        else:
            price_change.append(0)
            percent_change.append(0)

        if(last_row > 1 and isinstance(secondary_price, float)):
            sql_old_price = """SELECT Unofficial_price FROM {} WHERE ID = {}""".format(table_name, last_row - 1)
            cursor.execute(sql_old_price)
            secondary_old_price = cursor.fetchall()[0][0]
            if(isinstance(old_price, float)):
                secondary_price_change.append(round(secondary_price - secondary_old_price))
                secondary_percent_change.append(abs(round(((secondary_price - secondary_old_price) / secondary_old_price) * 100)))
            else:
                secondary_price_change.append("ERR")
                secondary_percent_change.append("ERR")
        else:
            secondary_price_change.append(0)
            secondary_percent_change.append(0)

    output.append(price_change)
    output.append(percent_change)
    output.append(secondary_price_change)
    output.append(secondary_percent_change)
    connection.commit()
    cursor.close()
    return output

#conn = create_connection(database)
#get_price_change(conn)
#create_sql_table(conn, "testName", "fakeLink", "currencyTes", "amazunyPrice", "NicePrice", "someday")
