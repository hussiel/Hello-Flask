'''
This module represents the main entry point for the flask application. It contains all of the routes that correspond
to endpoints of the web app. Included at the very bottom is also a function that takes in a string parameter representing an 
SQL query that executes it to retrieve data. This query is based on user-input from the terminal and is currently commented out.
'''
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session

#This will be used to convert data to a Pandas Data Frame.
import pandas as pd

#These functions are imported to ensure modularity and abstraction.
from functions.crud_functions import *

#This will be used to change the date format from yyyy-mm-dd to mm/dd/yyyy to ensure consistency within the database.
from datetime import datetime


#This represents an instance of a Flask web application.
app = Flask(__name__)
app.secret_key = "MyVerySecretKey"

#Below are the routes/decorators used to register a view function for a given URL rule.

#This will represent a decorator for the 'home' web page.
@app.route("/")
def home():

    #This variable represents every single entry in the 'sales' table.
    all_sales = all_entries()

    #---------------------
    '''
    These variables will help implement pagination to avoid slowing down the web app when
    attempting to display all entries from the database.

    '''
    #---------------------

    #This gets the current page, if no value provided the default is 1.
    page = request.args.get('page', 1, type = int)

    #This represents the number of entries shown per page.
    per_page = 25 

    #This represents the starting index for entries being displayed.
    start = (page - 1) * per_page 

    #Similarly, this is the ending index for entries being displayed.
    end = start + per_page

    #This variable represents the minimum number of pages needed to display all of the entries.
    total_pages = (len(all_sales) + per_page - 1) // per_page

    #This represents the entries displayed within a page.
    items_on_page = all_sales[start:end]

    #Render 'hmtl' template with given parameters to keep track of current pages.
    return render_template('home.html', items_on_page = items_on_page, 
                           total_pages = total_pages, page = page) 

#This route will allow data to be selected from a given date range.
@app.route("/select_between_dates", methods=['GET', 'POST'])
def select_by_date():

    #First, check if the method is a 'POST' or 'GET.
    #Initially, it will be a 'POST' since you are inputting date parameters to filter the data.
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        #Copy of start_date to check for logic. Also formats it.
        start_date_c = datetime.strptime(start_date, '%Y-%m-%d').date()

        #This represents current date.
        todays_date = datetime.now().date()

        #This creates a flash message in case the input 'start_date'is later than today's date.
        if start_date_c > todays_date:
            flash("Start date cannot be later than today's date!")

        #Store start_date and end_date in session for later use.
        session['start_date'] = start_date
        session['end_date'] = end_date

        #Redirect with query parameters instead of storing in session to maintain RESTful principles.
        return redirect(url_for('select_by_date', start_date=start_date, end_date=end_date))
    
    #If you are wanting to retrieve data, this will be a 'GET' method.
    elif request.method == 'GET':

        #Retrieve start_date and end_date from session.
        start_date = session.get('start_date')
        end_date = session.get('end_date')

        #This represents the filtered data.
        selected_entries = entries_by_date(start_date, end_date)

        #For pagination purposes.
        per_page = 25
        total_pages = (len(selected_entries) + per_page - 1) // per_page
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * per_page
        end = min(start + per_page, len(selected_entries))
        items_on_page = selected_entries[start:end]

        #Render template with current information.
        return render_template('filtered_data.html', items_on_page=items_on_page,
                               total_pages=total_pages, page=page)

#This route will allow the addition of a new entry or row to the MySQL database.
@app.route("/add_entry", methods = ['POST'])
def add():
    id = request.form['id']
    store_code = request.form['store_code']
    total_sale = request.form['total_sale']
    transaction_date = request.form['transaction_date']

    #This variable essentially represents whether or not an entry was added successfully.
    add_result = add_entry(id, store_code, total_sale, transaction_date)

    #This will redirect you based on whether or not the addition was successful.
    if(add_result == 1):
        #return all_entries()
        flash('Your Entry Has Been Added To The Database!')
        return redirect(url_for('home'))
    #If addition was not successful, you will be given an error message.
    else:
        flash('Your Entry Cannot Be Added To The Database At This Time...')
        return redirect(url_for('home'))
    
#This route will allow an entry to be edited and updated within the database.
@app.route("/edit_entry", methods = ['GET', 'POST'])
def edit():
    if request.method == 'POST':
        id = request.form['id']
        store_code = request.form['store_code']
        total_sale = request.form['total_sale']
        transaction_date = request.form['transaction_date']

        edit_result = edit_entry(id, store_code, total_sale, transaction_date)
        if(edit_result):
            #Flash message to show that update was successful.
            flash('Your Entry Was Updated!')
            return redirect(url_for('home'))
        #If update was not successful, you will be given an error message.
        else:
            flash('Your Entry Cannot Updated At This Time...')
            return redirect(url_for('home'))

#This route will allow an entry to be deleted from the database.
@app.route("/delete_entry/<id>/", methods = ['GET'])
def delete(id):
        delete_result = delete_entry(id)
        if(delete_result):
            #Flash message to show that deletion was successful.
            flash('Your Entry Was Deleted!')
            return redirect(url_for('home'))
        #If deletion was not successful, you will be given an error message.
        else:
            flash('Your Entry Cannot Deleted At This Time...')
            return redirect(url_for('home'))

#--------------------------------------------------------------------------------
'''

*Following are routes for the data types to be displayed. There is a separate endpoint for each case:

*No filter (no given date parameters) --> all entries will be displayed as one of either of the three data types.
If date parameters are given --> filtered entries will be displayed as one of the three data types 
(technically four, since I am including my own table to facilitate data manipulation).

*This section will create links to navigate through pages.
You will have to manually input these links into your address bar to access these web pages.

*This approach comes from HATEOAS (Hypermedia as the Engine of Application State), a REST architectural constraint.
HATEOAS enables users to interact with a server using only provided links within data representations.

*Basically, it means that APIs can make links to associated resources along the returned data. 
By embedding links for navigating to previous and next pages within the JSON response, you maintain the stateless principle
followed by RESTful API's. Granted, I did import 'session' which goes against the stateless principle, but it was only to 
facilitate pagination for the 'table' data structure which greatly facilitates data manipulation.

'''
#--------------------------------------------------------------------------------

#This route will allow us to determine the chosen data type to be displayed if no date parameters are given.
@app.route("/get_data_type", methods = ['POST'])
def get_data_type():

    #Get selected data type.
    data_type = request.form['data_type']

    #Redirect based on chosen data type.
    if data_type == 'json_dict':
        return redirect(url_for('as_jsondict'))

    if data_type == 'list':
        return redirect(url_for('as_list'))

    if data_type == 'pandasdf':
        return redirect(url_for('as_pandasdf'))
    
    #If default option is kept, redirect to 'home'.
    return redirect(url_for('home'))

#This route will allow data to be represented as a JSON dictionary if no date parameters are given.
@app.route("/as_jsondict", methods=['GET'])
def as_jsondict():

    #Retrieve all entries from database.
    all_data = all_entries()

    #For pagination.
    page = request.args.get('page', 1, type=int)
    per_page = 50
    start = (page - 1) * per_page 
    end = start + per_page
    items_on_page = all_data[start:end]
    total_pages = (len(all_data) + per_page - 1) // per_page

    links = {}
    if page > 1:
        links['prev'] = url_for('as_jsondict', page=page-1)
    if page < total_pages:
        links['next'] = url_for('as_jsondict', page=page+1)

    #This will return a JSON dict containing each of our entries (as JSON dicts) as well as other information about the page.
    response = {
        'data': items_on_page,
        'total pages': total_pages,
        'current page': page,
        'links': links
    }

    #This will return a JSON dict containing our data as well as other information about the page like links.
    return jsonify(response)
    
#This route will allow data to be represented as a list if no date parameters are given.
@app.route("/as_list", methods = ['GET'])
def as_list():

    #Retrieve all entries from database.
    all_data = all_entries()

    #For pagination.
    page = request.args.get('page', 1, type=int)
    per_page = 50
    start = (page - 1) * per_page 
    end = start + per_page
    items_on_page = all_data[start:end]

    #This line converts the data to lists.
    items_on_page = [list(entry.values()) for entry in items_on_page]
    total_pages = (len(all_data) + per_page - 1) // per_page

    links = {}
    if page > 1:
        links['prev'] = url_for('as_list', page=page-1)
    if page < total_pages:
        links['next'] = url_for('as_list', page=page+1)

    #This makes a dictionary with our data and other information.
    response = {
    'data': items_on_page,
    'total pages': total_pages,
    'current page': page,
    'links': links
    }

    #This will return a JSON dict containing our data as lists as well as other information about the page like links.
    return jsonify(response)
    

#This route will allow data to be represented as a Pandas dataframe if no date parameters are given.
@app.route("/as_pandasdf", methods = ['GET'])
def as_pandasdf():

    #Retrieve all entries from database.
    all_data = pd.DataFrame(all_entries())

    #For pagination.
    page = request.args.get('page', 1, type=int)
    per_page = 50
    start = (page - 1) * per_page
    end = start + per_page

    #Iloc is integer-location based indexing for selection by position. 
    #I am using it here to slice the DataFrame and get all rows within the specified range.
    items_on_page = all_data.iloc[start:end]
    total_pages = (len(all_data) + per_page - 1) // per_page

    links = {}
    if page > 1:
        links['prev'] = url_for('as_pandasdf', page=page-1)
    if page < total_pages:
        links['next'] = url_for('as_pandasdf', page=page+1)

    
    #--------------------
    '''

    This converts DataFrame to dictionary so it can be displayed.
    In a Pandas DataFrame, key-value pairs can be customized with the parameters.
    Here I am using orient ='split' because it is JSON serializable.

    '''
    #--------------------

    #This makes a dictionary with our data and other information.
    response = {
        'data': items_on_page.to_dict(orient='split'),
        'total_pages': total_pages,
        'current_page': page,
        'links': links
    }

    #This will return a JSON dict containing our data as well as other information about the page like links.
    return jsonify(response)

'''
These represent routes for when date parameters are given (gdp = given date parameters).
'''
#This route will allow us to determine the chosen data type to be displayed if date parameters are given.
@app.route("/get_data_type_gdp", methods = ['POST'])
def get_data_type_gdp():

    #Get selected data type.
    data_type = request.form['data_type']

    #Redirect based on chosen data type.
    if data_type == 'json_dict':
        return redirect(url_for('as_jsondict_gdp'))

    if data_type == 'list':
        return redirect(url_for('as_list_gdp'))

    if data_type == 'pandasdf':
        return redirect(url_for('as_pandasdf_gdp'))
    
    #If default option is kept, redirect to 'select_by_date' page where you can see filtered data.
    return redirect(url_for('select_by_date'))


#This route will allow data to be represented as a JSON dictionary if given date parameters.
@app.route("/as_jsondict_gdp", methods = ['POST','GET'])
def as_jsondict_gdp():

    #Retrieve start_date and end_date from session.
    start_date = session.get('start_date')
    end_date = session.get('end_date')

    # Retrieve data based on the specified date range
    filtered_data = entries_by_date(start_date, end_date)

    #For pagination.
    page = request.args.get('page', 1, type=int)
    per_page = 50
    start = (page - 1) * per_page 
    end = start + per_page
    items_on_page = filtered_data[start:end]
    total_pages = (len(filtered_data) + per_page - 1) // per_page

    links = {}
    if page > 1:
        links['prev'] = url_for('as_jsondict_gdp', page=page-1)
    if page < total_pages:
        links['next'] = url_for('as_jsondict_gdp', page=page+1)

    #This will return a JSON dict containing each of our entries (as JSON dicts) as well as other information about the page.
    response = {
        'data': items_on_page,
        'total pages': total_pages,
        'current page': page,
        'links': links
    }

    #This will return a JSON dict containing our data as well as other information about the page like links.
    return jsonify(response)

#This route will allow data to be represented as a list if given date parameters..
@app.route("/as_list_gdp", methods = ['GET'])
def as_list_gdp():

    #Retrieve start_date and end_date from session.
    start_date = session.get('start_date')
    end_date = session.get('end_date')

    # Retrieve data based on the specified date range
    filtered_data = entries_by_date(start_date, end_date)

    #For pagination.
    page = request.args.get('page', 1, type=int)
    per_page = 50
    start = (page - 1) * per_page 
    end = start + per_page
    items_on_page = filtered_data[start:end]

    #This line converts the data to lists.
    items_on_page = [list(entry.values()) for entry in items_on_page]
    total_pages = (len(filtered_data) + per_page - 1) // per_page

    links = {}
    if page > 1:
        links['prev'] = url_for('as_list_gdp', page=page-1)
    if page < total_pages:
        links['next'] = url_for('as_list_gdp', page=page+1)

    #This makes a dictionary with our data and other information.
    response = {
    'data': items_on_page,
    'total pages': total_pages,
    'current page': page,
    'links': links
    }

    #This will return a JSON dict containing our data as lists as well as other information about the page like links.
    return jsonify(response)

#This route will allow data to be represented as a Pandas dataframe if given date parameters..
@app.route("/as_pandasdf_gdp", methods = ['GET'])
def as_pandasdf_gdp():

    #Retrieve start_date and end_date from session.
    start_date = session.get('start_date')
    end_date = session.get('end_date')

    #Retrieve all entries from database.
    filtered_data = pd.DataFrame(entries_by_date(start_date, end_date))

    #For pagination.
    page = request.args.get('page', 1, type=int)
    per_page = 50
    start = (page - 1) * per_page
    end = start + per_page

    #Iloc is integer-location based indexing for selection by position. 
    #I am using it here to slice the DataFrame and get all rows within the specified range.
    items_on_page = filtered_data.iloc[start:end]
    total_pages = (len(filtered_data) + per_page - 1) // per_page

    links = {}
    if page > 1:
        links['prev'] = url_for('as_pandasdf_gdp', page=page-1)
    if page < total_pages:
        links['next'] = url_for('as_pandasdf_gdp', page=page+1)

    #This makes a dictionary with our data and other information.
    response = {
        'data': items_on_page.to_dict(orient='split'),
        'total_pages': total_pages,
        'current_page': page,
        'links': links
    }

    #This will return a JSON dict containing our data as well as other information about the page like links.
    return jsonify(response)


'''
These are Jinja2 filters for parsing through 'html' dates.

'''

#This is a custom Jinja2 filter designed to parse and format the 'total_sale' values in order to maintain consistency.
@app.template_filter('parse_total_sale')
def parse_total_sale(total_sale):
    
    # Remove non-numeric characters from the string
    total_sale = ''.join(c for c in total_sale if c.isdigit() or c == '.')

    # Convert the cleaned-up string to a floating-point number
    total_sale = float(total_sale)

    return total_sale

#This is a custom Jinja2 filter designed to parse and format the 'transaction_date' values in order to maintain consistency.
@app.template_filter('format_date')
def format_date(date_str):

    # Convert the date string to a datetime object
    transaction_date = datetime.strptime(date_str, "%m/%d/%Y")
    # Format the datetime object as a string in "yyyy-mm-dd" format
    transaction_date = transaction_date.strftime("%Y-%m-%d")
    return transaction_date

#This will run the app.
if __name__ == "__main__":
    app.run()

# #This function takes in a SQL query and executes it to retrieve data.
# def execute_query(sql_query):

#     #This is a variable representing database connection.
#     sql_cxn = dbConnection()

#     #Cursor used to execute statements to communicate with the MySQL database.
#     cur = sql_cxn.cursor(dictionary = True) # 'dictionary=True' will return each entry as a dictionary

#     #This executes given query.
#     cur.execute(sql_query)

#     #This represents all entries in the database.
#     all_entries = cur.fetchall()

#     #Closes the cursor, resets all results, and ensures that the cursor object has no reference to its original connection object.
#     cur.close()

#     #Closes connection to MySQL database.
#     sql_cxn.close()
#     return all_entries

# #Prompt user to type SQL into terminal.
# sql_query = input("Enter your SQL query: ")
# data = execute_query(sql_query)
# print(data)
