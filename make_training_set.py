#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  make_training_set.py
#  
#  
#  


import os
import time
import requests
from random import *
from threading import Thread



def shutdown():
    ''' '''
    r = requests.post("http://localhost:5000/shutdown", data={})
    


#--safe requests---------------------------------------------------

def valid_login():
    ''' '''
    print("valid_login()")
    # TODO: get random names from database when have time
    # FOR NOW: use one example for each of these functions (to get some data)
    r = randint(1, 3)
    if r == 1:
        r = requests.post("http://localhost:5000/login", data={'username': 'admin', 'password': 'password'})
    elif r == 2:
        r = requests.post("http://localhost:5000/login", data={'username': 'scoresman', 'password': 'pegging4life'})
    else:
        r = requests.post("http://localhost:5000/login", data={'username': 'drremulak', 'password': 'iamdrremulak'})

# NOTE: tsward (administrator) can log in as many times as he wants 
def invalid_login_safe():
    ''' '''
    print("invalid_login_safe()")
    r = requests.post("http://localhost:5000/login", data={'username': 'admin', 'password': 'forgot'})


def retrieve_login_safe():
    ''' '''
    print("retrieve_login_safe()")
    r = requests.post("http://localhost:5000/ssn_retrieval", data={'ssn': 123456789})


def generate_safe_request():
    ''' '''
    r = requests.post("http://localhost:5000/safe_or_malicious_mode", data={'safe_or_malicious': 'safe'})
    r = randint(1, 3)
    if r == 1:
        valid_login();
    elif r == 2:
        invalid_login_safe();
    else:
        retrieve_login_safe();

    
#-----------------------------------------------------------------------
    
#--malicious requests--------------------------------------------------------

def invalid_login_malicious():
    ''' '''
    print("invalid_login_malicious()")
    r = randint(1, 2)
    if r == 1:
        # contains semi
        r = requests.post("http://localhost:5000/login", data={'username': 'ericthemidget', 'password': 'for;got'})
    else:
        r = requests.post("http://localhost:5000/login", data={'username': 'dabadass', 'password': 'forgot'})

def retrieve_login_malicious():
    ''' '''
    print("retrieve_login_malicious()")
    r = requests.post("http://localhost:5000/ssn_retrieval", data={'ssn': 1234567890})
    

def generate_malicious_request():
    ''' '''
    r = requests.post("http://localhost:5000/safe_or_malicious_mode", data={'safe_or_malicious': 'malicious'})
    r = randint(1, 2)
    if r == 1:
        invalid_login_malicious();
    else:
        retrieve_login_malicious();

#-----------------------------------------------------------------------

def make_training_arff_file(training_len):
    ''' '''
    for i in range(0, training_len):
        r = randint(1, 10)
        if r >= 7:
            malicious = True
        else:
            malicious = False
        if malicious:
            generate_malicious_request()
        else:
            generate_safe_request()
    shutdown()
 

def run_flask():
    ''' '''
    os.system("python3 main_app.py -train_mode")


def main(args):
    try:
        training_len = int(sys.argv[1])
    except IndexError:
        training_len = 100
    except ValueError:
        print("Invalid training length parameter:", sys.argv[1])
        return 1
    print("----making training set of length:", training_len, "----")
    # run the flask server
    Thread(target=run_flask, args=()).start()
    # wait for flask to login/get setup
    time.sleep(10)    
    make_training_arff_file(training_len)
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
