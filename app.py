from flask import Flask, Response, session, render_template, request, jsonify, flash, redirect, url_for
from flaskext.mysql import MySQL
from dataaccessor import *
import datetime
import json

import pandas as pd

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'cs6400'
app.config['MYSQL_DATABASE_USER'] = 'USER'
app.config['MYSQL_DATABASE_PASSWORD'] = 'PASSWORD'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_DB'] = 'DB'
mysql.init_app(app)


# check whether it is loggin
def check_loggin(session):
    return session.get('loggin', False)


# check whether it is admin
def check_admin(session):
    return session.get('admin', False)


# get user name from session
def get_current_user(session):
    return session.get('username', None)


# pages
@app.route('/')
@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/go2Dashboard', methods=['GET', 'POST'])
def go2Dashboard():
    print('in go2Dashboard')
    # parse the params
    data_params = request.get_json()
    input_usr = data_params['usrname']
    input_psw = data_params['password']

    # connect to db
    conn = mysql.connect()
    cursor = conn.cursor()
    psw = getPsw4UsrInDB(cursor, input_usr)

    if not psw:
        print('Invalid email input')
        conn.close()
        error = 'Invalid email input'
        return jsonify(dict(error=error))

    elif psw[0][0] != input_psw:
        print('Unmatched email and password')
        conn.close()
        error = 'Unmatched email and password'
        return jsonify(dict(error=error))

    else:
        admin = checkAdmin4Usr(cursor, input_usr)
        session['loggin'] = True
        session['admin'] = admin
        session['username'] = input_usr
        conn.close()
        print('success, admin, input_usr')
        return jsonify(dict(redirect='dashboard'))


# pages
@app.route('/dashboard')
def dashboard():
    print(url_for('dashboard', status=0))
    return redirect(url_for('dashboardfilter', status=0))


@app.route('/dashboardfilter/<int:status>')
def dashboardfilter(status):
    print('in dashboardfilter')
    if not check_loggin(session):
        print('redirect to login')
        return redirect(url_for('login'))

    conn = mysql.connect()
    cursor = conn.cursor()

    # get dog list based on filter
    dog_list = None
    if status == 0:
        # column for dog_list: name, breed, sex, alteration, age, adoption_date, dogID, adoptability_status
        dog_list = getDogListInShelter(cursor)
        total_dog = len(dog_list)
    else:
        # here dog_list: give us the dog available for adoption
        dog_list, total_dog = getDogListInShelterWithAvaliableStatus(cursor)

        # get current info from session
    current_user = get_current_user(session)
    admin = check_admin(session)
    conn.close()
    print(dog_list)
    # column for dog_list:
    # name, breed, sex, alteration, age, adoption_date, dogID, surrender_date, adoptability_status
    # calculate age
    adjusted_dog_list = []
    for i in range(len(dog_list)):
        result = []
        for j in range(9):
            if j != 4:
                result.append(dog_list[i][j])
            else:
                surrender_age = dog_list[i][j]
                # calculate the current age
                end_date = datetime.datetime.today()
                # surrender_date
                start_date = dog_list[i][7]
                # calculate how many months between surrender date and today
                num_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
                # so the current age in terms of months should be
                current_age = surrender_age + num_months
                current_year = int(current_age / 12)
                current_month = current_age % 12
                if current_year == 0:
                    calculated_age = f"{current_month} Month(s)"
                else:
                    calculated_age = f"{current_year} Year(s) {current_month} Month(s)"
                result.append(calculated_age)
        adjusted_dog_list.append(result)

    print(current_user, int(admin))

    return render_template('dashboard.html', dog_list=adjusted_dog_list, dog_num=total_dog, admin_flag=int(admin),
                           status_flag=status)


@app.route('/go2Addadoptionapplication', methods=['GET', 'POST'])
def go2Addadoptionapplication():
    # print ('in go2Addadoptionapplication')
    # parse the params
    data_params = request.get_json()
    conn = mysql.connect()
    cursor = conn.cursor()

    appli_Num = getApplicationNuminDB(cursor)
    print('Get application num')
    print(appli_Num[0][0] + 1)
    input_appl = {}
    input_appl['status'] = 'pending approval'
    input_appl['appli_num'] = appli_Num[0][0] + 1
    input_appl['email'] = data_params['email']
    input_appl['firstname'] = data_params['firstname']
    input_appl['lastname'] = data_params['lastname']
    input_appl['co_applicant_first_name'] = data_params['co_applicant_first_name']
    input_appl['co_applicant_last_name'] = data_params['co_applicant_last_name']
    input_appl['date'] = data_params['date']
    input_appl['state'] = data_params['state']
    input_appl['city'] = data_params['city']
    input_appl['street'] = data_params['street']
    input_appl['cellphone'] = data_params['cellphone']
    input_appl['zipcode'] = data_params['zipcode']

    try:
        # connect to db
        conn = mysql.connect()
        cursor = conn.cursor()
        # add adoption application
        insertAdoptionApplication(cursor, conn, input_appl)
        conn.commit()
        print(cursor.rowcount, "Record inserted successfully into table")
        conn.close()
        flash(f"Success! Add new adoption application with application_num {input_appl['appli_num']} into db.")
    except Exception as e:
        flash(f"Fail! Problem adding new adoption application into db: {str(e)}")

    return jsonify(dict(redirect='dashboard'))


@app.route('/go2Adddog', methods=['GET', 'POST'])
def go2Adddog():
    print('in go2Adddog')
    # parse the params
    data_params = request.get_json()
    print(data_params)
    conn = mysql.connect()
    cursor = conn.cursor()

    dog_ID = getDogIDinDB(cursor)
    print('Get dog ID')
    print(dog_ID[0][0] + 1)
    input_dog = {}
    input_dog['dogID'] = dog_ID[0][0] + 1
    input_dog['breed'] = data_params['breed']
    input_dog['userID'] = data_params['userID']
    input_dog['uname'] = data_params['name']
    input_dog['uage'] = data_params['age']
    input_dog['ualterationstatus'] = data_params['alterationstatus']
    input_dog['usex'] = data_params['sex']
    input_dog['udesc'] = data_params['desc']
    input_dog['umicochipID'] = data_params['micochipID']
    input_dog['usurrenderDate'] = data_params['surrenderDate']
    input_dog['usurrenderReason'] = data_params['surrenderReason']
    input_dog['usurrenderbyanimalcontrol'] = data_params['surrenderbyanimalcontrol']
    input_dog['breed'] = data_params['breed']

    lower_name = data_params['name'].lower()

    microchip_flag = checkUniqueMicrochip(cursor, data_params['micochipID'])

    # requirement: 'Unknown' or 'Mixed' may be chosen as the only breed
    if ('Unknown' in data_params['breed'] or 'Mixed' in data_params['breed']) and len(
            data_params['breed']) > 1:
        flash(f"Fail! For Breed, 'Unknown' or 'Mixed' may be chosen as the only breed!")
    elif ('Bulldog' in data_params['breed']) and (len(data_params['breed']) == 1) and (lower_name == 'uga'):
        print("check joy")
        flash(f"Fail! Please enter some other name for the dog to be registered in the system.")
    elif len(microchip_flag) > 1:
        flash(f"Fail! Enter Microchip ID is duplicated in db. It should be globally unique.")
    else:
        # insert the values related to expense to db
        try:
            # connect to db
            conn = mysql.connect()
            cursor = conn.cursor()
            # insert information to Dog
            insertDog(cursor, conn, input_dog)
            conn.commit()
            print(cursor.rowcount, "Record inserted successfully into table")
            conn.close()
            flash(f"Success! Add new dog with dogID {input_dog['dogID']} into db.")
        except Exception as e:
            flash(f"Fail! Problem adding new dog into db: {str(e)}")
    # go back to the dashboard
    return jsonify(dict(redirect='dashboard'))


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    print('in logout')
    print(session)
    session.pop('loggin', None)
    session.pop('admin', None)
    session.pop('username', None)
    print(session)
    return redirect(url_for('login'))


@app.route('/add_dog')
def add_dog():
    print('in add_dog')
    if not check_loggin(session):
        print('redirect to login')
        return redirect(url_for('login'))
    return render_template('add_dog.html')


@app.route('/add_adoption_application')
def add_adoption_application():
    print('in add_adoption_application')
    if not check_loggin(session):
        print('redirect to login')
        return redirect(url_for('login'))
    return render_template('add_adoption_application.html')


@app.route('/report_generator')
def report_generator():
    print('in report_generator')
    if not check_loggin(session):
        print('redirect to login')
        return redirect(url_for('login'))
    return render_template('report_generator.html')


@app.route('/add_expense')
def add_expense():
    print('in add_expense')
    # get the dog_id from dog_details
    dog_id = request.args.get('dog_id')
    print(f"adding expense for dog {dog_id}")
    return render_template('add_expense.html', dog_id=dog_id)


@app.route('/go2Expense', methods=['GET', 'POST'])
def go2Expense():
    print('in go2Expense')
    # parse the params
    data_params = request.get_json()
    print(data_params)
    dog_id = int(data_params['dog_id'].replace('add_expense?dog_id=', ''))
    date = datetime.datetime.strptime(data_params['date'], '%Y-%m-%d')
    print(date)
    # connect to db
    conn = mysql.connect()
    cursor = conn.cursor()
    # check surrender date
    surrender_date = check_surrender_date(cursor, dog_id)
    print(surrender_date)
    # if entered date is after today: we file a error
    if date > datetime.datetime.today():
        flash("Fail! Please check your input date. It looks like the input date is a future date.")
    # if the input date is before the surrender date: we file a error
    elif date < datetime.datetime(surrender_date.year, surrender_date.month, surrender_date.day):
        flash("Fail! Please check your input date. It looks like the input date is before the surrender date.")
    else:
        # insert the values related to expense to db
        try:
            addExpense(cursor, data_params, dog_id)
            conn.commit()
            print(cursor.rowcount, "Record inserted successfully into table")
            conn.close()
            flash(f"Success! Insert new expense into db.")
        except Exception as e:
            flash(f"Fail! Problem inserting into db: {str(e)}")

    return jsonify(dict(redirect='/dog_details', dog_id=dog_id))


@app.route('/dog_details')
def dog_details():
    print('in dog_details')
    dog_id = request.args.get('dog_id')
    print(f"we're reviewing the information for {dog_id}")
    if not check_loggin(session):
        print('redirect to login')
        return redirect(url_for('login'))
    return redirect(url_for('go2DogDetails', dog_id=dog_id))


@app.route('/go2DogDetails', methods=['GET', 'POST'])
def go2DogDetails():
    print('in go2DogDetails')
    if not check_loggin(session):
        print('redirect to login')
        return redirect(url_for('login'))

    # get the dog_id
    dog_id = request.args.get('dog_id')

    print(f"display the information for dog {dog_id}")

    # connect to the database
    conn = mysql.connect()
    cursor = conn.cursor()

    # get dog details for specific dog - based on dog_id
    # first: get dog general detailed info (exclude expense) based on the selected dog ID
    dog_info = getDogDetailsExpectExpense(cursor, dog_id)

    print(dog_info)

    # extract information from tuple
    name = dog_info[0][0]
    breed = dog_info[0][1]
    sex = dog_info[0][2]
    alteration = dog_info[0][3]
    # age: it corresponds to the dog age (month) when the dog is surrendered
    age = dog_info[0][4]
    # get the surrender_daye
    surrender_date = dog_info[0][7].strftime('%Y-%m-%d')
    # calculate the current age
    end_date = datetime.datetime.today()
    start_date = dog_info[0][7]
    # calculate how many months between surrender date and today
    num_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
    # so the current age in terms of months should be
    current_age = age + num_months
    current_year = int(current_age / 12)
    current_month = current_age % 12
    if current_year == 0:
        calculated_age = f"{current_month} Month(s)"
    else:
        calculated_age = f"{current_year} Year(s) {current_month} Month(s)"

    description = dog_info[0][5]
    microchipID = dog_info[0][6]

    surrender_reason = dog_info[0][8]
    surrender_by_animal_control = dog_info[0][9]

    print(f"extract detailed information for dog {dog_id}")

    # calculate total expenses
    total_expense = getDogDetailsTotalExpense(cursor, dog_id)
    print(f"total expense for dog {dog_id} is: {total_expense}")

    # combine adjusted answers together
    dog_details_list = [name, breed, sex, alteration, calculated_age, description, microchipID, surrender_date,
                        surrender_reason,
                        surrender_by_animal_control, total_expense]

    # extract the expenses
    dog_expense = getDogDetailsExpense(cursor, dog_id)

    # how many transactions associated with this dog
    dog_expense_num = len(dog_expense)
    print(f"there are {dog_expense_num} transactions associated with dog {dog_id}")

    # adjust the format for dog_expense
    dog_expense_list = []
    for i in range(dog_expense_num):
        result = []
        for j in range(5):
            if j == 1:
                result.append(dog_expense[i][j].strftime('%Y-%m-%d'))
            else:
                result.append(dog_expense[i][j])
        dog_expense_list.append(result)

    # check for admin
    admin = check_admin(session)

    # check if this dog is eligible for adoption
    if type(microchipID) == str and len(microchipID) > 0 and alteration == 1:
        dog_eligible4adoption_flag = 1
    else:
        dog_eligible4adoption_flag = 0

    return render_template('dog_details.html', dog_id=dog_id, dog_details_list=dog_details_list,
                           dog_expense=dog_expense_list, dog_expense_num=dog_expense_num, admin_flag=int(admin),
                           dog_eligible4adoption_flag=dog_eligible4adoption_flag)


@app.route('/adoption_application_review/<int:page>')
def adoption_application_review(page=0):
    print('in adoption_application_review')
    if not check_loggin(session):
        print('redirect to login')
        return redirect(url_for('login'))

    conn = mysql.connect()
    cursor = conn.cursor()
    adoption_application_review = getAdoptionApplicationReview(cursor)
    title = getAdoptionApplicationReviewColumnName()
    conn.close()

    record_per_page, record_total = 20, len(adoption_application_review)
    minpage = 0
    maxpage = int(record_total / record_per_page) + (record_total % record_per_page > 0)

    data = adoption_application_review[page * record_per_page: (page + 1) * record_per_page]
    return render_template('adoption_application_review.html', data=data, title=title, page=page, minpage=minpage,
                           maxpage=maxpage)


@app.route('/change_adoption_application_status/<string:appl_num>/<string:status>')
def change_adoption_application_status(appl_num, status):
    print('in change_adoption_application_status')
    if not check_loggin(session):
        print('redirect to login')
        return redirect(url_for('login'))

    conn = mysql.connect()
    cursor = conn.cursor()
    # print(email, status)
    try:
        if status=="approved":
            flash("Success! We approve the adoption application.")
        else:
            flash("Success! We reject the adoption application.")
    except Exception as e:
        flash(f"fails to updating the status of the adoption application due to: {str(e)}")
    conn.close()
    return redirect(url_for('adoption_application_review', page=0))


@app.route('/update_sex')
def update_sex():
    """From dog_details, update the sex information"""
    print('in update_sex')
    # get the dog_id from dog_details
    dog_id = request.args.get('dog_id')
    print(f"updating the sex info for dog {dog_id}")
    return render_template('update_sex.html', dog_id=dog_id)


@app.route('/go2UpdateSex', methods=['GET', 'POST'])
def go2UpdateSex():
    print('in go2UpdateSex')
    # parse the params
    data_params = request.get_json()
    print(data_params)
    # connect to db
    conn = mysql.connect()
    cursor = conn.cursor()
    dog_id = int(data_params['dog_id'].replace('update_sex?dog_id=', ''))

    # insert the values related to expense to db
    try:
        updateDogSex(cursor, data_params, dog_id)
        conn.commit()
        print(cursor.rowcount, "Record updated successfully into table")
        conn.close()
        flash(f"Success! Update sex into db.")
    except Exception as e:
        flash(f"Fail! Problem inserting into db: {str(e)}")

    return jsonify(dict(redirect='/dog_details', dog_id=dog_id))


@app.route('/update_breed')
def update_breed():
    """From dog_details, update the breed information"""
    print('in update_breed')
    # get the dog_id from dog_details
    dog_id = request.args.get('dog_id')
    print(f"updating the breed info for dog {dog_id}")
    return render_template('update_breed.html', dog_id=dog_id)


@app.route('/go2UpdateBreed', methods=['GET', 'POST'])
def go2UpdateBreed():
    print('in go2UpdateBreed')
    # parse the params
    data_params = request.get_json()
    print(data_params)
    # extract the dog id
    dog_id = data_params['dog_id'].replace('update_breed?dog_id=', '')
    # connect to db
    conn = mysql.connect()
    cursor = conn.cursor()
    # get the dog_name
    dog_name = getDogName(cursor, dog_id)[0][0]
    lower_name = dog_name.lower()
    # requirement: 'Unknown' or 'Mixed' may be chosen as the only breed
    if ('Unknown' in data_params['updated_breed'] or 'Mixed' in data_params['updated_breed']) and len(
            data_params['updated_breed']) > 1:
        flash(f"Fail! For Breed, 'Unknown' or 'Mixed' may be chosen as the only breed!")
    elif lower_name == 'uga' and len(data_params['updated_breed']) == 1 and 'Bulldog' in data_params['updated_breed']:
        flash(f"Fail! You can't register a bulldog with the name Uga.")
    else:
        # insert the values related to expense to db
        try:
            # update the dog breed
            updateDogBreed(cursor, data_params, dog_id)
            conn.commit()
            print(cursor.rowcount, "Record updated successfully into table")
            conn.close()
            flash(f"Success! Update breed into db.")
        except Exception as e:
            flash(f"Fail! Problem inserting into db: {str(e)}")

    return jsonify(dict(redirect='/dog_details', dog_id=dog_id))


@app.route('/update_alteration')
def update_alteration():
    """From dog_details, update the alteration status information"""
    print('in update_alteration')
    # get the dog_id from dog_details
    dog_id = request.args.get('dog_id')
    print(f"updating the alteration status for dog {dog_id}")
    return render_template('update_alteration.html', dog_id=dog_id)


@app.route('/go2UpdateAlteration', methods=['GET', 'POST'])
def go2UpdateAlteration():
    print('in go2UpdateAlteration')
    # parse the params
    data_params = request.get_json()
    print(data_params)
    dog_id = int(data_params['dog_id'].replace('update_alteration?dog_id=', ''))
    # connect to db
    conn = mysql.connect()
    cursor = conn.cursor()

    # insert the values related to expense to db
    try:
        updateDogAlteration(cursor, data_params, dog_id)
        conn.commit()
        print(cursor.rowcount, "Record updated successfully into table")
        conn.close()
        flash(f"Success! Update alteration status into db.")
    except Exception as e:
        flash(f"Fail! Problem inserting into db: {str(e)}")

    return jsonify(dict(redirect='/dog_details', dog_id=dog_id))


@app.route('/update_microchip')
def update_microchip():
    """From dog_details, update the microchip ID information"""
    print('in update_microchip')
    # get the dog_id from dog_details
    dog_id = request.args.get('dog_id')
    print(f"updating the microchip ID for dog {dog_id}")
    return render_template('update_microchip.html', dog_id=dog_id)


@app.route('/go2UpdateMicrochip', methods=['GET', 'POST'])
def go2UpdateMicrochip():
    print('in go2UpdateMicrochip')
    # parse the params
    data_params = request.get_json()
    print(data_params)
    dog_id = int(data_params['dog_id'].replace('update_microchip?dog_id=', ''))
    # connect to db
    conn = mysql.connect()
    cursor = conn.cursor()

    # extract values from data_params
    updated_microchip = data_params['updated_microchip']

    # check if the enter microchip ID is unique
    unique_flag = checkUniqueMicrochip(cursor, updated_microchip)

    if len(unique_flag) > 0:
        flash('Failed! Your microchip ID input exists in db. This attribute should be globally unique.')
    else:
        # insert the values related to expense to db
        try:
            updateDogMicrochip(cursor, data_params, dog_id)
            conn.commit()
            print(cursor.rowcount, "Record updated successfully into table")
            conn.close()
            flash(f"Success! Update microchip ID into db.")
        except Exception as e:
            flash(f"Fail! Problem inserting into db: {str(e)}")

    return jsonify(dict(redirect='/dog_details', dog_id=dog_id))


@app.route('/add_adoption_search')
def add_adoption_search():
    print("in add_adoption_search")
    if not check_loggin(session):
        print('redirect to login')
        return redirect(url_for('login'))

    if not check_admin(session):
        print('')
        return redirect(url_for('dashboard'))

    dog_id = request.args.get('dog_id')
    print(f"adding adoption for dog {dog_id}")
    return render_template('add_adoption_search.html', dog_id=dog_id)


@app.route('/add_adoption_result', methods=['POST', 'GET'])
def add_adoption_result():
    print('in add_adoption_result')
    dog_id = request.args.get('dog_id')
    print(f"adding adoption for dog {dog_id}")

    if not check_loggin(session):
        print('redirect to login')
        return redirect(url_for('login'))

    if not check_admin(session):
        print('')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        search = request.form.get('search')
        print(f"search content: {search}")
        conn = mysql.connect()
        cursor = conn.cursor()

        search_list = adoptionSearch(cursor, search)
        conn.close()

        # adjust the datetime type for search_list
        search_result = []
        for i in range(len(search_list)):
            email = search_list[i][0]
            application_num = search_list[i][1]
            date = search_list[i][2].strftime('%Y-%m-%d')
            co_applicant_first_name = search_list[i][3]
            co_applicant_last_name = search_list[i][4]
            first_name = search_list[i][5]
            last_name = search_list[i][6]
            state = search_list[i][7]
            city = search_list[i][8]
            street = search_list[i][9]
            zip = search_list[i][10]
            cell = search_list[i][11]
            applicant_name = f"{first_name} {last_name}".title()
            if co_applicant_first_name != None and co_applicant_last_name != None:
                co_applicant_name = f"{co_applicant_first_name} {co_applicant_last_name}".title()
            else:
                co_applicant_name = ""
            search_result.append(
                [email, application_num, date, co_applicant_first_name, co_applicant_last_name, first_name, last_name,
                 state, city, street, zip, cell, applicant_name, co_applicant_name])
        print(search_result)

        search_result_num = len(search_result)

        return render_template("add_adoption_result.html", dog_id=dog_id, search_result=search_result, search=search,
                               search_result_num=search_result_num)


@app.route('/adoption_result_select')
def adoption_result_select():
    dog_id = request.args.get('dog_id')
    email = request.args.get('email')
    print(f'in adoption_result_select for {dog_id}')
    if not check_loggin(session):
        print('redirect to login')
        return redirect(url_for('login'))
    conn = mysql.connect()
    cursor = conn.cursor()
    print(f"selectd email is: {email}")
    # return the most recent adoption application based on adopter's email
    most_recent_application = adoptionSearchSelect(cursor, email)
    most_recent_application_num = most_recent_application[0][0]
    most_recent_application_date = most_recent_application[0][1]
    # calculate the adoption fee
    adoption_fee_list = calculate_adoption_fee(cursor, dog_id)

    if adoption_fee_list[0][1] == None:
        adoption_fee = 0
    else:
        adoption_fee = adoption_fee_list[0][1]

    conn.close()
    return render_template('adoption_result_application.html', most_recent_application_num=most_recent_application_num,
                           email=email, dog_id=dog_id, adoption_fee=adoption_fee,
                           most_recent_application_date=most_recent_application_date)


@app.route('/approveAdoption', methods=['GET', 'POST'])
def approveAdoption():
    """Adoption is added and confirmed by admin user"""
    data_params = request.get_json()
    print(data_params)
    # dog_id
    dog_id = data_params['dog_id']
    # adoption_fee
    adoption_fee = data_params['adoption_fee']
    # adoption date
    adoption_date = data_params['date']
    # application number
    application_num = data_params['application_num']
    print(f"in approveAdoption for {dog_id}")

    # submit the adoption details to the database
    conn = mysql.connect()
    cursor = conn.cursor()

    date = datetime.datetime.strptime(adoption_date, '%Y-%m-%d')
    # check surrender date
    surrender_date = check_surrender_date(cursor, dog_id)
    print(surrender_date)
    # if entered date is after today: we file a error
    if date > datetime.datetime.today():
        flash("Fail! Please check your input adoption date. It looks like the input date is a future date.")
    # if the input date is before the surrender date: we file a error
    elif date < datetime.datetime(surrender_date.year, surrender_date.month, surrender_date.day):
        flash("Fail! Please check your input adoption date. It looks like the input date is before the surrender date.")
    else:
        # insert the values related to expense to db
        try:
            submitAdoption2db(cursor, dog_id, adoption_fee, adoption_date, application_num)
            conn.commit()
            print(cursor.rowcount, "Record inserted successfully into table")
            conn.close()
            flash(f"Success! Insert new adoption into db.")
        except Exception as e:
            flash(f"Fail! Problem inserting into db: {str(e)}")
    # go back to dashboard
    return jsonify(dict(redirect='dashboard'))


@app.route('/report/animal_control')
def animal_control_report():
    print()
    if not check_loggin(session):
        print('redirect to login')
        return redirect(url_for('login'))
    if not check_admin(session):
        print('')
        return redirect(url_for('dashboard'))

    conn = mysql.connect()
    cursor = conn.cursor()
    AC_report = getAnimalControlReport(cursor)
    conn.close()
    return render_template('animal_control_report.html', AC_report=AC_report)


@app.route('/report/animal_control/drilldown/<int:rpt_type>/<int:year>/<int:month>')
def animal_control_report_drilldown(rpt_type, year, month):
    print()
    if not check_loggin(session):
        print('redirect to login')
        return redirect(url_for('login'))

    if not check_admin(session):
        print('')
        return redirect(url_for('dashboard'))

        # year = int(request.args.get("year"))
    # month = int(request.args.get("month"))
    # rpt_type = request.args.get("rpt_type") 

    conn = mysql.connect()
    cursor = conn.cursor()
    Drill_down = getDrilldownReport(cursor, rpt_type=rpt_type, year=year, month=month)
    conn.close()
    return render_template('animal_control_report_drilldown.html', Drill_down=Drill_down, rpt_type=rpt_type, year=year,
                           month=month)


@app.route('/report/monthly_adoption_report')
def monthly_adoption_report():
    print()
    if not check_loggin(session):
        print('redirect to login')
        return redirect(url_for('login'))

    if not check_admin(session):
        print('')
        return redirect(url_for('dashboard'))
    conn = mysql.connect()
    cursor = conn.cursor()
    Mthly_report = getMonthlyAdoptionReport(cursor)
    conn.close()
    return render_template('monthly_adoption_report.html', Mthly_report=Mthly_report)


@app.route('/report/expense_analysis')
def expense_analysis():
    print()
    if not check_loggin(session):
        print('redirect to login')
        return redirect(url_for('login'))

    if not check_admin(session):
        print('')
        return redirect(url_for('dashboard'))

    conn = mysql.connect()
    cursor = conn.cursor()
    Expense_report = getExpenseAnalysis(cursor)
    conn.close()
    return render_template('expense_analysis.html', Expense_report=Expense_report)


@app.route('/report/volunteer_lookup')
def volunteer_lookup():
    if not check_loggin(session):
        print('redirect to login')
        return redirect(url_for('login'))

    if not check_admin(session):
        print('')
        return redirect(url_for('dashboard'))
    return render_template('volunteer_lookup.html')


@app.route('/report/volunteer_lookup_result', methods=['POST', 'GET'])
def volunteer_lookup_result():
    print('in volunteerLookupResult')

    if not check_loggin(session):
        print('redirect to login')
        return redirect(url_for('login'))

    if not check_admin(session):
        print('')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name = request.form.get('uname')
        print(request.form)
        conn = mysql.connect()
        cursor = conn.cursor()

        data = getVolunteerLookup(cursor, name)
        num_volunteer = len(data)
        title = volunteerColumns()
        conn.close()
        return render_template("volunteer_results.html", data=data, title=title, num_volunteer=num_volunteer)


if __name__ == '__main__':
    app.run(host='localhost', port=8888, debug=True)
