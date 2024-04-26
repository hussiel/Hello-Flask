'''

This module contains a function that allows connection to a MySQL database. It will return a message if the connection was successful
or unsuccessful. You will need to change the password in order to be able to connect to your MySQL Workbench.

'''

#Library to connect to MySQL Database
import mysql.connector

#This function will be called from other modules in order to connect to SQL Database.
def dbConnection():
    my_db = mysql.connector.connect(
        host = 'localhost',
        user = 'root',
        password = '',
        database = 'store_data'
    )

    #This will return a message based on the status of the connection.
    if my_db:
        print("Connection to SQL Database was successful!")
        return my_db
    else:
        print("Connection to SQL Database was unsuccessful")

