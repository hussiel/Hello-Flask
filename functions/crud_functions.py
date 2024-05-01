'''

This module contains all CRUD functions called from app.py as well as additional helper functions for abstraction.
These functions are designed to help you manipulate the data within the MySQL database as well as format data types.

Additionally, there is also a function which takes in an SQL string query as a parameter (which you can edit through here)
and returns data. 

'''
#This will allow a flash message to be displayed in case of a duplicate ID when attempting to a add new row to the database.
from flask import redirect, url_for, flash

#This will import SQL_Connection module in order to connect with MySQL database.
from functions.SQL_Connection import * 

#This will be used to change the date format from yyyy-mm-dd to dd/mm/yyyy to ensure consistency within the database.
from datetime import datetime

#This function will obtain a list of all entries/rows within the MySQL database.
def all_entries():

    #This is a variable representing database connection.
    sql_cxn = dbConnection()

    #Cursor used to execute statements to communicate with the MySQL database.
    cur = sql_cxn.cursor(dictionary = True) # 'dictionary=True' will return each entry as a dictionary

    #This is a SQL query to return all entries from the datatable sorted by 'id'
    sql_query = 'SELECT * FROM sales ORDER BY id'

    #This executes given query.
    cur.execute(sql_query)

    #This represents all entries in the database.
    all_entries = cur.fetchall()

    #Closes the cursor, resets all results, and ensures that the cursor object has no reference to its original connection object.
    cur.close()

    #Closes connection to MySQL database.
    sql_cxn.close()
    return all_entries

#This function will return a set of entries based on input date parameters. It assumes the input date parameters are valid 
#(ie. No absurd years like 03/01/2023333). Will also check that start_date <= end_date.
def entries_by_date(start_date, end_date):

    #Comments for functionality included already within 'def all_entries()'.
    sql_cxn = dbConnection()
    cur = sql_cxn.cursor(dictionary=True)

    #SQL query to retrieve data between start_date and end_date
    #Query is written specifically so that dates from the database are formatted appropiately from MM/DD/YYYY to YYYY-MM-DD.
    query = "SELECT * FROM sales WHERE STR_TO_DATE(transaction_date, '%m/%d/%Y') BETWEEN %s AND %s ORDER BY STR_TO_DATE(transaction_date, '%m/%d/%Y') ASC"
    cur.execute(query, (start_date, end_date))
    filtered_entries = cur.fetchall()

    #Close the cursor and connection
    cur.close()
    sql_cxn.close()

    #Return the filtered_entries list containing entries between start_date and end_date
    return filtered_entries

#This function will allow you to add an entry to the database.
def add_entry(id = '', store_code = '', total_sale = '', transaction_date = ''):

    #Comments for functionality included already within 'def all_entries()'.
    sql_cxn = dbConnection()
    cur = sql_cxn.cursor(dictionary = True)

    #This next part will check that the given 'id' isn't already contained within the database to avoid duplication of primary keys.
    #If it is, you will be given a flash message and redirected to the 'home' page.

    #This will create a single row/column containing a number representing the number of occurrences of 'id'. The column is labeled
    #'occurrences'
    dupeCheckQuery = "SELECT COUNT(*) AS occurrences FROM sales WHERE id = %s" 
    cur.execute(dupeCheckQuery, (id,))

    #This will retrieve that number. Since it is just one row, fetchone() is used instead of fetchall().
    singleRow = cur.fetchone()
    #If that number is greater than 0, you won't be able to add the entry to the database to avoid duplication.
    if singleRow['occurrences'] > 0: 
        cur.close()
        sql_cxn.close()
        flash("That ID is already contained within the database!")
        return redirect(url_for('home'))

    #Formatting our 'transaction_date'
    transaction_date = format_transaction_date(transaction_date)

    #Formatting 'total_sale'.
    total_sale = format_total_sale(total_sale)

    #SQL query for inserting data into database.
    sql_query = ("INSERT INTO sales (id, store_code, total_sale, transaction_date) VALUES (%s, %s, %s, %s)")
    values = (id, store_code, total_sale, transaction_date)
    cur.execute(sql_query, values)

    #Commit changes to data base and close.
    sql_cxn.commit()
    cur.close()
    sql_cxn.close()

    #This represents number of rows affected (0 or 1).
    add_result = cur.rowcount

    #Will return 1 if addition was successful.
    return add_result

#This function will allow you to edit an entry within the database.
def edit_entry(id = '', store_code = '', total_sale = '', transaction_date = ''):
    sql_cxn = dbConnection()
    cur = sql_cxn.cursor(dictionary = True)

    # Formatting our 'transaction_date'
    transaction_date = format_transaction_date(transaction_date)

    #Formatting our 'total_sale'
    total_sale = format_total_sale(total_sale)

    #SQL query for editing and updating data wihtin the database.
    sql_query = ("UPDATE sales SET store_code = %s, total_sale = %s, transaction_date = %s WHERE id = %s")
    values = (store_code, total_sale, transaction_date, id)
    cur.execute(sql_query, values)

    #Commit changes to data base and close.
    sql_cxn.commit()
    cur.close()
    sql_cxn.close()

    #This represents the number of rows that were modified. 
    edit_result = cur.rowcount 
    return edit_result

#This function will allow you to delete an entry from the database.
def delete_entry(id = ''):
    sql_cxn = dbConnection()
    cur = sql_cxn.cursor(dictionary = True)

    #SQL query for deleting data wihtin the database.
    sql_query = ("DELETE FROM sales WHERE id = %s")

    #Since 'id' is a single value wrapped in parentheses, we include a comma so that it can be interpreted as a tuple.
    values = (id,)
    cur.execute(sql_query, values)

    #Commit changes to data base and close.
    sql_cxn.commit()
    cur.close()
    sql_cxn.close()

    #This represents the number of rows that were modified.
    delete_result = cur.rowcount 
    return delete_result


'''

Included below are additional helper functions for formatting.

'''

#This helper function is designed to format the dates. In HTML, dates are represented as YYYY-MM-DD, whereas in our MySQLdatabase 
#the dates are formatted as MM/DD/YYYY with no trailing zeroes.
def format_transaction_date(transaction_date):

    # Convert the transaction_date string to a datetime object
    transaction_date_obj = datetime.strptime(transaction_date, '%Y-%m-%d')

    # Format the datetime object to the desired format without leading zeroes
    transaction_date_formatted = transaction_date_obj.strftime('%m/%d/%Y')

    # Remove leading zeroes from day and month if present
    transaction_date_final = '/'.join(str(int(x)) for x in transaction_date_formatted.split('/'))

    return transaction_date_final

#This helper function is designed to format the 'total_sale' amount like the other values in our MySQL database.
def format_total_sale(total_sale):

    #Convert total_sale to float and format it to two decimal places.
    total_sale_formatted = '{:,.2f}'.format(float(total_sale))

    #Add dollar sign to the formatted total_sale.
    total_sale_with_currency = '$' + str(total_sale_formatted)

    return total_sale_with_currency



