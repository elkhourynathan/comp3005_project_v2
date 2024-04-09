# COMP 3005 - Project V2 

#### About

This was created for the final project of COMP3005 which is a Health and Fitness Club Management System.

Created by Nathan El-Khoury

### File Structure

- `backend/`: This directory contains all the backend code for the application, written in Flask.
    - `admin.py`: Contains Admin related routes
    - `app.py`: Contains the core Flask App
    - `auth.py`: Contains authentication logic and routes
    - `database.py`: Initializes the db object using ORM
    - `member.py`: Contains Member related routes
    - `models.py`: Model definitions for the ORM
    - `trainer.py`: Contains Trainer related routes
    - `views.py`: Contains core routes such as home and decorater functions to handle re-routing
    - `requirements.txt`: This file lists all the Python packages that the application depends on.
    - `static/`: This directory contains static files like CSS and JavaScript files.
        - `main.js`: This is the main JavaScript file for the application.
    - `templates/`: This directory contains the HTML templates that the application uses.
- `SQL/`: This directory contains SQL scripts.
    - `DDL.sql`: This file contains Data Definition Language (DDL) statements for setting up the database schema.
    - `DML.sql`: This file contains Data Manipulation Language (DML) statements for manipulating data in the database.
- `docs/`: This directory contains drawio, png, and final report documentation
- `README.md`: This file contains documentation on the project and instructions on how to run the application.

### ER Model
![ER Model](/docs/v2_diagrams-ER%20Model.drawio.png)

### Relational Schema
![Relational Schema](/docs/v2_diagrams-Relational%20Schema.drawio.png)


### Configuration

Before running the application, you need to create a `.env` file in the root directory `/backend` of the project and add your PostgreSQL database credentials to it. Here's an example:

```env
MYAPP_DATABASE=your_database
MYAPP_USER=your_username
MYAPP_PASSWORD=your_password
MYAPP_HOST=localhost
MYAPP_PORT=5432
```

Additionally, you must run the DDL.sql and DML.sql to create and populate your postgres database. These can be found in the `/SQL` folder

### Installation
Before you can run the application, you need to install the necessary requirements. You can do this by running the following command in your terminal. Ensure you are within the `/backend` directory in your terminal.

```bash
cd ./backend
pip install -r requirements.txt
pip3 install -r requirements.txt
```
### How to Run:

1. To run the application navigate to the `/backend` directory
2. Run the application from the command below:
```bash
flask run
```
3. Access the application by opening a web browser and navigating to
``` bash
http://localhost:5000
```
Note: Though `__init__.py` is empty it causes Flask to recognize the entire directory as a Python package, so running `flask run` from the root of the project will start the application.