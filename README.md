
# flask app

This is a basic modular Web Application designed to connect to a MySQL database to modify, add, and delete data. It implements CRUD concepts and offers an easy-to-use interface while following the REST architecture. Included are the dependencies needed to run the app as well as a sample MySQL database.

## Getting Started:

### ⭐ You can begin by downloading all of this project's dependencies by running this command from your terminal:
`pip install -r requirements.txt`

### OR... you can download everything manually by following these steps:

#### STEP 1: Firstly, you should create a virtual environment to isolate project dependencies and avoid version conflicts. You can do this by running the following command from your terminal. 

` virtualenv -p python3 env` or  `python3 -m venv env`

#### Alternatively, if in VS Code, you can click on 'View' > 'Command Palette...' > 'Python: Create Environment' > 'Venv'

#### STEP 2: Next, you should activate your virtual environment by running the following command:
` . env/Scripts/activate `

#### STEP 3: After activating your Venv you can now download Flask by running this command:  
`pip install flask`

#### STEP 4: Download the Python MySQL Connector to connect to MySQL by running this command:

` pip install mysql-connector-python`

#### STEP 5: You need to modify the 'password' within 'SQL_Connection.py' to successfully connect to your MySQL workbench. It is also advised that you run the app in debug mode to facilitate making changes to the program. You can do this by changing:

```
if __name__ == "__main__":
    app.run()
```

#### to:


```
if __name__ == "__main__":
    app.run(debug = True)
```

#### Additionally, you should also download Bootstrap and extract files to your project directory by following this link:
https://getbootstrap.com/docs/4.3/getting-started/download/ 

#### Once you have downloaded all of these packages/dependencies, you are ready to get started!


## Main Pages:
![homepage](https://github.com/hussiel/Hello-Flask/assets/142855475/3a15fb54-a5db-42cd-adc9-b5491fa24c9c)

![selectdate](https://github.com/hussiel/Hello-Flask/assets/142855475/8020ef5c-713d-4731-8de2-95981b937527)

![filteredpage](https://github.com/hussiel/Hello-Flask/assets/142855475/f1e876b7-bf30-4830-8da4-52957996e634)


## Pagination Features:
![pagination](https://github.com/hussiel/Hello-Flask/assets/142855475/6d3dcb84-3641-4432-91da-02f4d1063642)
![pagination for dict](https://github.com/hussiel/Hello-Flask/assets/142855475/2d8cbbd0-46c6-4c84-bd7d-cb3d3e784ed5)









