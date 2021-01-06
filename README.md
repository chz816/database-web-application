# Database-Driven Web Applications with Flask
This is the repo for our designed database driven by a Flask based web application. In this project, we build a dynamic web application aimed to help our client to better manage her shelter.

We achieve the following:
- Create a Flask-based website driven by MySQL database
- Work with dynamic HTML templates
- Accept user input with HTML forms; user can modify or edit the information


## Team Members
- Jiachen Guo
- Zijun Huang
- Siyuan Liu
- Rachel Chujie Zheng

## Local Setup

Our platform is based on Flask in Python 3 and MySQL as DBMS, so please make sure you have correctly set up the environment in the very beginning. The following are some useful links for envrionment set up.

    1. Flask
    https://anaconda.org/anaconda/flask; 
    https://pypi.org/project/Flask/
    
    2. MySQL
    https://dev.mysql.com/doc/mysql-installation-excerpt/5.7/en/
    
    3. Flask-MySQL
    https://flask-mysql.readthedocs.io/en/latest/
    
    4. Ajax
    https://www.w3schools.com/xml/ajax_intro.asp

To install Flask, you can run the following command:
```bash
pip install Flask
```

### Installation

After setting up the environment mentioned above, please pull the files from our repository. You could either download as a zip file or type the following command in yoru terminal:
     
```bash
 git clone https://github.com/chz816/database-web-application.git
```

## Data
We provide a sample data for testing our implementation. You can directly run the following command to set up the database:
```bash
cd setup
./setup.sh
```

You can also modify the data by modifying the codes in ```setup``` folder. ```db_init.sql``` creates the database named ```DB``` in MySQL, and ```db_data.sql``` sets up the dataset.

## Launch
Use the following command to launch our app:
```bash
python app.py
```

then you should be able to see the following info in the terminal:
```
* Running on http://localhost:xxxx/ (Press CTRL+C to quit)
* Restarting with stat
* Debugger is active!
* Debugger PIN: xxx-xxx-xxx
```

finally you can land on our homepage by entering http://localhost:xxxx/ in the broswer (we prefer Chrome or Firefox).

### Note
If you find any issues or have some suggestions any time, please feel free to submit a request on our repositoty page. We will address the issue as soon as possible.
