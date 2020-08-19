def getPsw4UsrInDB(cursor, input_usr):
    query = "SELECT password FROM User WHERE email = %(usrname)s"
    cursor.execute(query, {'usrname': input_usr})
    psw = cursor.fetchall()
    return psw


def checkAdmin4Usr(cursor, input_usr):
    query = "SELECT email FROM Owner WHERE email = %(usrname)s"
    cursor.execute(query, {'usrname': input_usr})
    email = cursor.fetchall()
    return bool(len(email) == 1)


def getDogListInShelter(cursor):
    query = "SELECT Dog.name, DogBreed.breed, Dog.sex, Dog.alteration, Dog.age, DogAdoption.adoption_date, Dog.dogID, Dog.surrender_date, \
             CASE WHEN Dog.alteration = 1 AND Dog.microchipID IS NOT NULL THEN 'AVAILABLE' ELSE 'NOT AVAILABLE' END AS adoptability_status \
             FROM Dog LEFT JOIN (SELECT DISTINCT dogID, GROUP_CONCAT(DISTINCT breed ORDER BY dogID SEPARATOR '/') AS breed \
             FROM BelongTo GROUP BY dogID) DogBreed ON Dog.dogID = DogBreed.dogID \
             LEFT JOIN (SELECT Adoption.dog, Adoption.adoption_date FROM Adoption) DogAdoption \
             ON Dog.dogID = DogAdoption.dog WHERE DogAdoption.adoption_date IS NULL ORDER BY Dog.surrender_date ASC;"
    cursor.execute(query)
    query_result = cursor.fetchall()
    return query_result


def getDogListInShelterWithAvaliableStatus(cursor):
    """Select the dog whose status is AVAILABLE"""
    query = "SELECT * FROM (SELECT Dog.NAME, DogBreed.breed, Dog.sex, Dog.alteration, Dog.age, DogAdoption.adoption_date, Dog.dogID, Dog.surrender_date, \
             CASE WHEN Dog.alteration = 1 AND Dog.microchipID IS NOT NULL THEN 'AVAILABLE' ELSE 'NOT AVAILABLE' END AS adoptability_status FROM Dog  \
             LEFT JOIN (SELECT DISTINCT dogID, GROUP_CONCAT(DISTINCT breed ORDER BY dogID SEPARATOR '/') AS breed FROM BelongTo GROUP BY dogID) DogBreed \
             ON Dog.dogID = DogBreed.dogID LEFT JOIN (SELECT Adoption.dog, Adoption.adoption_date FROM Adoption) DogAdoption ON Dog.dogID = DogAdoption.dog \
             WHERE DogAdoption.adoption_date IS NULL ORDER BY Dog.surrender_date ASC) AS joy WHERE joy.adoptability_status = 'AVAILABLE' ORDER BY joy.surrender_date;"
    cursor.execute(query)
    query_result = cursor.fetchall()

    # count how many dog
    query2 = "SELECT Dog.name, DogBreed.breed, Dog.sex, Dog.alteration, Dog.age, DogAdoption.adoption_date, Dog.dogID, Dog.surrender_date, \
             CASE WHEN Dog.alteration = 1 AND Dog.microchipID IS NOT NULL THEN 'AVAILABLE' ELSE 'NOT AVAILABLE' END AS adoptability_status \
             FROM Dog LEFT JOIN (SELECT DISTINCT dogID, GROUP_CONCAT(DISTINCT breed ORDER BY dogID SEPARATOR '/') AS breed \
             FROM BelongTo GROUP BY dogID) DogBreed ON Dog.dogID = DogBreed.dogID \
             LEFT JOIN (SELECT Adoption.dog, Adoption.adoption_date FROM Adoption) DogAdoption \
             ON Dog.dogID = DogAdoption.dog WHERE DogAdoption.adoption_date IS NULL ORDER BY Dog.surrender_date ASC;"
    cursor.execute(query2)
    all_available_dog = cursor.fetchall()
    total_dog = len(all_available_dog)
    return query_result, total_dog


def getAdoptionApplicationReview(cursor):
    query = """select Adopter.email, Adopter.cell_phone, Adopter.first_name, Adopter.last_name,AdoptionApplication.co_applicant_first_name,AdoptionApplication.co_applicant_last_name,Adopter.zip_code, AdoptionApplication.application_num, AdoptionApplication.date, AdoptionApplication.status FROM AdoptionApplication, ADOPTER WHERE AdoptionApplication.status = "pending approval" AND Adopter.email = AdoptionApplication.adopter ORDER BY AdoptionApplication.application_num DESC;
            """
    cursor.execute(query)
    query_result = cursor.fetchall()
    return query_result


def addExpense(cursor, data_params, dog_id):
    """Add expense information into the database"""
    # the date of the expense
    date = data_params['date']
    # the name f the vendor
    vendor = data_params['vendor']
    # the amount of the expense
    amount = data_params['amount']
    # an optional description of the expense
    description = data_params['description']
    # dog_id
    # execute the query
    query = f"INSERT INTO Expense VALUES ('{dog_id}', '{date}', '{amount}', '{vendor}', '{description}');"
    cursor.execute(query)

def getDogDetailsExpectExpense(cursor, dog_id):
    """Extract detailed information from database (expect expense)"""
    query = f"SELECT Dog.NAME, DogBreed.breed, Dog.sex, Dog.alteration, Dog.age, Dog.description, Dog.microchipID, Dog.surrender_date, Dog.surrender_reason, " \
            f"Dog.surrender_by_animal_control FROM Dog LEFT JOIN ( SELECT DISTINCT dogID, GROUP_CONCAT( DISTINCT breed ORDER BY dogID SEPARATOR '/' ) AS breed " \
            f"FROM BelongTo GROUP BY dogID ) DogBreed ON Dog.dogID = DogBreed.dogID " \
            f"WHERE Dog.dogID = {dog_id} ORDER BY Dog.surrender_date ASC;"
    cursor.execute(query)
    query_result = cursor.fetchall()
    return query_result


def getDogDetailsExpense(cursor, dog_id):
    """Extract information related to expense from database"""
    query = f"SELECT dogID, date, vendor, amount, optional_description FROM Expense WHERE dogID = {dog_id} ORDER BY dogID;"
    cursor.execute(query)
    query_result = cursor.fetchall()
    return query_result


def getDogDetailsTotalExpense(cursor, dog_id):
    """Calculate total expense associated with this dog"""
    query = f"SELECT dogID, sum(amount) as total FROM Expense WHERE dogID ={dog_id} GROUP BY dogID ORDER BY dogID;"
    cursor.execute(query)
    query_result = cursor.fetchall()
    # if we don't have any expense record
    if len(query_result) < 1:
        # total expense should be 0
        total_expense = 0
    else:
        total_expense = query_result[0][1]
    return total_expense


def getAdoptionApplicationReviewColumnName():
    return ['email', 'cell_phone', 'first_name', 'last_name', 'co_applicant_first_name', 'co_applicant_last_name',
            'zip_code', 'application_num', 'date', 'status']


def updateAdoptionApplicationReviewStatus(cursor, conn, appl_num, status):
    query = """UPDATE AdoptionApplication SET status= %(status)s WHERE application_num= %(appl_num)s;
            """
    try:
        cursor.execute(query, {'appl_num': int(appl_num), 'status': status})
        conn.commit()
        return True
    except Exception as e:
        print("Problem inserting into db: " + str(e))
        return False
    return False


def insertDog(cursor, conn, input_dog):
    # insert information to dog
    query = (
        "INSERT INTO Dog (dogID,user,name,sex,alteration,description,age,microchipID,surrender_date,surrender_reason,surrender_by_animal_control) "
        "VALUES (%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s)")
    input_dict = (input_dog['dogID'], str(input_dog['userID']), str(input_dog['uname']),
                  str(input_dog['usex']), int(input_dog['ualterationstatus']), str(input_dog['udesc']),
                  int(input_dog['uage']), str(input_dog['umicochipID']), str(input_dog['usurrenderDate']),
                  str(input_dog['usurrenderReason']), int(input_dog['usurrenderbyanimalcontrol']))
    cursor.execute(query, input_dict)
    conn.commit()

    # insert breed information
    for breed in input_dog['breed']:
        query2 = f"INSERT INTO BelongTo VALUES ({input_dog['dogID']}, '{breed}');"
        cursor.execute(query2)
        conn.commit()

def insertAdoptionApplication(cursor, conn, input_appl):
    query = "SELECT email FROM Adopter WHERE email = %(usrname)s"
    cursor.execute(query, {'usrname': str(input_appl['email'])})
    flag = cursor.fetchall()
    #print(flag)
    if not flag:
        query1 = ("INSERT INTO Adopter (email,first_name,last_name,zip_code,state,city,street,cell_phone) "
              "VALUES (%s, %s, %s, %s,%s, %s, %s, %s) ;")
        input_dict1 = (str(input_appl['email']), str(input_appl['firstname']), str(input_appl['lastname']),
                   str(input_appl['zipcode']), str(input_appl['state']), str(input_appl['city']),
                   str(input_appl['street']), str(input_appl['cellphone']))

        cursor.execute(query1, input_dict1)
        conn.commit()

    query2 = (
        "INSERT INTO AdoptionApplication (application_num,adopter,date,status,co_applicant_first_name,co_applicant_last_name) "
        "VALUES (%s, %s, %s, %s,%s, %s) ;")
    input_dict2 = (input_appl['appli_num'], str(input_appl['email']), str(input_appl['date']),
                   str(input_appl['status']), str(input_appl['co_applicant_first_name']),
                   str(input_appl['co_applicant_last_name']))

    cursor.execute(query2, input_dict2)
    conn.commit()

def getApplicationNuminDB(cursor):
    query = "SELECT max(application_num) from AdoptionApplication"
    cursor.execute(query)
    query_result = cursor.fetchall()
    return query_result


def getDogIDinDB(cursor):
    query = "SELECT max(dogID) from Dog"
    cursor.execute(query)
    query_result = cursor.fetchall()
    return query_result


def updateDogBreed(cursor, data_params, dog_id):
    """Update the breed info for specific dog"""
    # extract values from data_params
    # here updated_breed is a list
    updated_breed = data_params['updated_breed']
    # first, remove the original breed information
    query1 = f"DELETE FROM BelongTo WHERE dogID = {dog_id};"
    cursor.execute(query1)
    # then update the breed information
    for breed in updated_breed:
        query2 = f"INSERT INTO BelongTo VALUES ({dog_id}, '{breed}');"
        cursor.execute(query2)


def updateDogSex(cursor, data_params, dog_id):
    """Update the sex info for specific dog"""
    # extract values from data_params
    updated_sex = data_params['updated_sex']
    # execute the query
    query = f"UPDATE Dog SET sex = '{updated_sex}' WHERE dogID = {dog_id};"
    cursor.execute(query)


def updateDogAlteration(cursor, data_params, dog_id):
    """Update the alteration status for specific dog"""
    # extract values from data_params
    updated_alteration = data_params['updated_alteration']
    # execute the query
    query = f"UPDATE Dog SET alteration = {updated_alteration} WHERE dogID = {dog_id};"
    cursor.execute(query)


def updateDogMicrochip(cursor, data_params, dog_id):
    """Update the Microchip ID for specific dog"""
    # extract values from data_params
    updated_microchip = data_params['updated_microchip']
    # execute the query
    query = f"UPDATE Dog SET microchipID = {updated_microchip} WHERE dogID = {dog_id};"
    cursor.execute(query)


def adoptionSearch(cursor, search):
    # search = data_params['search']
    """Return the result based on Mo's search input"""
    lower_search = search.lower()
    query = f"SELECT DISTINCT Adopter.email, AdoptionApplication.application_num, AdoptionApplication.date, " \
            f"AdoptionApplication.co_applicant_first_name, AdoptionApplication.co_applicant_last_name, " \
            f"Adopter.first_name, Adopter.last_name, Adopter.state, Adopter.city, Adopter.street, Adopter.zip_code, Adopter.cell_phone " \
            f"FROM AdoptionApplication LEFT JOIN Adopter ON AdoptionApplication.adopter = Adopter.email " \
            f"WHERE AdoptionApplication.STATUS = 'approved' AND (LOWER( Adopter.last_name ) LIKE '%{lower_search}%' OR LOWER( AdoptionApplication.co_applicant_last_name ) LIKE '%{lower_search}%');"
    cursor.execute(query)
    query_result = cursor.fetchall()
    return query_result


def adoptionSearchSelect(cursor, email):
    """If Mo select this adopter based on email, this function returns its most recent adoption application"""
    query = f"SELECT application_num, MAX(date) FROM AdoptionApplication WHERE adopter = '{email}' GROUP BY application_num;"
    cursor.execute(query)
    query_result = cursor.fetchall()
    return query_result


def calculate_adoption_fee(cursor, dog_id):
    """Calculate the adoption fee"""
    query = f"SELECT Dog.dogID, IF (Dog.surrender_by_animal_control = 1, 0.15 * sum( Expense.amount ), 1.15 * sum( Expense.amount )) " \
            f"FROM Dog LEFT JOIN Expense ON Dog.dogID = Expense.dogID LEFT JOIN Adoption ON Adoption.dog = Dog.dogID " \
            f"WHERE Dog.dogID = {dog_id};"
    cursor.execute(query)
    query_result = cursor.fetchall()
    return query_result


def submitAdoption2db(cursor, dog_id, adoption_fee, adoption_date, application_num):
    """After Mo approves the adoption, the adoption details is recorded into db"""
    query = f"INSERT INTO Adoption VALUES ({application_num}, {dog_id}, {adoption_fee}, '{adoption_date}');"
    cursor.execute(query)


def check_surrender_date(cursor, dog_id):
    """Check the surrender date for dog"""
    query = f"select surrender_date from Dog where Dog.dogID = {dog_id};"
    cursor.execute(query)
    query_result = cursor.fetchall()
    return query_result[0][0]


def getAnimalControlReport(cursor):
    query = """
    WITH srd AS
   (    SELECT  YEAR(surrender_date) as surrender_year 
				, MONTH(surrender_date) as surrender_month
				, COUNT(distinct dogID) as num_surrendered
        FROM Dog
        WHERE surrender_date BETWEEN
            DATE_SUB(DATE_SUB(CURDATE(), INTERVAL DAY(CURDATE()) - 1 DAY) , INTERVAL 6 Month)
            AND curdate()
            AND surrender_by_animal_control = 1
        GROUP BY YEAR(surrender_date), MONTH(surrender_date)
        ORDER BY YEAR(surrender_date) DESC, MONTH(surrender_date) DESC),

        adpt AS
        (  SELECT YEAR(adoption_date) as adoption_year
			, MONTH(adoption_date) as adoption_month
            , COUNT(distinct dogID) as num_adopted
        FROM Dog a, Adoption b
        WHERE a.dogID = b.dog
			AND adoption_date BETWEEN
            DATE_SUB(DATE_SUB(CURDATE(), INTERVAL DAY(CURDATE()) - 1 DAY) , INTERVAL 6 Month)
            AND curdate()
            AND surrender_by_animal_control = 1
        GROUP BY YEAR(adoption_date), MONTH(adoption_date)
        ORDER BY YEAR(adoption_date) DESC, MONTH(adoption_date) DESC
        ),

        exps AS
        (SELECT YEAR(adoption_date) as adoption_year
			, MONTH(adoption_date) as adoption_month
			, SUM(amount) as total_expense
        FROM Dog a, Adoption b, Expense c
        WHERE a.dogID = b.dog and b.dog = c.dogID
            AND adoption_date BETWEEN DATE_SUB(DATE_SUB(CURDATE(), INTERVAL DAY(CURDATE()) - 1 DAY) , INTERVAL 6 Month)
            AND curdate()
            AND DATEDIFF(adoption_date,surrender_date) >=60
        GROUP BY YEAR(adoption_date), MONTH(adoption_date)
        ORDER BY YEAR(adoption_date) DESC, MONTH(adoption_date) DESC
                ),

        		long_stay AS
        (SELECT YEAR(adoption_date) as adoption_year
        , MONTH(adoption_date) as adoption_month
        , COUNT(distinct a.dogID) as num_adopted
        FROM Dog a, Adoption b
        WHERE a.dogID = b.dog 
            AND adoption_date BETWEEN
            DATE_SUB(DATE_SUB(CURDATE(), INTERVAL DAY(CURDATE()) - 1 DAY) , INTERVAL 6 Month)
            AND
            curdate()
            AND DATEDIFF(adoption_date, surrender_date) >= 60
        GROUP BY YEAR(adoption_date), MONTH(adoption_date)
        ORDER BY YEAR(adoption_date) DESC, MONTH(adoption_date) DESC

            ),

                gen_date AS

        (SELECT DISTINCT YEAR(a.Date) as g_year, MONTH(a.Date) as g_month
        FROM (
            select curdate() - INTERVAL (a.a + (10 * b.a) + (100 * c.a) + (1000 * d.a) ) DAY as Date
            from (select 0 as a union all select 1 union all select 2 union all select 3 union all select 4 union all select 5 union all select 6 union all select 7 union all select 8 union all select 9) as a
            cross join (select 0 as a union all select 1 union all select 2 union all select 3 union all select 4 union all select 5 union all select 6 union all select 7 union all select 8 union all select 9) as b
            cross join (select 0 as a union all select 1 union all select 2 union all select 3 union all select 4 union all select 5 union all select 6 union all select 7 union all select 8 union all select 9) as c
            cross join (select 0 as a union all select 1 union all select 2 union all select 3 union all select 4 union all select 5 union all select 6 union all select 7 union all select 8 union all select 9) as d
            ) a
            WHERE a.Date between DATE_SUB(DATE_SUB(CURDATE(), INTERVAL DAY(CURDATE()) - 1 DAY) , INTERVAL 6 Month) and curdate() 
            )

    SELECT g_year, g_Month 
		, COALESCE(a.num_surrendered,0) AS srd_by_AC
		, COALESCE(b.num_adopted,0) AS srd_by_AC_ADPT
		, COALESCE(c.total_expense,0) AS exps_for_ADPT
		, COALESCE(d.num_adopted,0) AS long_stay
    FROM
    	gen_date         
		LEFT JOIN    srd a
			ON a.surrender_year = g_year AND a.surrender_month = g_month
        LEFT JOIN adpt b
			ON  g_month = b.adoption_month AND g_year = b.adoption_year
        LEFT JOIN exps c
			ON  g_month = c.adoption_month AND g_year = c.adoption_year
        LEFT JOIN long_stay d
			ON g_month = d.adoption_month AND g_year = d.adoption_year
    ORDER BY g_year DESC , g_month DESC;

       """
    cursor.execute(query)
    query_result = cursor.fetchall()
    return query_result


def getDrilldownReport(cursor, rpt_type=0, year=2020, month=4):
    query_Adpt = """
    SELECT a.dogID, b.breed, sex, alteration, microchipID, surrender_date,
        (CASE WHEN DATEDIFF(adoption_date, surrender_date) >= 60 THEN DATEDIFF(adoption_date, surrender_date)
             ELSE NULL END) AS days_in_the_stay
    FROM Dog a
        LEFT JOIN (
            SELECT dogID,
                GROUP_CONCAT(DISTINCT breed ORDER BY breed SEPARATOR '/') as breed
            FROM BelongTo
            GROUP BY dogID
            ) AS b
        ON a.dogID = b.dogID
        LEFT JOIN Adoption c
        ON a.dogID = c.dog
    WHERE DATEDIFF(adoption_date, surrender_date) >= 60
        AND YEAR(adoption_date) = %(year)s
        AND MONTH(adoption_date) = %(month)s
    ORDER BY days_in_the_stay DESC, dogID DESC;
    """

    query_Srd = """
    SELECT a.dogID, b.breed, sex, alteration, microchipID, surrender_date
    FROM Dog a
        LEFT JOIN (
            SELECT dogID,
                GROUP_CONCAT(DISTINCT breed ORDER BY breed SEPARATOR '/') as breed
            FROM BelongTo
            GROUP BY dogID
            ) AS b
        ON a.dogID = b.dogID
        LEFT JOIN Adoption c
        ON a.dogID = c.dog
    WHERE surrender_by_animal_control
        AND YEAR(surrender_date) = %(year)s
        AND MONTH(surrender_date) = %(month)s
    ORDER BY a.dogID;
    """
    if rpt_type:
        cursor.execute(query_Adpt, {"year": year, "month": month})

    else:
        cursor.execute(query_Srd, {"year": year, "month": month})
    query_result = cursor.fetchall()
    return query_result


def getMonthlyAdoptionReport(cursor):
    query = """
     With
        srd AS
    (
        SELECT DISTINCT
            YEAR(a.surrender_date) AS year,
            MONTH(a.surrender_date) AS month,
            b.breed, COUNT(Distinct a.dogID) AS num_Surrendered
        FROM Dog a,
            (SELECT DISTINCT dogID, GROUP_CONCAT(breed ORDER BY breed SEPARATOR '/') AS breed
             FROM BelongTo
        GROUP BY dogID) AS b
        WHERE a.dogID = b.dogID
            AND
            a.surrender_date
            BETWEEN
            DATE_SUB(DATE_SUB(CURDATE(), INTERVAL DAY(CURDATE()) - 1 DAY), INTERVAL 12 Month)
            AND
            DATE_SUB(CURDATE(), INTERVAL DAY(CURDATE()) DAY)
        GROUP BY YEAR(a.surrender_date), MONTH(a.surrender_date), b.breed
        ORDER BY YEAR(a.surrender_date), MONTH(a.surrender_date), b.breed
    ),
    adp AS
    (
         SELECT DISTINCT
             YEAR(c.adoption_date) AS year,
             MONTH(c.adoption_date) AS month,
             b.breed,
             COUNT(Distinct a.dogID) as num_adopted,
             SUM(adoption_fee) as total_adoption_fee,
             SUM(CASE WHEN surrender_by_animal_control = 1 THEN adoption_fee/.15*1.15
                     ELSE adoption_fee END) AS adj_revenue
             FROM Dog a,
             (SELECT DISTINCT dogID, GROUP_CONCAT(DISTINCT breed ORDER BY dogID SEPARATOR '/') AS breed
                  FROM BelongTo
                  GROUP BY dogID) AS b,
             Adoption c
        WHERE a.dogID = b.dogID
            AND a.dogID = c.dog
            AND (c.adoption_date
                 BETWEEN
                 DATE_SUB(DATE_SUB(CURDATE(), INTERVAL DAY(CURDATE()) - 1 DAY), INTERVAL 12 Month)
            AND
                DATE_SUB(CURDATE(), INTERVAL DAY(CURDATE()) DAY) )
        GROUP BY YEAR(c.adoption_date), MONTH(c.adoption_date), b.breed
        ORDER BY YEAR(c.adoption_date), MONTH(c.adoption_date), b.breed),
    
    adp_exp AS
    (
        SELECT DISTINCT
            YEAR(c.adoption_date ) as YEAR,
            MONTH(c.adoption_date) as MONTH,
            b.breed,
            SUM(amount) as total_expense
        FROM Dog a,
            (SELECT DISTINCT dogID, GROUP_CONCAT(breed ORDER BY breed SEPARATOR '/') AS breed
                 FROM BelongTo
                 GROUP BY dogID) AS b,
            Adoption AS c ,
            Expense AS d
        WHERE a.dogID = b.dogID
            AND a.dogID = c.dog
            AND a.dogID = d.dogID
            AND c.adoption_date
            BETWEEN
            DATE_SUB(DATE_SUB(CURDATE(), INTERVAL DAY(CURDATE()) - 1 DAY), INTERVAL 12 Month)
                AND
            DATE_SUB(CURDATE(), INTERVAL DAY(CURDATE()) DAY)
        GROUP BY YEAR(c.adoption_date), MONTH(c.adoption_date), b.breed
        ORDER BY YEAR(c.adoption_date), MONTH(c.adoption_date), b.breed)
    

        SELECT COALESCE(srd.year,adp.year) as Year
        , COALESCE(srd.month,adp.month) as Month
        , COALESCE (srd.breed, adp.breed) as breed
        , COALESCE(num_surrendered,0) as num_surrendered
        , COALESCE(num_adopted,0) as num_adopted
        , ROUND(COALESCE(total_expense,0),2) as total_expense
        , ROUND(COALESCE(total_adoption_fee,0),2) as total_adoption_fee
        , ROUND(COALESCE(adj_revenue - total_expense,0),2) AS net_profit
    FROM srd
    LEFT JOIN adp ON srd.month = adp.month and srd.year = adp.year and srd.breed = adp.breed
    LEFT JOIN adp_exp ON adp.month = adp_exp.month and adp.year = adp_exp.year and adp.breed = adp_exp.breed
    
    UNION
    
    SELECT COALESCE(srd.year,adp.year) as YEAR
		, COALESCE(srd.month,adp.month) as MONTH
        , COALESCE (srd.breed, adp.breed) as breed
        , COALESCE(num_surrendered,0) as num_surrendered
        , COALESCE(num_adopted,0) as num_adopted
        , ROUND(COALESCE(total_expense,0),2) as total_expense
        , ROUND(COALESCE(total_adoption_fee,0),2) as total_adoption_fee
        , ROUND(COALESCE(adj_revenue - total_expense,0),2) AS net_profit
    FROM adp
    LEFT JOIN srd ON srd.month = adp.month and srd.year = adp.year and srd.breed = adp.breed
    LEFT JOIN adp_exp ON adp.month = adp_exp.month and adp.year = adp_exp.year and adp.breed = adp_exp.breed;    
    """
    cursor.execute(query)
    query_result = cursor.fetchall()
    return query_result


def getExpenseAnalysis(cursor):
    query = """
    SELECT vendor, sum(amount) AS total_amount
    FROM Expense
    GROUP BY vendor
    ORDER BY total_amount DESC;
    """
    cursor.execute(query)
    query_result = cursor.fetchall()
    return query_result


def getVolunteerLookup(cursor, input_name):
    query = """SELECT first_name, last_name, cell_phone, email
            FROM user
            WHERE first_name LIKE %(UserInput)s OR last_name LIKE %(UserInput)s
            ORDER BY last_name, first_name"""
    cursor.execute(query, {'UserInput': '%' + str(input_name) + '%'})
    result = cursor.fetchall()
    return result


def volunteerColumns():
    return ['First Name', 'Last Name', 'Cell Phone', 'Email']

def getDogName(cursor, dog_id):
    """Get the dog name"""
    query = f"select Dog.name from Dog where Dog.dogID = {dog_id};"
    cursor.execute(query)
    query_result = cursor.fetchall()
    return query_result

def checkUniqueMicrochip(cursor, microchip):
    """Check if the microchip ID is unique"""
    query = f"select * from Dog where Dog.microchipID = '{microchip}';"
    cursor.execute(query)
    query_result = cursor.fetchall()
    return query_result
