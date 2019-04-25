

from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort
import requests
import os
import argparse
import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb
import numpy as np
import random
import getpass
import smtplib
import datetime

SSN_LEN = 9

app = Flask(__name__)

arff_file = None
unsafe_mode = False
rtc_mode = False
activity_mode_malicious = False

# NOTE: To run this program you need a mysql database setup and email
# account that both have the same email
company_db = "CS880"
company_email = "cs880spr2019@gmail.com"
company_pw = ''

 
@app.route('/')
def home():
    #TODO: get this to work (actual log in)
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        #return "Welcome to the system!"
        print("---Logged in!")
        return render_template("logged_in.html")
    print("---Home Page")
    #return render_template('login.html')
    return render_template('flogin.html')
 

 
@app.route('/login', methods=['POST'])
def attempt_login():
    global unsafe_mode
    global rc_mode
    global activity_mode_malicious
    global company_db
    global company_email
    global company_pw

    user_name = request.form['username']
    password = request.form['password']
    print("---Attempting login with username", user_name, " - password:", password)
    
    db = MySQLdb.connect("localhost", "root", company_pw, company_db)
    curs = db.cursor()
    
    # First check to see if user name is in database
    query = ('SELECT * from usr where usr.username=\'' + user_name + '\'')
    numrows = curs.execute(query)
    
    ground_truth = "'SAFE'"
    if activity_mode_malicious:
        ground_truth = "'MALICIOUS'"
    
    if numrows == 0:
        print("Username \"" + user_name + "\" does not exist in the database.")
        """ report normal behavior """
        new_line = "0 'no' 9 " + ground_truth
        if arff_file:
            arff_file.write(new_line + '\n')
        if rtc_mode:
            os.system('mvn exec:java -Dexec.mainClass=com.scoresman.App -Dexec.args="runtimeClassification ' + new_line + '"')
            f = open('cur_runtime_classification.txt', 'r')
            first_line = f.readline()
            f.close()
            os.system('rm cur_runtime_classification.txt')
            return render_template('login.html', message='Username "' + user_name + '" not found.', classification=first_line) 
        return render_template('login.html', message='Username "' + user_name + '" not found.') 
    
    contains_semi = False
    failed_login = False
    
    if not unsafe_mode:
        #--Look for malicious behavior--------------------------------------
        # If the user has tried to log in unsuccessfuly >= 5 times, prompt user and increment login attemps 
        query = ('SELECT username from usr where usr.username=\'' + user_name + '\' and usr.login_attempts>=5')       
        numrows = curs.execute(query)
        message = ''
        if numrows > 0:
            print("MALICIOUS? 1")
            failed_login = True
            message = ('User ' + user_name + ' has tried to log in more than 5 times. ' + 
                      'Your account is locked, please contact a system administrator.')
        #check to see if the password contains a semi colon (potential SQL injection attack)
        if ';' in password:
            print("MALICIOUS? 2")
            contains_semi = True
            failed_login = True
            message = ("Potential SQL injection attack (; in password)")
        # if failed login, report (potentially) malicious behavior
        if failed_login:
            query = ('SELECT * from usr where usr.username=\'' + user_name + '\' and usr.administrator=0')
            numrows = curs.execute(query)
            if numrows > 0 and not contains_semi: # if not admin
                query = ('UPDATE usr set login_attempts=usr.login_attempts+1 where usr.username=\'' + user_name + '\'') 
                numrows = curs.execute(query)
                db.commit()
            query = ('SELECT login_attempts from usr where usr.username=\'' + user_name + '\'')
            numrows = curs.execute(query)
            row = curs.fetchone()
            semi = "'no'"
            if contains_semi:
                semi = "'yes'"
                
            new_line = str(row[0]) + ' ' + semi + " 9 " + ground_truth
                
            if arff_file:
                
                """ report (potentially) malicious behavior """
                arff_file.write(new_line + '\n')
            
            if rtc_mode:
                os.system('mvn exec:java -Dexec.mainClass=com.scoresman.App -Dexec.args="runtimeClassification ' + new_line + '"')
                f = open('cur_runtime_classification.txt', 'r')
                first_line = f.readline()
                f.close()
                os.system('rm cur_runtime_classification.txt')
                return render_template('login.html', message=message, classification=first_line)
            
            return render_template('login.html', message=message) 
        
    query = ('SELECT * from usr where usr.username=\'' + user_name +
            '\' and usr.pwd=\'' + password + '\'')
    numrows = curs.execute(query)
    
    # if incorrect password, prompt user and increment login attemps 
    if numrows < 1:
        if not unsafe_mode:
            # Increment the users number of login attempts in the database
            query = ('SELECT * from usr where usr.username=\'' + user_name + '\' and usr.administrator=0')
            numrows = curs.execute(query)
            if numrows > 0: # if not admin
                query = ('UPDATE usr set login_attempts=usr.login_attempts+1 where usr.username=\'' + user_name + '\'') 
                numrows = curs.execute(query)
                db.commit()
        flash('wrong password!')
        print('---Incorrect password.')
        query = ('SELECT login_attempts from usr where usr.username=\'' + user_name + '\'')
        numrows = curs.execute(query)
        row = curs.fetchone()
        if arff_file:
            new_line = str(row[0]) + " 'no' 9 " + ground_truth 
            """ report normal behavior """
            arff_file.write(new_line + '\n')
        message = 'Incorrect password for user ' + user_name
        return render_template('login.html', message=message) 
    # TODO: add these when everything is working???
    #curs.close()
    session['logged_in'] = True
    query = ('SELECT login_attempts from usr where usr.username=\'' + user_name + '\'')
    numrows = curs.execute(query)
    row = curs.fetchone()
    if arff_file:
        new_line = str(row[0]) + " 'no' 9 " + ground_truth
        """ report normal behavior """
        arff_file.write(new_line + '\n')
    return home()
    
    
@app.route('/retrieve_login', methods=['POST'])
def retrieve_login():
    print("---Retrieve login page")
    if request.form['retrieve_login_button'] == 'Retrieve login info':
        return render_template('retrieve_login.html')
    return home()
    

@app.route('/ssn_retrieval', methods=['POST'])
def ssn_retrieval():
    global unsafe_mode
    global activity_mode_malicious
    global company_db
    global company_email
    global company_pw

    ssn = request.form['ssn']
    print("--Attempting login retrieval with SSN \"" + ssn + '"')
    
    invalid_ssn = False
    try:
        int(ssn)
    except ValueError:
        invalid_ssn = True
    #NOTE: this test would prevent the buffer overflow attack...
    #if len(ssn) != 9:
        #invalid_ssn = True
        
    if invalid_ssn:
        message = "\"" + ssn + "\" is an invalid SSN"
        print("---" + message)
        return render_template('retrieve_login.html', message=message)
    
    ground_truth = "'SAFE'"
    if activity_mode_malicious:
        ground_truth = "'MALICIOUS'"
    
    db = MySQLdb.connect("localhost", "root", company_pw, company_db)
    curs = db.cursor()

    #TODO: get email from the C program (if time) 
    # The buffer overflow attack would happen here
    #os.system("gcc retrieve_email.c -o rem");
    #os.system("./rem " + ssn);
    
    # NOTE: a safe program would just do this...
    # FOR NOW just use this and detect the potential buffer overflow attack above
    query = ('SELECT usr.email from usr where usr.ssn=' + ssn)
    numrows = curs.execute(query)
    if numrows == 0:
        message = "SSN " + ssn + " was not found in the database"
        print("---" + message) 
        new_line = "0 'no' " + str(len(ssn)) + ' ' + ground_truth
        if arff_file:
            """ report (potentially) malicious behavior """
            if not unsafe_mode:
                if len(ssn) > SSN_LEN:
                    print("MALICIOUS? 3")
            arff_file.write(new_line + '\n')
        if rtc_mode:
            os.system('mvn exec:java -Dexec.mainClass=com.scoresman.App -Dexec.args="runtimeClassification ' + new_line + '"')
            f = open('cur_runtime_classification.txt', 'r')
            first_line = f.readline()
            f.close()
            os.system('rm cur_runtime_classification.txt')
            return render_template('retrieve_login.html', message=message, classification=first_line)
        return render_template('retrieve_login.html', message=message) 
    row = curs.fetchone()
    email = row[0]
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    try:
        server.login(company_email, company_pw)
        logged_in = True
    except smtplib.SMTPAuthenticationError:
        print("ERROR: should have worked (company password = db password)")
    server.login(company_email, company_pw)
    print("   successfully logged in to company email ", company_email)
    #Send the mail
    msg = "Here is a link to reset your password..."
    server.sendmail(company_email, email, msg)
    if arff_file: 
        new_line = "0 'no' " + str(len(ssn)) + ' ' + ground_truth
        """ report normal behavior """ 
        arff_file.write(new_line + '\n')
    message = "A link to reset your password has been sent to your email " + email + '.'
    print("---" + message) 
    return render_template('login.html', message=message) 


#safe_or_malicious_mode
@app.route('/safe_or_malicious_mode', methods=['POST'])
def safe_or_malicious_mode():
    ''' '''
    global activity_mode_malicious
    if request.form['safe_or_malicious'] == "safe":
        activity_mode_malicious = False
    else:
        activity_mode_malicious = True
    print("---activity mode malicious = " + str(activity_mode_malicious))
    return home()
    
    
#run_weka
@app.route('/run_weka', methods=['POST'])
def run_weka():
    ''' '''
    test_file = request.form['test_file']
    print("---Running weka with test_file \"" + test_file + "\"")
    os.system('mvn exec:java -Dexec.mainClass=com.scoresman.App -Dexec.args="classifyTestFile ' + test_file + '"')
    #os.system("bash run_weka.sh " + test_file + '.arff')
    return home()
    

@app.route('/logged_in', methods=['POST'])
def logged_in():
    ''' '''
    print("---logging out")
    session['logged_in'] = False
    return home()
    

def create_arff_file(test_file):
    ''' '''
    global arff_file
    if test_file:
        filename = 'arff_files/' + test_file[0] + '.arff'
    else:
        filename = 'arff_files/train.arff'
    arff_file = open(filename, 'w')
    now = datetime.datetime.now()
    header = ('% Date: ' + str(now) + '\n%\n' + 
    '@relation \'safe_or_malicious\'\n' + 
    '@attribute \'n_logins\' numeric\n' +
    '@attribute \'pswd_contains_semi\' {\'yes\',\'no\'}\n' + 
    '@attribute \'ssn_len\' numeric\n' +
    '@attribute \'is_malicious\' {\'MALICIOUS\',\'SAFE\'}\n' +
    '@data\n%\n')
    arff_file.write(header)
    


def get_args(args):
    ''' '''
    # TODO: error check args
    parser = argparse.ArgumentParser()
    parser.add_argument('-host', '--host', default='localhost', type=str)
    parser.add_argument('-port', '--port', default=5000, type=int)
    parser.add_argument('-debug', '--debug', default=False, type=bool)
    parser.add_argument('-um', '--unsafe_mode', action='store_true')
    parser.add_argument('-train_mode', '--train_mode', action='store_true')
    parser.add_argument('-test_mode', '--test_mode', nargs=1)
    parser.add_argument('-rtc_mode', '--run_time_classification_mode', action='store_true')
    return parser.parse_args()
 
 
@app.route('/shutdown', methods=['POST'])
def shutdown():
    global arff_file
    shutdown_server()
    arff_file.close()
    prompt = 'Server shutting down...'
    print("---" + prompt)
    return prompt
    

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
 
 
def main(args):
    global unsafe_mode
    global rtc_mode
    global company_pw
    
    args = get_args(args)
    if not args:
        print("Invalid args.")
        return 1

    logged_in = False
    while not logged_in:
        company_pw = getpass.getpass(prompt='Enter password for company database ' + company_db + ': ', stream=None) 
        # attempt to initialize the python/mysql package
        try:
            db = MySQLdb.connect("localhost", "root", company_pw, company_db)
            curs = db.cursor()
            logged_in = True
        except pymysql.err.OperationalError:
            print("   Error logging in to database. Please try again.")
    
    print("Successfully logged in!")
        
    unsafe_mode = args.unsafe_mode
    if unsafe_mode:
        print("Not Running in safe mode")
    else:
        print("Running in safe mode")
    
    rtc_mode = args.run_time_classification_mode
    if rtc_mode:
        print("Running in run time classification mode")
    
    print("activity mode malicious = " + str(activity_mode_malicious))
    
    if args.train_mode and args.test_mode:
        print("error: train mode AND test mode selected")
        return 1
    
    if args.train_mode or args.test_mode:
        create_arff_file(args.test_mode)
        
    app.secret_key = os.urandom(12)
    app.run(args.host, args.port, args.debug)
    return 0
    
 
if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))
    
