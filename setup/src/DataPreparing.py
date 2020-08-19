'''
Created on Jul 10, 2020

@author: lx_ui
'''

import pandas as pd
import numpy as np
import os
import InsertData as id

path = os.path.join(os.getcwd(), 'Demo Data')

dataList = [i for i in os.listdir(path) if i[-3:] == 'tsv']

filePaths = {i[:-4] : os.path.join(path, i) for i in dataList}


dog_orig = pd.read_csv(filePaths['Dog'], sep = '\t', header = 0,dtype={'microchip': str})
user_orig = pd.read_csv(filePaths['Users'], sep = '\t', header = 0, dtype = {'phone': str})
exp_orig = pd.read_csv(filePaths['Expenses'], sep = '\t', header = 0)
adoption_orig = pd.read_csv(filePaths['Adoption'], sep = '\t', header = 0)
app_orig = pd.read_csv(filePaths['Applications'], sep = '\t', header = 0, dtype={'a_phone': str, 'a_postal_code': str})
breed_orig = pd.read_csv(filePaths['Breed'], sep = '\t', header = 0)

#Dog and BelongTo
dog_orig.columns = ['dogID','name','sex','alteration','surrender_by_animal_control',
                    'surrender_date','surrender_reason','description','age',
                    'microchipID','user','breed']


BelongTo = dog_orig[["dogID","breed"]]
Dog = dog_orig.drop("breed",axis = 1).drop_duplicates()



#User and Owner
User = user_orig.drop("Volunteer",axis = 1)
User = User.rename(columns ={"u_f_name":"first_name","u_l_name":"last_name","start_date":"date","phone":"cell_phone"})
Owner = User[User.first_name == "Mo"].email


#AdoptionApplication and Adopter
app_orig.pop("a_email.1")
AdoptionApplication = app_orig[['app_num','app_date','coapp_f_name','coapp_l_name','a_email','is_approved','is_rejected']]
AdoptionApplication.columns = ['application_num','date','co_applicant_first_name','co_applicant_last_name','adopter','is_approved','is_rejected']
check_status = AdoptionApplication['is_rejected'] + AdoptionApplication['is_approved']
check_status.unique() #2 unique levels, 0 and 1

def app_status(row):
    if row.loc['is_approved']:
        return "approved"
    if row.loc['is_rejected']:
        return "rejected"
    return "pending approval"

AdoptionApplication['status'] = AdoptionApplication.apply (lambda row: app_status(row), axis=1)

AdoptionApplication = AdoptionApplication.drop(['is_rejected','is_approved'], axis = 1)

Adopter = app_orig[['a_email','a_f_name','a_l_name','a_street_addr', 'a_city', 'a_state',
       'a_postal_code', 'a_phone']].drop_duplicates()
Adopter.columns = ['email','first_name','last_name','street','city',
                   'state','zip_code','cell_phone']

#Adoption
Adoption = adoption_orig
Adoption.columns = ['dog','application','adoption_date']

#Expense
Expense = exp_orig
Expense.columns = ['dogID','vendor','date','amount','optional_description']


def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)

createFolder('./Cleaned_Data/')

savePath = os.path.join(os.getcwd(), 'Cleaned_Data')
os.chdir(savePath)

# Breed
Breed = breed_orig
Breed.columns = ['breed']
'''
#Write to csv
User.to_csv("User.csv", sep = '\t',index = False,)
Owner.to_csv("Owner2.csv",sep = '\t',index = False)
BelongTo.to_csv("BelongTo.csv",sep = '\t',index = False)
Dog.to_csv("Dog.csv", sep = '\t',index = False, na_rep='')
AdoptionApplication.to_csv("AdoptionApplication.csv", sep = '\t',index = False)
Adopter.to_csv("Adopter.csv",sep = '\t',index = False)
Adoption.to_csv("Adoption.csv",sep = '\t',index = False)
Expense.to_csv("Expense.csv", sep = '\t',index = False)
'''


# Data Insertion
User.to_sql(name = 'user', con = id.engine, if_exists = 'append', index = False)
Owner.to_sql(name = 'owner', con = id.engine, if_exists = 'append', index = False)
Breed.to_sql(name = 'breed', con = id.engine, if_exists = 'append', index = False)
Dog.to_sql(name = 'dog', con = id.engine, if_exists = 'append', index = False)
BelongTo.to_sql(name = 'belongto', con = id.engine, if_exists = 'append', index = False)
Adopter.to_sql(name = 'adopter', con = id.engine, if_exists = 'append', index = False)
AdoptionApplication.to_sql(name = 'adoptionApplication', con = id.engine, if_exists = 'append', index = False)
Expense.to_sql(name = 'expense', con = id.engine, if_exists = 'append', index = False)
Adoption.to_sql(name = 'adoption', con = id.engine, if_exists = 'append', index = False)