import pyodbc 
from pyodbc import Error
import flask 
from flask import request, jsonify
import datetime
import time 
# ---------- SQL connector class ---------- 
class SQLServer:
    def __init__(self, server, db, uid, pwd, dbdriver='ODBC Driver 17 for SQL Server'):
        self.dbdriver='DRIVER={'+dbdriver+'};'
        self.server='SERVER='+server+';'
        self.db='DATABASE='+db+';'
        self.uid='UID='+uid+';'
        self.pwd='PWD='+pwd

    def __enter__(self):
        self.connstr=self.dbdriver+self.server+self.db+self.uid+self.pwd
        self.cnxn=pyodbc.connect(self.connstr)
        self.cursor = self.cnxn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cnxn.close()

# ---------- Server Connection Info ----------
servername_endpoint = 'cot-CIS3365-05.cougarnet.uh.edu'
database = 'CIS3363WU'
username = 'testuser2'
user_password = 'qwerty123'
# Will need to be connected to the UH wifi or using the UH VPN or else error will occur at connection
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server}; dict=true; \
    SERVER='+servername_endpoint+'; \
    DATABASE='+database+'; \
    UID='+username+'; \
    PWD='+user_password
)

# ---------- SQL Connector ----------
def execute_query(connection, query):
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = []
    try:
        cursor.execute(query)
        table = cursor.fetchall()
        columnNames = [column[0] for column in cursor.description]
        for record in table:
            result.append(dict(zip(columnNames, record )))
        return result
    except Error as e:
        print(f"The error '{e}' occurred")

# ---------- Time Token Class ----------
class authentication_token: 
    def __init__(self):
        self.current_token = 0

    def get_time_token_8h(self):
        date = datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=0, minutes=0, hours= 8)
        token = date.timestamp()
        self.current_token = token

    def get_curr_token(self):
        return self.current_token

# ---------- Current User Function ----------
class current_user:
    def __init__(self):
        self.current_user=0

    def set_current_user(self, currentuser):
        self.current_user = currentuser

    def get_current_user(self):
        return self.current_user
        
current_tokens = {} # dict that will store user tokens
# -------------------- Start of API --------------------
app = flask.Flask(__name__) # sets up the application
app.config["DEBUG"] = True # allow to show errors in browser
tokens = authentication_token()
curuser = current_user()

# -------------------- API Default URL --------------------
@app.route('/') 
def startup():
    return "API Is running"

#--------------------------------------------------------------------
#------------------------------- LOGIN ------------------------------
#--------------------------------------------------------------------
@app.route('/api/authenticate', methods=['GET']) # http://127.0.0.1:5000/api/authenticate
def user_authentication(): 
    user_logininfo = request.get_json()
    sql = """
    SELECT * FROM Login_information
    """ 
    logins = execute_read_query(conn, sql) # Fetch reqest for login information from DB
    if 'username' in user_logininfo:         # User Inputs of Username stored to variables / reject if no username provided
        input_username = user_logininfo['username']
    else: 
        return 'No username provided'
    if 'password' in user_logininfo:         # User Input of Password stored to variable / reject if no pass provided
        input_pw = user_logininfo['password']
    else:
        return 'no password provided'
    Username = 0
    userPassword = 0
    for login in logins:
        if input_username == login['username']: # vars to check username and password are assigned  
            Username = login['username']
            userPassword = login['user_password']
    if Username == 0 or userPassword == 0:      # Handle Non-existing users
        return 'Account Could Not Be Found'
    else: 
        if Username == input_username and userPassword == input_pw: # verification on if username and password match in DB
            tokens.get_time_token_8h() # creates an 8 hour token
            token = tokens.get_curr_token() # stores the token in token variable
            current_tokens.update({Username : token})    # stored the token with the username for verification
            curuser.set_current_user(Username)
            return "Successfully Logged in"
    return 'COULD NOT VERIFY!'


#--------------------------------------------------------------------
#------------------------------- LOGIN OUT --------------------------
#--------------------------------------------------------------------
@app.route('/api/logout', methods=['GET']) # http://127.0.0.1:5000/api/logout?username=
def user_deauthentication():
    current_tokens.update({curuser.get_current_user() : 0})
    return "Successfully Logged Out"

# -------------------- API TO GET ANY WHOLE TABLE (READ) -------------------- 
@app.route('/table/all/<table>', methods=['GET']) # http://127.0.0.1:5000/table/all/Business_contacts
def table_all(table):
    try: 
        token = current_tokens[curuser.get_current_user()]
    except:
        return 'No Active User Detected'
    # checks if the time token is still valid/the date on the token has not passed yet
    if float(token) > time.time():
        sql = 'SELECT * FROM %s;' %(table)
        results = execute_read_query(conn, sql)
        return jsonify(results)
    else: 
        return 'Session Timed Out! Please Log Back in'


# --------------------------------------------------------------------
# ------------------- Index/Home/Appointments API --------------------
# --------------------------------------------------------------------
# Index PAGE 
@app.route('/home', methods = ['GET'])
def index_page():
        # token retreived based on username
    try: 
        token = current_tokens[curuser.get_current_user()]
    except:
        return 'No Active User Detected'
    # checks if the time token is still valid/the date on the token has not passed yet
    if float(token) > time.time():
        # main scheduled jobs table
        sql = """
        SELECT Scheduled_Jobs.job_id, Customer.first_name, Customer.last_name, Customer_Contacts.phone, Customer_Contacts.street, Customer_Contacts.city, 
        Customer_Contacts.state_code_id, Customer_Contacts.zipcode, Scheduled_Jobs.app_status, 
        Scheduled_Jobs.app_date, Invoice.invoice_status,
        Employee.last_name as emplname, Employee.first_name as empfname
        FROM Customer
        INNER JOIN Customer_Contacts on Customer_Contacts.customer_id = Customer.customer_id
        INNER JOIN Scheduled_Jobs on Scheduled_Jobs.customer_id = Customer.customer_id
        LEFT JOIN Invoice on invoice.invoice_id = Scheduled_Jobs.invoice_id
        INNER JOIN Employee on Scheduled_Jobs.employee_id = Employee.employee_id
        ORDER BY app_date DESC
        """ 
        sched_join_results = execute_read_query(conn, sql)


        # states drop down
        sql = """
        SELECT * FROM State_code
        """
        states_results = execute_read_query(conn, sql)
        # employee drop down
        sql = """
        SELECT first_name, last_name, employee_id FROM Employee
        """
        employee_names = execute_read_query(conn, sql)
        # Services offered
        sql = """
        SELECT service_id, service_name FROM Services_Offered
        """
        services = execute_read_query(conn, sql)
        # Existing Customer 
        sql = """
        SELECT Customer.customer_id, Customer.first_name, Customer.last_name, Customer_Contacts.street
        FROM customer
        INNER JOIN Customer_Contacts on Customer_Contacts.customer_id = customer.customer_id
        """
        customers = execute_read_query(conn, sql)
        # used to display the update drop down in order
        sql = """
        SELECT Scheduled_Jobs.job_id, Customer.last_name, Customer.first_name
        FROM Scheduled_Jobs
        INNER JOIN Customer on Customer.customer_id = Scheduled_Jobs.customer_id
        """ 
        dropdop_appointment = execute_read_query(conn, sql)
        return jsonify(states_results, sched_join_results, employee_names, services, customers, dropdop_appointment)
    else: 
        return 'Session Timed Out! Please Log Back in'

#  Index Add Appointment with Existing Customer 
@app.route('/home/existing', methods = ['POST'])
def add_appointment_existing_cust():
    try: 
        token = current_tokens[curuser.get_current_user()]
    except:
        return 'No Active User Detected'
    if float(token) > time.time():
        request_data = request.get_json()
        request_data = request_data['data']
        customer_id = request_data['customer_id']          

        quote_service = request_data['services']           
        quote_comment = request_data['quote_comment']   
        quote_total = request_data['quote_total']   

        employee_selected = request_data['employeelist']

        app_status = request_data['app_status']
        app_date = request_data['app_date']
        app_date = app_date + ' ' + request_data['app_time']
    
        # stores quote information 
        sql = """
        INSERT INTO Quote (comments, service_id, total_cost)
        VALUES ('%s','%s', '%s')
        """ %(quote_comment, quote_service, quote_total)
        execute_query(conn, sql)
        # Get quote id to store in invoice table 
        sql = 'SELECT * FROM Quote WHERE quote_id= SCOPE_IDENTITY()' 
        quote_id = execute_read_query(conn, sql)
        quote_id = quote_id[0]["quote_id"]
        # Stores quote id into invoice table 
        sql = "INSERT INTO Invoice (quote_id, invoice_status) VALUES (%s, '%s')" %(quote_id, "Pending")
        execute_query(conn, sql)
        sql = 'SELECT * FROM Invoice WHERE invoice_id= SCOPE_IDENTITY()' 
        invoice_id = execute_read_query(conn, sql)
        invoice_id = invoice_id[0]["invoice_id"]
        sql = "INSERT INTO Scheduled_Jobs (app_status, app_date, customer_id, employee_id, invoice_id) VALUES ('%s', '%s', %s, %s, %s)" % (app_status, app_date, customer_id, employee_selected, invoice_id)
        execute_query(conn, sql)
        return "Added Appointment"
    else: 
        return 'Session Timed Out! Please Log Back in'

#  Index New Appointment with New Customer 
@app.route('/home', methods = ['POST'])
def add_appointment():
    try: 
        token = current_tokens[curuser.get_current_user()]
    except:
        return 'No Active User Detected'
    if float(token) > time.time():
        request_data = request.get_json()
        request_data = request_data['data']
        first_name = request_data['first_name']     
        last_name = request_data['last_name']       

        phone = request_data['phone']               
        email = request_data['email']               
        street = request_data['street']             
        city = request_data['city']                 
        state = request_data['state']              
        zipcode = request_data['zipcode']           

        quote_service = request_data['services']           
        quote_comment = request_data['quote_comment']   
        quote_total = request_data['quote_total']   

        employee_selected = request_data['employeelist']

        app_status = request_data['app_status']
        app_date = request_data['app_date']
        app_date = app_date + ' ' + request_data['app_time']

        # Customer Information 
        sql = """
        INSERT INTO Customer (first_name, last_name) 
        VALUES ('%s', '%s');
        """ %(first_name,last_name)
        execute_query(conn, sql)
        # gets the customer id from the above executioncus
        sql = 'SELECT * FROM Customer WHERE customer_id= SCOPE_IDENTITY()' 
        customer_id = execute_read_query(conn, sql)
        customer_id = customer_id[0]['customer_id']
        # Stores Customer Contacts Information 
        sql = """
        INSERT INTO Customer_Contacts (customer_id, phone, email, street, city, state_code_id, zipcode) 
        VALUES (%s, %s, '%s', '%s','%s', '%s', %s)
        """%(customer_id, phone, email, street, city, state, zipcode)
        execute_query(conn, sql)
        # stores quote information 
        sql = """
        INSERT INTO Quote (comments, service_id, total_cost)
        VALUES ('%s','%s', '%s')
        """ %(quote_comment, quote_service, quote_total)
        execute_query(conn, sql)
        # Get quote id to store in invoice table 
        sql = 'SELECT * FROM Quote WHERE quote_id= SCOPE_IDENTITY()' 
        quote_id = execute_read_query(conn, sql)
        quote_id = quote_id[0]["quote_id"]
        # Stores quote id into invoice table 
        sql = "INSERT INTO Invoice (quote_id, invoice_status) VALUES (%s, '%s')" %(quote_id, "Pending")
        execute_query(conn, sql)
        sql = 'SELECT * FROM Invoice WHERE invoice_id= SCOPE_IDENTITY()' 
        invoice_id = execute_read_query(conn, sql)
        invoice_id = invoice_id[0]["invoice_id"]
        sql = "INSERT INTO Scheduled_Jobs (app_status, app_date, customer_id, employee_id, invoice_id) VALUES ('%s', '%s', %s, %s, %s)" % (app_status, app_date, customer_id, employee_selected, invoice_id)
        execute_query(conn, sql)
        return "Added Appointment"
    else: 
        return 'Session Timed Out! Please Log Back in'

#  HOME PAGE UPDATE APPOINTMENT FORM  
@app.route('/home/form', methods=['POST']) 
def update_appointment_form():
    try: 
        token = current_tokens[curuser.get_current_user()]
    except:
        return 'No Active User Detected'
    # checks if the time token is still valid/the date on the token has not passed yet
    if float(token) > time.time():
        keys = []
        id = request.get_json()
        raw_keys = id.keys()# extract column lables using first entry from table 
        for key in raw_keys: # extract the keys from the table and store it in a string(dict)
            keys.append(key)
        # states drop down
        sql = """
        SELECT * FROM State_code
        """
        states_results = execute_read_query(conn, sql)
        # employee drop down
        sql = """
        SELECT first_name, last_name, employee_id FROM Employee
        """
        employee_names = execute_read_query(conn, sql)
        # Services offered
        sql = """
        SELECT service_id, service_name FROM Services_Offered
        """
        services = execute_read_query(conn, sql)
        sql = """ 
        SELECT Scheduled_Jobs.job_id, Customer.first_name, Customer.last_name, Customer_Contacts.phone, Customer_Contacts.street, Customer_Contacts.city,
        Customer_Contacts.state_code_id, Customer_Contacts.zipcode, Scheduled_Jobs.app_status, 
        Scheduled_Jobs.app_date, Invoice.invoice_status, Customer_Contacts.email, Quote.comments,
        Quote.service_id, Quote.total_cost, Scheduled_Jobs.employee_id, Customer.customer_id, Invoice.invoice_id, Quote.quote_id
        FROM Scheduled_Jobs
        INNER JOIN Customer on Customer.customer_id = Scheduled_Jobs.customer_id
        INNER JOIN Customer_Contacts on Customer_Contacts.customer_id = Customer.customer_id
        FULL OUTER JOIN Invoice on invoice.invoice_id = Scheduled_Jobs.invoice_id 
        FULL OUTER JOIN Quote on Quote.quote_id = Invoice.quote_id   
        WHERE %s = %s;
        """ %(keys[0], id[keys[0]])
        main_results = execute_read_query(conn, sql)
        rawdatetime = main_results[0]["app_date"]
        appoint_date = rawdatetime.strftime("%Y-%m-%d")
        appoint_times = rawdatetime.strftime("%I:%M:%S%p")
        for employee in employee_names:
            if employee["employee_id"] == main_results[0]["employee_id"]:
                current_employee = employee["first_name"] + " " + employee["last_name"]
        return jsonify(states_results, main_results, employee_names, services, appoint_date, appoint_times, current_employee)
    else: 
        return 'Session Timed Out! Please Log Back in'

#  Home Appointment Push Update Process 
@app.route('/home', methods = ['PUT'])
def update_appointment():
    try: 
        token = current_tokens[curuser.get_current_user()]
    except:
        return 'No Active User Detected'
    # checks if the time token is still valid/the date on the token has not passed yet
    if float(token) > time.time():
        request_data = request.get_json()
        customer_id = request_data['customer_id']
        invoice_id = request_data['invoice_id']
        quote_id = request_data['quote_id']
        first_name = request_data['first_name']     
        last_name = request_data['last_name']       

        phone = request_data['phone']               
        email = request_data['email']               
        street = request_data['street']             
        city = request_data['city']                 
        state = request_data['state']               
        zipcode = request_data['zipcode']           

        quote_service = request_data['services']           
        quote_comment = request_data['quote_comment']   
        quote_total = request_data['quote_total']   

        employee_selected = request_data['employeelist']

        app_status = request_data['app_status']
        app_date = request_data['app_date']
        app_date = app_date + ' ' + request_data['app_time']

        # Customer Information 
        sql = """
        UPDATE Customer 
        SET first_name = '%s', last_name = '%s'
        WHERE customer_id = %s
        """ %(first_name,last_name,customer_id)
        execute_query(conn, sql)
        sql = """
        UPDATE Customer_Contacts 
        SET phone = %s, email = '%s', street = '%s', city = '%s', state_code_id = '%s', zipcode = %s
        WHERE customer_id = %s
        """%(phone, email, street, city, state, zipcode,customer_id)
        execute_query(conn, sql)
        # stores quote information 
        sql = """
        UPDATE Quote 
        SET comments = '%s', service_id = '%s', total_cost = '%s'
        WHERE quote_id = %s
        """ %(quote_comment, quote_service, quote_total,quote_id)
        execute_query(conn, sql)
        sql = "UPDATE Scheduled_Jobs  SET app_status='%s', app_date='%s', customer_id=%s, employee_id=%s WHERE invoice_id=%s" % (app_status, app_date, customer_id, employee_selected, invoice_id)
        execute_query(conn, sql)
        return "Added Appointment"
    else: 
        return 'Session Timed Out! Please Log Back in'

#  Home Appointment Push Delete Process 
@app.route('/home', methods = ['DELETE'])
def Delete_appointment():
    try: 
        token = current_tokens[curuser.get_current_user()]
    except:
        return 'No Active User Detected'
    # checks if the time token is still valid/the date on the token has not passed yet
    if float(token) > time.time():
        request_data = request.get_json()
        job_id = request_data['job_id']
        sql = """
        SELECT Scheduled_Jobs.customer_id, Scheduled_Jobs.customer_id, Scheduled_Jobs.deploy_id, Scheduled_Jobs.invoice_id, invoice.quote_id
        FROM Scheduled_Jobs
        FULL OUTER JOIN Invoice on invoice.invoice_id = Scheduled_Jobs.invoice_id    
        WHERE job_id = %s
        """ %(job_id)
        results = execute_read_query(conn, sql)
        results = results[0]
        # Deletes the Related Quote 
        sql = "DELETE FROM Quote WHERE quote_id = %s" % (results['quote_id'])
        execute_query(conn, sql)
        # Deletes the Related Invoice
        sql = "DELETE FROM Invoice WHERE invoice_id = %s"%(results['invoice_id'])
        execute_query(conn, sql)
        sql = "DELETE FROM Scheduled_Jobs WHERE job_id = %s"%(job_id)
        execute_query(conn, sql)
        return "Deleted Appointment %s" %(job_id)
    else: 
        return 'Session Timed Out! Please Log Back in'

# ---------------------------------------------------------------------
# ----------------------------- SERVICE API ---------------------------
# ---------------------------------------------------------------------

# Page is loaded with the use of table/all/Services_offered

# Adds A New Service to the Service Offered Table
@app.route('/services/addservice', methods = ['POST'])
def add_service():
    try: 
        token = current_tokens[curuser.get_current_user()]
    except:
        return 'No Active User Detected'
    # checks if the time token is still valid/the date on the token has not passed yet
    if float(token) > time.time():
        request_data = request.get_json()
        service_name = request_data['service_name']            
        service_description = request_data['service_description']               
        recommended_service_cost = request_data['recommended_service_cost']  

        sql = "INSERT INTO Services_Offered (service_name, service_description, recommended_service_cost) VALUES ('%s', '%s', '%s')" % (service_name, service_description, recommended_service_cost) 
        execute_query(conn, sql)
        return "Added Services"
    else: 
        return 'Session Timed Out! Please Log Back in'

# Loads Information for service update form
@app.route('/services/info', methods = ['POST'])
def service_info():
    try: 
        token = current_tokens[curuser.get_current_user()]
    except:
        return 'No Active User Detected'
    # checks if the time token is still valid/the date on the token has not passed yet
    if float(token) > time.time():
        request_data = request.get_json()
        service_id = request_data['service_id']
        sql = "SELECT * FROM Services_Offered WHERE service_id=%s " %(service_id)
        results = execute_read_query(conn, sql)
        return jsonify(results)
    else: 
        return 'Session Timed Out! Please Log Back in'

# Pushes Updated Information
@app.route('/services/update', methods = ['PUT'])
def update_service():
    try: 
        token = current_tokens[curuser.get_current_user()]
    except:
        return 'No Active User Detected'
    if float(token) > time.time():
        request_data = request.get_json()
        service_id = request_data['service_id']
        service_name = request_data['service_name']            
        service_description = request_data['service_description']               
        recommended_service_cost = request_data['recommended_service_cost']  

        sql = """
        UPDATE Services_Offered 
        SET service_name = '%s' , service_description = '%s' , recommended_service_cost = %s
        WHERE service_id = %s
        """ % (service_name, service_description, recommended_service_cost, service_id) 
        execute_query(conn, sql)
        return "Updated Services"
    else: 
        return 'Session Timed Out! Please Log Back in'

# Deletes a Selected Service
@app.route('/services/delete', methods = ['DELETE'])
def delete_service():
    try: 
        token = current_tokens[curuser.get_current_user()]
    except:
        return 'No Active User Detected'
    if float(token) > time.time():
        request_data = request.get_json()
        service_id = request_data['service_id'] 

        sql = """
        DELETE Services_Offered 
        WHERE service_id = %s
        """ % (service_id) 
        execute_query(conn, sql)
        return "Deleted Service %s" %(service_id)
    else: 
        return 'Session Timed Out! Please Log Back in'

# --------------------------------------------------------------------
# ----------------------------- CUSTOMER API -------------------------
# --------------------------------------------------------------------
# Main Customer Page 
@app.route('/customers/customer_contacts', methods = ['GET'])
def customers():
    try: 
        token = current_tokens[curuser.get_current_user()]
    except:
        return 'No Active User Detected'
    if float(token) > time.time():
        sql = """
        SELECT Customer.customer_id, Customer.first_name, Customer.last_name, Customer_Contacts.phone, Customer_Contacts.email, Customer_Contacts.street, Customer_Contacts.city, Customer_Contacts.state_code_id, Customer_Contacts.zipcode
        FROM Customer
        LEFT JOIN Customer_Contacts ON Customer.customer_id = Customer_Contacts.contact_id
        ORDER BY Customer.last_name
        """
        results = execute_read_query(conn, sql)

        sql = """
        SELECT * FROM State_code
        """
        state_results = execute_read_query(conn, sql)
        sql = "SELECT * FROM Customer"
        customer_id_dropdown = execute_read_query(conn,sql)
        return jsonify(state_results, results, customer_id_dropdown)
    else: 
        return 'Session Timed Out! Please Log Back in'

# Adds a new customer with their incuded contact inforamtion
@app.route('/customer/add', methods = ['POST'])
def add_customer():
    try: 
        token = current_tokens[curuser.get_current_user()]
    except:
        return 'No Active User Detected'
    if float(token) > time.time():
        request_data = request.get_json()
        first_name = request_data['first_name']
        last_name = request_data['last_name']        
        phone = request_data['phone']    
        email = request_data['email']
        street = request_data['street']
        city = request_data['city']   
        state = request_data['state_code_id']     
        zipcode = request_data['zipcode']  
        
        sql = """
        INSERT INTO Customer (first_name, last_name) 
        VALUES ('%s', '%s');
        """ %(first_name,last_name)
        execute_query(conn, sql)
        # gets the customer id from the above execution
        sql = 'SELECT * FROM Customer WHERE customer_id= SCOPE_IDENTITY()' 
        customer_id = execute_read_query(conn, sql)
        customer_id = customer_id[0]['customer_id']
        # Stores Customer Contacts Information 
        sql = """
        INSERT INTO Customer_Contacts (customer_id, phone, email, street, city, state_code_id, zipcode) 
        VALUES (%s, %s, '%s', '%s','%s', '%s', %s)
        """%(customer_id, phone, email, street, city, state, zipcode)
        execute_query(conn, sql)
        
        return "Added Customer"
    else: 
        return 'Session Timed Out! Please Log Back in'

#customer redirect for update
@app.route('/customer/info', methods = ['POST'])
def customer_info():
    try: 
        token = current_tokens[curuser.get_current_user()]
    except:
        return 'No Active User Detected'
    if float(token) > time.time():
        request_data = request.get_json()
        # custoemr first and last name
        customer_id = request_data['customer_id']
        sql = "SELECT * FROM Customer WHERE customer_id = %s" %(customer_id)
        customer_firstlast = execute_read_query(conn, sql)
        sql = "SELECT * FROM Customer_Contacts WHERE customer_id = %s"%(customer_id)
        customer_contact = execute_read_query(conn, sql)
        sql = "SELECT * FROM State_code"
        states = execute_read_query(conn, sql)
        return jsonify(customer_firstlast[0], customer_contact[0], states)
    else: 
        return 'Session Timed Out! Please Log Back in'

#customer update
@app.route('/customer/update', methods = ['PUT'])
def update_customer():
    try: 
        token = current_tokens[curuser.get_current_user()]
    except:
        return 'No Active User Detected'
    if float(token) > time.time():
        request_data = request.get_json()
        customer_id = request_data['customer_id']
        first_name = request_data['first_name']
        last_name = request_data['last_name']        
        phone = request_data['phone']    
        email = request_data['email']
        street = request_data['street']
        city = request_data['city']   
        state = request_data['state_code_id']     
        zipcode = request_data['zipcode']  
        
        sql = """
        UPDATE Customer 
        SET first_name ='%s', last_name = '%s'
        WHERE customer_id = %s
        """ %(first_name,last_name, customer_id)
        execute_query(conn, sql)
        # Stores Customer Contacts Information 
        sql = """
        UPDATE Customer_Contacts 
        SET phone = '%s', email = '%s', street = '%s', city = '%s', state_code_id = '%s', zipcode = %s
        WHERE customer_id = %s  
        """%(phone, email, street, city, state, zipcode, customer_id)
        execute_query(conn, sql)
        return "Updated Customer Information"
    else: 
        return 'Session Timed Out! Please Log Back in'

#delete customer
@app.route('/services/delcustomer', methods = ['DELETE'])
def del_customer():
    try: 
        token = current_tokens[curuser.get_current_user()]
    except:
        return 'No Active User Detected'
    if float(token) > time.time():
        request_data = request.get_json()
        customer_id = request_data['customer_id'] 
        
        sql = "DELETE FROM Customer_Contacts WHERE customer_id = %s" %(customer_id)
        execute_query(conn, sql)
    
        sql = "DELETE FROM Scheduled_Jobs WHERE customer_id = %s" %(customer_id)
        execute_query(conn, sql)

        sql = "DELETE FROM Job_Feedback WHERE customer_id = %s" %(customer_id)
        execute_query(conn, sql)

        sql = "DELETE FROM Customer WHERE customer_id = %s" %(customer_id)
        execute_query(conn, sql)
        
        return "Deleted Customer"
    else: 
        return 'Session Timed Out! Please Log Back in'

# --------------------------------------------------------------------
# ------------------- COMMERCIAL CUSTOMER API ------------------------
# --------------------------------------------------------------------
# Main page of commercial customers
@app.route('/customers/commercial', methods = ['GET'])
def commercial_customers():
    try: 
        token = current_tokens[curuser.get_current_user()]
    except:
        return 'No Active User Detected'
    if float(token) > time.time():
        sql = """
        SELECT * FROM State_code
        """
        state_results = execute_read_query(conn, sql)

        sql= """
        SELECT Commercial_Customers.customer_id, Commercial_Customers.business_name, Commercial_Customers.business_hrs, Business_Contacts.phone, Business_Contacts.email, Business_Contacts.street, Business_Contacts.city, Business_Contacts.state_code_id, Business_Contacts.zipcode
        FROM Commercial_Customers
        INNER JOIN Business_Contacts ON Commercial_Customers.customer_id = Business_Contacts.comm_cust_id
        ORDER BY Commercial_Customers.business_name
        """ 
        commcust_results = execute_read_query(conn, sql)
        sql= "SELECT * FROM Commercial_Customers"
        comcust_id = execute_read_query(conn, sql)
        return jsonify(state_results, commcust_results, comcust_id)
    else: 
        return 'Session Timed Out! Please Log Back in'

# Adds a new commercial customer
@app.route('/customers/commercial/add', methods = ['POST'])
def add_commcustomer():
    try: 
        token = current_tokens[curuser.get_current_user()]
    except:
        return 'No Active User Detected'
    if float(token) > time.time():
        request_data = request.get_json()
        business_name = request_data['business_name']
        business_hrs= request_data['business_hrs']        
        phone = request_data['phone']    
        email = request_data['email']
        street = request_data['street']
        city = request_data['city']   
        state = request_data['state_code_id']     
        zipcode = request_data['zipcode']  
        
        sql = """
        INSERT INTO Commercial_Customers (business_name, business_hrs) 
        VALUES ('%s', '%s');
        """ %(business_name, business_hrs)
        execute_query(conn, sql)
        # gets the customer id from the above execution
        sql = 'SELECT * FROM Commercial_Customers WHERE customer_id= SCOPE_IDENTITY()' 
        comm_cust_id = execute_read_query(conn, sql)
        comm_cust_id = comm_cust_id[0]['customer_id']
        # Stores Customer Contacts Information 
        sql = """
        INSERT INTO Business_Contacts (comm_cust_id, phone, email, street, city, state_code_id, zipcode) 
        VALUES (%s, %s, '%s', '%s','%s', '%s', %s)
        """%(comm_cust_id, phone, email, street, city, state, zipcode)
        execute_query(conn, sql)
        
        return "Added Commercial Customer"
    else: 
        return 'Session Timed Out! Please Log Back in'

@app.route('/customers/commercial/info', methods = ['POST'])
def commcustomer_info():
    try: 
        token = current_tokens[curuser.get_current_user()]
    except:
        return 'No Active User Detected'
    if float(token) > time.time():
        request_data = request.get_json()
        # custoemr first and last name
        comm_cust_id = request_data['customer_id']
        sql = "SELECT * FROM Commercial_Customers WHERE customer_id = %s" %(comm_cust_id)
        commcust_results = execute_read_query(conn, sql)
        sql = "SELECT * FROM Business_Contacts WHERE comm_cust_id = %s"%(comm_cust_id)
        commcust_contact = execute_read_query(conn, sql)
        sql = "SELECT * FROM State_code"
        states = execute_read_query(conn, sql)
        return jsonify(commcust_results[0], commcust_contact[0], states)
    else: 
        return 'Session Timed Out! Please Log Back in'

# Pushes updated information to the database
@app.route('/customers/commercial/update', methods = ['POST'])
def update_commcustomer():
    try: 
        token = current_tokens[curuser.get_current_user()]
    except:
        return 'No Active User Detected'
    if float(token) > time.time():
        request_data = request.get_json()
        comm_cust_id = request_data['customer_id']
        business_name = request_data['business_name']
        business_hrs = request_data['business_hrs']        
        phone = request_data['phone']    
        email = request_data['email']
        street = request_data['street']
        city = request_data['city']   
        states = request_data['state_code_id']     
        zipcode = request_data['zipcode']  
        
        sql = """
        UPDATE Commercial_Customers 
        SET business_name ='%s', business_hrs = '%s'
        WHERE customer_id = %s
        """ %(business_name,business_hrs, comm_cust_id)
        execute_query(conn, sql)
        # Stores Customer Contacts Information 
        sql = """
        UPDATE Business_Contacts 
        SET phone = '%s', email = '%s', street = '%s', city = '%s', state_code_id = '%s', zipcode = %s
        WHERE comm_cust_id = %s  
        """%(phone, email, street, city, states, zipcode, comm_cust_id)
        execute_query(conn, sql)
        return "Updated Commercial Customer Information"
    else: 
        return 'Session Timed Out! Please Log Back in'

# Deletes a commercial customer 
@app.route('/customers/commercial/delete', methods = ['DELETE'])
def del_commcustomer():
    try: 
        token = current_tokens[curuser.get_current_user()]
    except:
        return 'No Active User Detected'
    if float(token) > time.time():
        request_data = request.get_json()
        customer_id = request_data['customer_id'] 
        
        sql = "DELETE FROM Business_Contacts WHERE comm_cust_id = %s" %(customer_id)
        execute_query(conn, sql)
    
        sql = "DELETE FROM Commercial_Customers WHERE customer_id = %s" %(customer_id)
        execute_query(conn, sql)
        
        return "Deleted Commercial Customer"
    else: 
        return 'Session Timed Out! Please Log Back in'

# --------------------------------------------------------------------
# ---------------------------- FEEDBACK API --------------------------
# --------------------------------------------------------------------
# Main Page
@app.route('/feedback', methods = ['GET'])
def feeback():
    try: 
        token = current_tokens[curuser.get_current_user()]
    except:
        return 'No Active User Detected'
    if float(token) > time.time():
        # Form the customers drop down 
        sql = "SELECT * FROM Customer ORDER BY last_name ASC"
        customerlist = execute_read_query(conn, sql)
        # Gets the Table in feedback page from newest to oldest
        sql = """
        SELECT Job_Feedback.feedback_id, Customer.first_name, Customer.last_name, Job_Feedback.customer_comments, Job_Feedback.feedback_date
        FROM Job_Feedback
        INNER JOIN Customer ON Job_Feedback.customer_id = Customer.customer_id
        ORDER BY Job_Feedback.feedback_date DESC
        """
        feedbacklist = execute_read_query(conn, sql)
        # Seperation of the date from feedback_date
        for feedback in feedbacklist:
            rawdatetime = feedback["feedback_date"]
            feedback_date = rawdatetime.strftime("%Y-%m-%d")
            feedback["feedback_date"] = feedback_date
        # Gets the dropdown for feedback ID 
        sql = """
        SELECT Job_Feedback.feedback_id, Customer.first_name, Customer.last_name
        FROM Job_Feedback
        INNER JOIN Customer on Customer.customer_id = Job_Feedback.customer_id
        """ 
        feedback_id = execute_read_query(conn,sql)
        return jsonify(customerlist, feedbacklist, feedback_id)
    else: 
        return 'Session Timed Out! Please Log Back in'

# Add new feedback
@app.route('/feedback/add', methods = ['POST'])
def add_feedback():
    try: 
        token = current_tokens[curuser.get_current_user()]
    except:
        return 'No Active User Detected'
    # checks if the time token is still valid/the date on the token has not passed yet
    if float(token) > time.time():
        request_data = request.get_json()
        customer = request_data['customer']            
        customer_comments = request_data['customer_comments']               
        feedback_date = request_data['feedback_date']  

        sql = "INSERT INTO Job_Feedback (customer_id, customer_comments, feedback_date) VALUES ('%s', '%s', '%s')" % (customer, customer_comments, feedback_date) 
        execute_query(conn, sql)
        return "Added Feedback"
    else: 
        return 'Session Timed Out! Please Log Back in'

# API for feedback update form
@app.route('/feedback/info', methods = ['POST'])
def feedback_info():
    try: 
        token = current_tokens[curuser.get_current_user()]
    except:
        return 'No Active User Detected'
    # checks if the time token is still valid/the date on the token has not passed yet
    if float(token) > time.time():
        request_data = request.get_json()
        feedback_id = request_data['feedback_id']
        sql = "SELECT * FROM Job_Feedback WHERE feedback_id=%s " %(feedback_id)
        results = execute_read_query(conn, sql)
        selected_customer_id = results[0]["customer_id"]
        sql = "SELECT first_name, last_name FROM Customer WHERE customer_id = %s" %(selected_customer_id)
        customer_name = execute_read_query(conn, sql)
        # Seperation of the date from feedback_date
        rawdatetime = results[0]["feedback_date"]
        feedback_date = rawdatetime.strftime("%Y-%m-%d")# Gets the customer names and ids
        sql = "SELECT * FROM Customer"
        customerlist = execute_read_query(conn, sql)
        return jsonify(results, customer_name, feedback_date, customerlist)
    else: 
        return 'Session Timed Out! Please Log Back in'

# Updates information for feedback based on Feedback_id
@app.route('/feedback/update', methods = ['PUT'])
def update_feedback():
    try: 
        token = current_tokens[curuser.get_current_user()]
    except:
        return 'No Active User Detected'
    if float(token) > time.time():
        request_data = request.get_json()
        feedback_id = request_data['feedback_id']
        customer = request_data['customer']            
        customer_comments = request_data['customer_comments']               
        feedback_date = request_data['feedback_date']  

        sql = """
        UPDATE Job_Feedback 
        SET customer_id =%s, customer_comments = '%s', feedback_date= '%s' 
        WHERE feedback_id = %s
        """ % (customer, customer_comments, feedback_date, feedback_id) 
        execute_query(conn, sql)
        return "Updated Feedback"
    else: 
        return 'Session Timed Out! Please Log Back in'

#Delete Feedback
@app.route('/feedback/delete', methods = ['DELETE'])
def del_feedback():
    try: 
        token = current_tokens[curuser.get_current_user()]
    except:
        return 'No Active User Detected'
    if float(token) > time.time():
        request_data = request.get_json()
        feedback_id = request_data['feedback_id'] 
        
        sql = "DELETE FROM Job_Feedback WHERE feedback_id = %s" %(feedback_id)
        execute_query(conn, sql)
    
        return "Deleted Customer Feedback"
    else: 
        return 'Session Timed Out! Please Log Back in'


# --------------------------------------------------------------------
# ------------- TOOL/CHEM/TOOL MAINTAIN/LICENSES API -----------------
# --------------------------------------------------------------------
# Main page 
@app.route('/inventory', methods = ['GET'])
def equip_inventories():
        # token retreived based on username
    try: 
        token = current_tokens[curuser.get_current_user()]
    except:
        return 'No Active User Detected'
    # checks if the time token is still valid/the date on the token has not passed yet
    if float(token) > time.time():
        # Tool Table 

        sql= """
        SELECT equipment_id, equipment_name FROM Tools_Inventory
        """
        equipment_results = execute_read_query(conn, sql)

        sql = """         
        SELECT Tools_Inventory.equipment_id, Tools_Inventory.equipment_name, Tools_Inventory.equipment_type, Tools_Inventory.quality, Supplier.supplier_name 
        FROM Tools_Inventory
        INNER JOIN Supplier ON Tools_Inventory.supplier_id = Supplier.supplier_id
        """ 
        tool_ivt = execute_read_query(conn, sql)

        # Chemical Table
        sql = """
        SELECT Chemical_Inventory.chemical_id, Chemical_Inventory.chemical_Name, Chemical_Inventory.chemcial_type, Licenses_Permits.License_name, Supplier.supplier_name
        FROM Chemical_Inventory
        LEFT JOIN Licenses_Permits ON Chemical_Inventory.license_ID = Licenses_Permits.license_ID
        LEFT JOIN Supplier ON Chemical_Inventory.supplier_id = Supplier.Supplier_id
        """
        chem_ivt = execute_read_query(conn, sql)
        
        # Tool Maint Information
        sql = """                
        SELECT ri.repair_id, ti.equipment_name, ri.repair_status, ri.date_repair_start, ri.repair_comments
        FROM Repair_Information ri
        INNER JOIN Tools_Inventory ti ON ti.repair_id = ri.repair_id       
        """
        tool_maintain_ivt = execute_read_query(conn, sql)
        for row in tool_maintain_ivt:
            for column in row:
                if column == 'date_repair_start':
                    rawdatetime = row["date_repair_start"]
                    formated_date = rawdatetime.strftime("%Y-%m-%d")
                    row["date_repair_start"] = formated_date
        # LICENSES List
        sql = "SELECT License_id, License_name, License_description, License_expiration_date FROM Licenses_Permits"
        licenses = execute_read_query(conn, sql)
        for row in licenses:
            for column in row: 
                if column == 'License_expiration_date':
                    rawdatetime = row["License_expiration_date"]
                    formated_date = rawdatetime.strftime("%Y-%m-%d")
                    row["License_expiration_date"] = formated_date

        
        # Supplier List for drop downs 
        sql = "SELECT * FROM Supplier"
        suppliers = execute_read_query(conn, sql)

        return jsonify(tool_ivt, chem_ivt, tool_maintain_ivt, licenses, equipment_results, suppliers)
    else: 
        return 'Session Timed Out! Please Log Back in'


# ----- Start of Tool Inventory APIs
# Add A New Tool 
@app.route('/inventory/tools/add', methods = ['POST'])
def add_tools():
    request_data = request.get_json()
    equipment_name = request_data['equipment_name']                       
    equipment_type = request_data['equipment_type']
    quality = request_data['quality']
    supplier_id = request_data['supplier_id']

    sql = """
    INSERT INTO Tools_Inventory (equipment_name, equipment_type, quality, supplier_id) 
    VALUES ('%s', '%s', '%s', %s)
    """ % (equipment_name, equipment_type, quality, supplier_id) 
    execute_query(conn, sql)

    return "Added New Tool"

# For the tool update page
@app.route('/inventory/tools/info', methods = ['POST'])
def tools_info():
    request_data = request.get_json()
    # custoemr first and last name
    equipment_id = request_data['equipment_id']

    sql = """
    SELECT t.equipment_id, t.equipment_name, t.equipment_type, t.quality, t.supplier_id, s.supplier_name
    FROM Tools_Inventory t
    INNER JOIN Supplier s ON t.supplier_id = s.supplier_id
    WHERE equipment_id = %s
     """ %(equipment_id)
    equipment_info = execute_read_query(conn, sql)


    sql = "SELECT * FROM Supplier"
    supplier_info = execute_read_query(conn, sql)


    return jsonify(equipment_info, supplier_info)

# Pushes Tool Update
@app.route('/inventory/tools/update', methods = ['PUT'])
def update_tools():
    request_data = request.get_json()
    equipment_id = request_data['equipment_id']
    supplier_id = request_data['supplier_id']
    equipment_name = request_data['equipment_name']
    equipment_type = request_data['equipment_type']
    quality = request_data['quality']
            
    sql = """
    UPDATE Tools_Inventory
    SET equipment_name ='%s', equipment_type = '%s', quality = '%s', supplier_id = %s
    WHERE equipment_id = %s
    """ %(equipment_name, equipment_type, quality, supplier_id, equipment_id)
    execute_query(conn, sql)
    return "Succesfully Updated %s" % (equipment_name)

# Delete A Tools
@app.route('/inventory/tools/delete', methods = ['PUT'])
def del_tools():
    request_data = request.get_json()
    equipment_id = request_data['equipment_id'] 
    
    sql = """
    UPDATE Equipment_Deployment 
    SET equipment_id = null 
    WHERE equipment_id = %s 
    """ % (equipment_id)
    
    execute_query(conn, sql)

    sql = "DELETE FROM Tools_Inventory WHERE equipment_id = %s" % (equipment_id)
    execute_query(conn, sql)

   
    return "Deleted Tool"


# ----- Start of Chemcial Inventory APIs
# Add Chemicals
@app.route('/inventory/chemcials/add', methods = ['POST'])
def add_chemicals():
    request_data = request.get_json()
    chemical_name = request_data['chemical_name']                       
    chemcial_type = request_data['chemcial_type']
    supplier_id = request_data['supplier_id']
    license_id = request_data['license_id']

    sql = """
    INSERT INTO Chemical_Inventory (chemical_Name, chemcial_type, license_ID, supplier_id) 
    VALUES ('%s', '%s', %s, %s)
    """ % (chemical_name, chemcial_type, license_id, supplier_id)
    execute_query(conn, sql)

    return "Added New Chemical"

# For the chemcial update page
@app.route('/inventory/chemical/info', methods = ['POST'])
def chemical_info():
    request_data = request.get_json()
    # Customer first and last name
    chemical_id = request_data['chemical_id']

    # Main sql for data
    sql = """
    SELECT Chemical_Inventory.chemical_Name, Chemical_Inventory.chemcial_type, 
    Licenses_Permits.License_name, Chemical_Inventory.license_ID, 
    Supplier.supplier_name, Chemical_Inventory.supplier_id
    FROM Chemical_Inventory
    LEFT JOIN Licenses_Permits ON Licenses_Permits.License_ID = Chemical_Inventory.license_ID
    LEFT JOIN Supplier on Supplier.supplier_id = Chemical_Inventory.supplier_id
    WHERE chemical_ID = %s
    """ %(chemical_id)
    chemical_info = execute_read_query(conn, sql)

    # Supplier Drop Down 
    sql = "SELECT * FROM Supplier"
    supplier_info = execute_read_query(conn, sql)

    # License Drop Down 
    sql = "SELECT * FROM Licenses_Permits"
    license_info = execute_read_query(conn, sql)

    return jsonify(chemical_info, supplier_info, license_info)

#chemical update
@app.route('/inventory/chemical/update', methods = ['PUT'])
def update_chemical():
    request_data = request.get_json()
    for data in request_data:
        if request_data[data] == '':
            request_data[data] = 'null'
    
    chemical_id = request_data['chemical_id']
    chemical_name = request_data['chemical_name']
    chemcial_type = request_data['chemcial_type']
    supplier_id = request_data['supplier_id']
    license_id = request_data['license_id']
    
            
    sql = """
    UPDATE Chemical_Inventory
    SET chemical_name ='%s', chemcial_type = '%s', license_id = %s, supplier_id = %s
    WHERE chemical_id = %s
    """ %(chemical_name, chemcial_type, license_id, supplier_id, chemical_id)
    execute_query(conn, sql)

    return "Successfully Updated %s" %(chemical_name)

#Delete Chemicals
@app.route('/inventory/chemical/delete', methods = ['PUT'])
def del_chemicals():
    request_data = request.get_json()
    chemical_id = request_data['chemical_id'] 
    
    sql = """
    UPDATE Equipment_Deployment
    SET chemical_id = null
    WHERE chemical_id = %s 
    """ % (chemical_id)
    
    execute_query(conn, sql)

    sql = "DELETE FROM Chemical_Inventory WHERE chemical_id = %s" % (chemical_id)
    execute_query(conn, sql)
   
    return "Deleted the Chemical"


# ----- Start of Tool Maintenance APIs
#Add Repair Information
@app.route('/inventory/repair/add', methods = ['POST'])
def add_addrepairtools():
    request_data = request.get_json()
    equipment = request_data['equipment_list']                         
    repair_status = request_data['repair_status']
    date_repair_start = request_data['date_repair_start']
    repair_comments = request_data['repair_comments']

    sql = "INSERT INTO Repair_Information (repair_status, date_repair_start, repair_comments) VALUES ('%s', '%s', '%s')" % (repair_status, date_repair_start, repair_comments) 
    execute_query(conn, sql)

    sql = 'SELECT * FROM Repair_Information WHERE repair_id = SCOPE_IDENTITY()' 
    repair_id= execute_read_query(conn, sql)
    repair_id = repair_id[0]['repair_id']


    sql = "UPDATE Tools_Inventory SET repair_id = '%s' WHERE equipment_id='%s'" % (repair_id, equipment)
    execute_query(conn, sql)

    return "Added New Maintenance Log "

# For the tool maintenance update page
@app.route('/inventory/repair/info', methods = ['POST'])
def repair_info():
    request_data = request.get_json()
    repair_id = request_data['repair_id']


    sql = "SELECT * FROM Repair_Information WHERE repair_id = %s" % (repair_id)
    repair_info = execute_read_query(conn, sql)
    rawdatetime = repair_info[0]["date_repair_start"]
    appoint_date = rawdatetime.strftime("%Y-%m-%d")

    return jsonify(repair_info[0], appoint_date)

# Pushes chemical update
@app.route('/inventory/repair/update', methods = ['PUT'])
def update_repair():
    request_data = request.get_json()
    repair_id = request_data['repair_id']
    repair_status = request_data['repair_status']
    date_repair_start = request_data['date_repair_start']
    repair_comments = request_data['repair_comments']

    sql = """
    UPDATE Repair_Information
    SET repair_status ='%s', date_repair_start = '%s', repair_comments = '%s'
    WHERE repair_id = %s
    """ %(repair_status, date_repair_start, repair_comments, repair_id)
    execute_query(conn, sql)

    return "Updated Tool Maintenance"

# Delete a repair information 
@app.route('/inventory/repair/delete', methods = ['PUT'])
def del_repair():
    request_data = request.get_json()
    repair_id = request_data['repair_id'] 

    sql = """
    UPDATE Tools_Inventory 
    SET repair_id = null
    WHERE repair_id = %s 
    """ % (repair_id)
    
    execute_query(conn, sql)

    sql = "DELETE FROM Repair_Information WHERE repair_id = %s" % (repair_id)
    execute_query(conn, sql)
   
    return "Deleted the Repair"


# ----- Start of Licenses APIs
# Add new License 
@app.route('/inventory/license/add', methods = ['POST'])
def add_licenses():
    request_data = request.get_json()
    license_name = request_data['license_name']                         
    license_description = request_data['license_description']
    license_expiration_date = request_data['license_expiration_date']


    sql = "INSERT INTO Licenses_Permits (License_name, License_description, License_expiration_date) VALUES ('%s', '%s', '%s')" % (license_name, license_description, license_expiration_date)
    execute_query(conn, sql)

    return "Added License"

# Loads information for update form for licenses
@app.route('/inventory/license/info', methods = ['POST'])
def license_info():
    try: 
        token = current_tokens[curuser.get_current_user()]
    except:
        return 'No Active User Detected'
    # checks if the time token is still valid/the date on the token has not passed yet
    if float(token) > time.time():
        request_data = request.get_json()
        license_id = request_data['license_id']
        
        sql = "SELECT * FROM Licenses_Permits WHERE License_id= %s " %(license_id)
        licenses = execute_read_query(conn, sql)
        for row in licenses:
            for column in row: 
                if column == 'License_expiration_date':
                    rawdatetime = row["License_expiration_date"]
                    formated_date = rawdatetime.strftime("%Y-%m-%d")
                    row["License_expiration_date"] = formated_date
        
        return jsonify(licenses)
    else: 
        return 'Session Timed Out! Please Log Back in'

# Pushes Updated Information of License
@app.route('/inventory/license/update', methods = ['PUT'])
def update_license():
    try: 
        token = current_tokens[curuser.get_current_user()]
    except:
        return 'No Active User Detected'
    if float(token) > time.time():
        request_data = request.get_json()
        license_id = request_data['license_id']
        license_name = request_data['license_name']            
        license_description = request_data['license_description']               
        license_expiration_date = request_data['license_expiration_date']  

        sql = """
        UPDATE Licenses_Permits
        SET license_name = '%s' , license_description = '%s' , license_expiration_date = '%s'
        WHERE license_id = %s
        """ % (license_name, license_description, license_expiration_date, license_id) 
        execute_query(conn, sql)
        return "Updated License"
    else: 
        return 'Session Timed Out! Please Log Back in'

# Deletes a Licnese
@app.route('/inventory/license/delete', methods = ['PUT'])
def del_license():
    request_data = request.get_json()
    license_id = request_data['license_id'] 

    sql = """
    UPDATE Chemical_Inventory 
    SET license_ID = null
    WHERE license_ID = %s 
    """ % (license_id)
    
    execute_query(conn, sql)

    sql = "  = %s" % (license_id)
    execute_query(conn, sql)
   
    return "Deleted the License %s" %(license_id)


#--------------------------------------------------------------------
#-------------------- VEHICLE INVENTORY APIS ------------------------
#--------------------------------------------------------------------
# Vehicle inventory Main Page
@app.route('/inventory/vehicle', methods = ['GET'])
def vehicleivt():
    try: 
        token = current_tokens[curuser.get_current_user()]
    except:
        return 'No Active User Detected'
        # checks if the time token is still valid/the date on the token has not passed yet
    if float(token) > time.time():
        # Vehicle Inventory Table 

        sql= """
            SELECT vehicle_id, vehicle_name FROM Vehicle_Inventory
        """
        car_results = execute_read_query(conn, sql)

        sql = """
        SELECT Vehicle_Inventory.vehicle_id, Vehicle_Inventory.vehicle_name, Vehicle_Inventory.vehicle_vin, 
        Vehicle_Inventory.vehicle_license, Vehicle_Inventory.vehicle_status, 
        Vehicle_Information.vehicle_info_id, Vehicle_Information.insurance_info, Vehicle_Information.next_inspection_date 
        FROM Vehicle_Information
        LEFT JOIN Vehicle_Inventory on Vehicle_Inventory.vehicle_info_id = Vehicle_Information.vehicle_info_id
        """
        vehicleinfo = execute_read_query(conn, sql)
        for row in vehicleinfo:
            rawdatetime = row['next_inspection_date']
            if rawdatetime != None:
                date_processed = rawdatetime.strftime("%Y-%m-%d")
                row['next_inspection_date'] = date_processed
        # Vehicle Maintenance
        sql = """
            SELECT Vehicle_Maintenance.maintenance_id, Employee.first_name, Employee.last_name, Vehicle_Maintenance.service_date, Vehicle_Inventory.vehicle_name, Vehicle_Maintenance.maintenance_comments
            FROM Vehicle_Maintenance
            INNER JOIN Employee ON Employee.employee_id = Vehicle_Maintenance.employee_id
            INNER JOIN Vehicle_Inventory ON Vehicle_Inventory.vehicle_id = Vehicle_Maintenance.vehicle_id
            """
        vehiclemaint = execute_read_query(conn, sql)
        for row in vehiclemaint:
            rawdatetime = row['service_date']
            if rawdatetime != None:
                date_processed = rawdatetime.strftime("%Y-%m-%d")
                row['service_date'] = date_processed
        # Employee Information

        sql = " SELECT employee_id, first_name, last_name FROM Employee"
        emp = execute_read_query(conn, sql)

        sql = "SELECT * FROM Vehicle_Inventory"
        vehicleivt = execute_read_query(conn, sql)

        return jsonify(vehicleinfo, vehiclemaint, emp, car_results, vehicleivt)
    else: 
        return 'Session Timed Out! Please Log Back in'

# ----- Start of Vehicle Inventory APIS
#Add Vehicle
@app.route('/inventory/vehicle/add', methods = ['POST'])
def add_vehicle():
    request_data = request.get_json()
    vehicle_name = request_data['vehicle_name']                         
    vehicle_vin = request_data['vehicle_vin']
    vehicle_license = request_data['vehicle_license']
    vehicle_status = request_data['vehicle_status']
    

    sql = "INSERT INTO Vehicle_Inventory (vehicle_name, vehicle_vin, vehicle_license, vehicle_status) VALUES ('%s', '%s', '%s', '%s')" % (vehicle_name, vehicle_vin, vehicle_license, vehicle_status)
    execute_query(conn, sql)

    return "Added New Vehicle"

# Info for Vehicle Update Form 
@app.route('/inventory/vehicle/info', methods = ['POST'])
def vehicle_info():
    request_data = request.get_json()
    vehicle_id = request_data['vehicle_id']


    sql = "SELECT * FROM Vehicle_Inventory WHERE vehicle_id = %s" % (vehicle_id)
    vehicle_info = execute_read_query(conn, sql)

    return jsonify(vehicle_info)

# Pushes vehicle update
@app.route('/inventory/vehicle/update', methods = ['PUT'])
def update_vehicle():
    request_data = request.get_json()
    vehicle_id = request_data['vehicle_id']
    vehicle_name = request_data['vehicle_name']
    vehicle_vin = request_data['vehicle_vin']
    vehicle_license = request_data['vehicle_license']
    vehicle_status = request_data['vehicle_status']

    sql = """
    UPDATE Vehicle_Inventory
    SET vehicle_name ='%s', vehicle_vin = '%s', vehicle_license = '%s', vehicle_status = '%s'
    WHERE vehicle_id = %s
    """ %(vehicle_name, vehicle_vin, vehicle_license, vehicle_status, vehicle_id)
    execute_query(conn, sql)

    return "Updated Vehicle"

# Deletes a vehicle
@app.route('/inventory/vehicle/delete', methods = ['PUT'])
def delete_vehicle():
    request_data = request.get_json()
    vehicle_id = request_data['vehicle_id']

    sql = """
    UPDATE Equipment_Deployment
    SET vehicle_id = null
    WHERE vehicle_id = %s
    """ %(vehicle_id)
    execute_query(conn, sql)
    

    sql = """
    UPDATE Vehicle_Inventory
    SET vehicle_Status = 'Sold'
    WHERE vehicle_id = %s
    """ %(vehicle_id)
    execute_query(conn, sql)

    return "Deleted Vehicle"    


# ----- Start of Vehicle Information APIs
#Add Vehicle Information 
@app.route('/inventory/vehicle/info/add', methods = ['POST'])
def add_vehicleinfo():
    request_data = request.get_json()
    vehicles = request_data['car_list']                         
    insurance_info = request_data['insurance_info']
    next_inspection_date = request_data['next_inspection_date']
   

    sql = "INSERT INTO Vehicle_Information (insurance_info, next_inspection_date) VALUES ('%s', '%s')" % (insurance_info, next_inspection_date) 
    execute_query(conn, sql)

    sql = 'SELECT * FROM Vehicle_Information WHERE vehicle_info_id = SCOPE_IDENTITY()' 
    vehicle_info_id = execute_read_query(conn, sql)
    vehicle_info_id = vehicle_info_id[0]['vehicle_info_id']


    sql = "UPDATE Vehicle_Inventory SET vehicle_info_id = '%s' WHERE vehicle_id='%s'" % (vehicle_info_id, vehicles)
    execute_query(conn, sql)

    return "Added New Vehicle Information"

# Gets information for update form for Vehicle Information
@app.route('/inventory/vehicle/info/update/info', methods = ['POST'])
def vehicleinfo_info():
    request_data = request.get_json()
    vehicle_info_id = request_data['vehicle_info_id']

    sql = """
    SELECT Vehicle_Information.insurance_info, Vehicle_Information.next_inspection_date, Vehicle_Information.vehicle_info_id, 
    Vehicle_Inventory.vehicle_name, Vehicle_Inventory.vehicle_id
    FROM Vehicle_Information 
    INNER JOIN Vehicle_Inventory on Vehicle_Inventory.vehicle_info_id = Vehicle_Information.vehicle_info_id
    WHERE Vehicle_Information.vehicle_info_id = %s    """ % (vehicle_info_id)
    vehicle_info_info = execute_read_query(conn, sql)
    for row in vehicle_info_info:
        rawdatetime = row['next_inspection_date']
    if rawdatetime != None:
        feedback_date = rawdatetime.strftime("%Y-%m-%d")
        row['next_inspection_date'] = feedback_date
    sql = "SELECT vehicle_id, vehicle_name FROM Vehicle_Inventory"
    vehicle_dropdown = execute_read_query(conn, sql)

    return jsonify(vehicle_info_info,vehicle_dropdown)

# Vehicle Information update
@app.route('/inventory/vehicle/info/update/', methods = ['PUT'])
def update_vehicleinfo():
    request_data = request.get_json()
    vehicle_info_id = request_data['vehicle_info_id']
    insurance_info = request_data['insurance_info']
    next_inspection_date = request_data['next_inspection_date']


    sql = """
    UPDATE Vehicle_Information
    SET insurance_info ='%s', next_inspection_date = '%s'
    WHERE vehicle_info_id = %s
    """ %(insurance_info, next_inspection_date, vehicle_info_id)
    execute_query(conn, sql)

    return "Updated Vehicle Information"

# Deletes Vehicle Information aka insurance 
@app.route('/inventory/vehicle/info/delete', methods = ['PUT'])
def delete_vehicleinfo():
    request_data = request.get_json()
    vehicle_info_id = request_data['vehicle_info_id']

    sql = """
    UPDATE Vehicle_Inventory
    SET vehicle_info_id = null
    WHERE vehicle_info_id = %s
    """ %(vehicle_info_id)

    execute_query(conn, sql)

    sql = "DELETE FROM Vehicle_Information WHERE vehicle_info_id = %s" %(vehicle_info_id)
    execute_query(conn, sql)

    return "Deleted Vehicle Information"


# ----- Start of Vehicle Maintenance APIs
#Add Vehicle Maintenance
@app.route('/inventory/vehicles/maintenance/add', methods = ['POST'])
def add_vehiclemain():
    request_data = request.get_json()
    vehicle_id = request_data['car_list']      
    employee_id = request_data['employees']                   
    service_date = request_data['service_date']
    maintenance_comments = request_data['maintenance_comments']
    
    sql = "INSERT INTO Vehicle_Maintenance (service_date, maintenance_comments, vehicle_id, employee_id) VALUES ('%s', '%s', %s, %s)" % (service_date, maintenance_comments, vehicle_id, employee_id) 
    execute_query(conn, sql)

    return "Added New Vehicle Maintenance"

# Info for vehicle Main update form 
@app.route('/inventory/vehicles/maintenance/info', methods = ['POST'])
def maintenance_info():
    request_data = request.get_json()
    maintenance_id = request_data['maintenance_id']

    sql = """
    SELECT Vehicle_Maintenance.employee_id, Vehicle_Maintenance.maintenance_comments, Vehicle_Maintenance.maintenance_id, Vehicle_Maintenance.service_date, Vehicle_Inventory.vehicle_name, Vehicle_Maintenance.vehicle_id 
    FROM Vehicle_Maintenance 
    INNER JOIN Vehicle_Inventory on Vehicle_Inventory.vehicle_id = Vehicle_Maintenance.vehicle_id
    WHERE maintenance_id = %s
    """ % (maintenance_id)
    maintenance_info = execute_read_query(conn, sql)
    for row in maintenance_info:
        rawdatetime = row['service_date']
    if rawdatetime != None:
        feedback_date = rawdatetime.strftime("%Y-%m-%d")
        row['service_date'] = feedback_date
    sql= """
    SELECT vehicle_id, vehicle_name FROM Vehicle_Inventory
    """
    car_list = execute_read_query(conn, sql)

    sql = "SELECT employee_id, first_name, last_name FROM Employee"
    emp_list = execute_read_query(conn, sql)

    return jsonify(maintenance_info, car_list, emp_list)

# Pushes update to database
@app.route('/inventory/vehicles/maintenance/update', methods = ['PUT'])
def maintenance_update():
    request_data = request.get_json()
    maintenance_id = request_data['maintenance_id']
    service_date = request_data['service_date']
    employee_id = request_data['employee_id']
    maintenance_comments = request_data['maintenance_comments']


    sql = """
    UPDATE Vehicle_Maintenance
    SET service_date = '%s', employee_id = %s, maintenance_comments = '%s'
    WHERE maintenance_id = %s
    """ %(service_date, employee_id, maintenance_comments, maintenance_id)
    execute_query(conn, sql)

    return "Updated Vehicle Maintenance"

# Deletes a vehicle maintence log 
@app.route('/inventory/vehicles/maintenance/delete', methods = ['PUT'])
def maintenance_delete():
    request_data = request.get_json()
    maintenance_id = request_data['maintenance_id']

    sql = "DELETE FROM Vehicle_Maintenance WHERE maintenance_id = %s" %(maintenance_id)
    execute_query(conn, sql)

    return "Deleted Vehicle Maintenance"       

#--------------------------------------------------------------------
# --------------------------- SUPPLIER PAGE -------------------------
#--------------------------------------------------------------------
# Main Suppliers Page 
@app.route('/supliers', methods = ['GET'])
def supplier():

    sql = "SELECT equipment_id, equipment_name FROM Tools_Inventory"
    equipment_results = execute_read_query(conn, sql)

    sql = """
        SELECT * FROM State_code
        """
    states_results = execute_read_query(conn, sql)

    #sql= """
        #SELECT supplier_id, supplier_name FROM Supplier
        #"""
    #supply_name_results = execute_read_query(conn, sql)

    sql = """
    SELECT Supplier.supplier_id, Supplier.supplier_name, Supplier_Contacts.sup_contact_id, Supplier_Contacts.phone, Supplier_Contacts.email, Supplier_Contacts.street, Supplier_Contacts.city, State_code.state_name, Supplier_Contacts.zipcode
    FROM Supplier
    LEFT JOIN Supplier_Contacts ON Supplier.sup_contact_id = Supplier_Contacts.sup_contact_id
    INNER JOIN State_code ON Supplier_Contacts.state_code_id = State_code.state_code_id
    """
    supplier_results = execute_read_query(conn,sql)

    return jsonify(equipment_results, states_results, supplier_results)

#Add supplier
@app.route('/supliers/add', methods = ['POST'])
def add_supplier():
    request_data = request.get_json()
    supplier_name = request_data['supplier_name']
    phone = request_data['phone']        
    email = request_data['email']    
    street = request_data['street']
    city = request_data['city'] 
    states = request_data['states']      
    zipcode = request_data['zipcode']  
    
    sql= """
    INSERT INTO Supplier_Contacts (phone, email, street, city, state_code_id, zipcode) 
    VALUES (%s, '%s', '%s','%s', '%s', %s)
    """%(phone, email, street, city, states, zipcode)
    execute_query(conn, sql)

   
    sql = 'SELECT * FROM Supplier_Contacts WHERE sup_contact_id = SCOPE_IDENTITY()' 
    sup_contact_id = execute_read_query(conn, sql)
    sup_contact_id = sup_contact_id[0]['sup_contact_id']
    # Stores Customer Contacts Information 

    sql = """
    INSERT INTO Supplier (sup_contact_id, supplier_name) 
    VALUES (%s, '%s');
    """ %(sup_contact_id, supplier_name)
    execute_query(conn, sql)

    return "Added New Supplier"

# Information about the update form for suppliers
@app.route('/suppliers/update/info', methods = ['POST'])
def supplier_info():
    request_data = request.get_json()
    # custoemr first and last name
    suppliercontact_id = request_data['sup_contact_id']

    sql = """
    SELECT Supplier.supplier_id, Supplier.supplier_name, Supplier_Contacts.sup_contact_id, Supplier_Contacts.phone, Supplier_Contacts.email, 
    Supplier_Contacts.street, Supplier_Contacts.city, State_code.state_name, State_code.state_code_id, Supplier_Contacts.zipcode
    FROM Supplier
    FULL OUTER JOIN Supplier_Contacts ON Supplier.sup_contact_id = Supplier_Contacts.sup_contact_id
    INNER JOIN State_code ON Supplier_Contacts.state_code_id = State_code.state_code_id
    WHERE supplier_contacts.sup_contact_id = %s """ %(suppliercontact_id)
    supplier_info = execute_read_query(conn, sql)
    
    sql = "SELECT * FROM State_code"
    states = execute_read_query(conn, sql)

    return jsonify(supplier_info, states)

# Suppliers update 
@app.route('/suppliers/update', methods = ['PUT'])
def update_supplier():
    request_data = request.get_json()
    sup_contact_id = request_data['sup_contact_id']
    supplier_name = request_data['supplier_name']
    phone = request_data['phone']           
    email = request_data['email']
    street = request_data['street']
    city = request_data['city']   
    states = request_data['states']     
    zipcode = request_data['zipcode']  
    
    sql = """
    UPDATE Supplier 
    SET supplier_name ='%s'
    WHERE sup_contact_id = %s
    """ %(supplier_name, sup_contact_id)
    execute_query(conn, sql)
    # Stores Customer Contacts Information 
    sql = """
    UPDATE Supplier_Contacts
    SET phone = '%s', email = '%s', street = '%s', city = '%s', state_code_id = '%s', zipcode = %s
    WHERE sup_contact_id = %s  
    """%(phone, email, street, city, states, zipcode, sup_contact_id)
    execute_query(conn, sql)
    return "Updated Customer Information"

# Deletes Suppliers 
@app.route('/suppliers/delete', methods = ['PUT'])
def del_supplier():
    request_data = request.get_json()
    supplier_id = request_data['supplier_id']

    sql = """
    UPDATE Tools_Inventory
    SET supplier_id = null
    WHERE supplier_id = %s
    """ %(supplier_id)
    execute_query(conn, sql)

    sql = """
    UPDATE Chemical_Inventory
    SET supplier_id = null
    WHERE supplier_id = %s
    """ %(supplier_id)
    execute_query(conn, sql)

    sql = "DELETE FROM Supplier WHERE supplier_id = %s" %(supplier_id)
    execute_query(conn, sql)

    return "Deleted Supplier"



#--------------------------------------------------------------------
# ----------------- EQUIPMENT DEPLOYMENT PAGE -----------------------
#--------------------------------------------------------------------
# Equipment Deployment Main Page
@app.route('/jobs/equipment_deployment', methods = ['GET'])
def equipment_deployment():
    sql = """
    SELECT Equipment_Deployment.deploy_id, Equipment_Deployment.equip_status,
    Equipment_Deployment.equipment_id, Tools_Inventory.equipment_name, Tools_Inventory.equipment_type,
    Equipment_Deployment.chemical_ID, Chemical_Inventory.chemical_Name, Chemical_Inventory.chemcial_type,
    Equipment_Deployment.vehicle_id, Vehicle_Inventory.vehicle_name, Vehicle_Inventory.vehicle_license,
    Scheduled_Jobs.job_id, Scheduled_Jobs.app_date
    FROM Equipment_Deployment
    LEFT JOIN Tools_Inventory on Tools_Inventory.equipment_id = Equipment_Deployment.equipment_id
    LEFT JOIN Chemical_Inventory on Chemical_Inventory.chemical_ID = Equipment_Deployment.chemical_id
    LEFT JOIN Vehicle_Inventory on Vehicle_Inventory.vehicle_id= Equipment_Deployment.vehicle_id
    INNER JOIN Scheduled_Jobs on Scheduled_Jobs.deploy_id = Equipment_Deployment.deploy_id
    ORDER BY Scheduled_Jobs.app_date DESC
    """ 
    equip_deploy_table = execute_read_query(conn, sql)

    sql = """
    SELECT Equipment_Deployment.deploy_id, Scheduled_Jobs.app_date
    FROM Equipment_Deployment
    LEFT JOIN Scheduled_Jobs on Scheduled_Jobs.deploy_id = Equipment_Deployment.deploy_id 
    ORDER BY Scheduled_Jobs.app_date DESC
    """
    equip_id = execute_read_query(conn, sql)

    sql = "SELECT * FROM Chemical_Inventory"
    chemicals = execute_read_query(conn, sql)

    sql = "SELECT * FROM Vehicle_Inventory"
    vehicles = execute_read_query(conn, sql)

    sql = "SELECT * FROM Tools_Inventory"
    tools = execute_read_query(conn, sql)

    sql = "SELECT app_date FROM Scheduled_Jobs ORDER BY app_date DESC"
    dates_dropdown = execute_read_query(conn, sql)
    for row in dates_dropdown:
        rawdatetime = row["app_date"]
        appoint_date = rawdatetime.strftime("%Y-%m-%d")
        appoint_times = rawdatetime.strftime("%I:%M:%S%p")
        newdatetime = appoint_date + ' ' + appoint_times
        row["app_date"] = newdatetime

    return jsonify(equip_deploy_table, equip_id, tools, chemicals, vehicles, dates_dropdown)

# Add new Deployment   
@app.route('/jobs/equipment_deployment/add', methods = ['POST'])
def add_equip_deploy():
    request_data = request.get_json()
    chemical = request_data['chemical']
    tool = request_data['tool']
    vehicle = request_data['vehicle']
    equip_status = request_data['equip_status']
    app_date = request_data['add_scheddate']

    sql = """
    INSERT INTO Equipment_Deployment (equip_status, vehicle_id, chemical_id, equipment_id)
    VALUES ('%s', %s, %s, %s)
    """%(equip_status, vehicle, chemical, tool)
    execute_query(conn, sql)

    sql = 'SELECT * FROM Equipment_Deployment WHERE deploy_id = SCOPE_IDENTITY()' 
    deploy_id = execute_read_query(conn, sql)
    deploy_id = deploy_id[0]['deploy_id']

    sql = """
    UPDATE Scheduled_Jobs 
    SET deploy_id = %s
    WHERE app_date = '%s'
    """ % (deploy_id, app_date)
    execute_query(conn, sql)

    return "Added Equipment Deployment"

# Equipment deployment update form
@app.route('/jobs/equipment_deployment/update/info', methods = ['POST'])
def equip_deploy_form():
    request_data = request.get_json()
    deployid = request_data['deployid']
    sql = """
    SELECT Equipment_Deployment.deploy_id, Equipment_Deployment.equip_status,
    Equipment_Deployment.equipment_id, Tools_Inventory.equipment_name, Tools_Inventory.equipment_type,
    Equipment_Deployment.chemical_ID, Chemical_Inventory.chemical_Name, Chemical_Inventory.chemcial_type,
    Equipment_Deployment.vehicle_id, Vehicle_Inventory.vehicle_name, Vehicle_Inventory.vehicle_license,
    Scheduled_Jobs.job_id, Scheduled_Jobs.app_date
    FROM Equipment_Deployment
    LEFT JOIN Tools_Inventory on Tools_Inventory.equipment_id = Equipment_Deployment.equipment_id
    LEFT JOIN Chemical_Inventory on Chemical_Inventory.chemical_ID = Equipment_Deployment.chemical_id
    LEFT JOIN Vehicle_Inventory on Vehicle_Inventory.vehicle_id= Equipment_Deployment.vehicle_id
    INNER JOIN Scheduled_Jobs on Scheduled_Jobs.deploy_id = Equipment_Deployment.deploy_id
    ORDER BY Scheduled_Jobs.app_date DESC
    """ 
    equip_deploy_table = execute_read_query(conn, sql)

    sql = """
    SELECT Equipment_Deployment.deploy_id, Equipment_Deployment.equip_status,
    Equipment_Deployment.equipment_id, Tools_Inventory.equipment_name, Tools_Inventory.equipment_type,
    Equipment_Deployment.chemical_ID, Chemical_Inventory.chemical_Name, Chemical_Inventory.chemcial_type,
    Equipment_Deployment.vehicle_id, Vehicle_Inventory.vehicle_name, Vehicle_Inventory.vehicle_license,
    Scheduled_Jobs.job_id, Scheduled_Jobs.app_date
    FROM Equipment_Deployment
    LEFT JOIN Tools_Inventory on Tools_Inventory.equipment_id = Equipment_Deployment.equipment_id
    LEFT JOIN Chemical_Inventory on Chemical_Inventory.chemical_ID = Equipment_Deployment.chemical_id
    LEFT JOIN Vehicle_Inventory on Vehicle_Inventory.vehicle_id= Equipment_Deployment.vehicle_id
    INNER JOIN Scheduled_Jobs on Scheduled_Jobs.deploy_id = Equipment_Deployment.deploy_id
    WHERE Equipment_Deployment.deploy_id = %s
    """ %(deployid)
    current_equipdep_info = execute_read_query(conn, sql)

    sql = "SELECT * FROM Chemical_Inventory"
    chemicals = execute_read_query(conn, sql)

    sql = "SELECT * FROM Vehicle_Inventory"
    vehicles = execute_read_query(conn, sql)

    sql = "SELECT * FROM Tools_Inventory"
    tools = execute_read_query(conn, sql)

    sql = "SELECT app_date FROM Scheduled_Jobs "
    avaliable_appoints = execute_read_query(conn, sql)
    return jsonify(current_equipdep_info, equip_deploy_table, chemicals, vehicles, tools, avaliable_appoints)

# Update Equipment Deployment
@app.route('/jobs/equipment_deployment/update', methods = ['PUT'])
def equip_deploy_update():
    request_data = request.get_json()
    deploy_id = request_data['deploy_id']
    chemical = request_data['chemical_id']
    tool = request_data['equipment_id']
    vehicle = request_data['vehicle_id']
    equip_status = request_data['equip_status']
    sql = """
    UPDATE Equipment_Deployment 
    SET equip_status = '%s' , vehicle_id = %s , chemical_id = %s , equipment_id = %s
    WHERE deploy_id = %s
    """%(equip_status, vehicle, chemical, tool, deploy_id)
    execute_query(conn, sql)

    return "Updated Equipment Deployment"

# Delete the Equipment Deployment
@app.route('/jobs/equipment_deployment/delete', methods = ['PUT'])
def del_equip_deploy():
    request_data = request.get_json()
    deploy_id = request_data['deploy_id']

    sql = """
    UPDATE Scheduled_Jobs
    SET deploy_id = null
    WHERE deploy_id = %s
    """ %(deploy_id)
    execute_query(conn, sql)

    sql = "DELETE FROM Equipment_Deployment WHERE deploy_id = %s" %(deploy_id)
    execute_query(conn, sql)

    return "Deleted Equipment Deployment"



#--------------------------------------------------------------------
#-------------------- ADMIN PAGE VERIFICATION -----------------------
#--------------------------------------------------------------------
@app.route('/admin_validation', methods=['GET']) # http://127.0.0.1:5000/api/authenticate
def admin_validation(): 
    user_logininfo = request.get_json()
    sql = """
    SELECT * FROM Login_information
    """ 
    logins = execute_read_query(conn, sql) # Fetch reqest for login information from DB
    if 'username' in user_logininfo:         # User Inputs of Username stored to variables / reject if no username provided
        input_username = user_logininfo['username']
    else: 
        return 'No username provided'
    if 'password' in user_logininfo:         # User Input of Password stored to variable / reject if no pass provided
        input_pw = user_logininfo['password']
    else:
        return 'no password provided'
    Username = 0
    userPassword = 0
    for login in logins:
        if input_username == login['username']: # vars to check username and password are assigned  
            Username = login['username']
            userPassword = login['user_password']
            privilege = login['privilege_id']
    if Username == 0 or userPassword == 0:      # Handle Non-existing users
        return 'Account Could Not Be Found'
    else: 
        if Username == input_username and userPassword == input_pw: # verification on if username and password match in DB
            tokens.get_time_token_8h() # creates an 8 hour token
            token = tokens.get_curr_token() # stores the token in token variable
            current_tokens.update({Username : token})    # stored the token with the username for verification
            curuser.set_current_user(Username)
            return jsonify(logins, privilege)
    return 'COULD NOT VERIFY!'




#--------------------------------------------------------------------
#------------------------- EMPLOYEE PAGE ----------------------------
#--------------------------------------------------------------------
# Employee Main page
@app.route('/employee', methods = ['GET'])
def employee_info():

    sql = """
    SELECT * FROM State_code
    """
    states_results = execute_read_query(conn, sql)

    sql = """
    SELECT * FROM Roles
    """ 
    role_results = execute_read_query(conn,sql)

    sql = """
    SELECT Employee.employee_id, Employee_Contact_Info.emp_cnt_id, Employee.first_name, Employee.last_name, Employee.employee_status, Roles.role_name, Roles.role_description,Employee_Contact_Info.emp_phone, Employee_Contact_Info.emp_email, Employee_Contact_Info.emp_street, Employee_Contact_Info.emp_city, State_code.state_name, Employee_Contact_Info.emp_zipcode
    FROM Employee
    INNER JOIN Employee_Contact_Info ON Employee.emp_cnt_id = Employee_Contact_Info.emp_cnt_id
    INNER JOIN State_code ON Employee_Contact_Info.state_code_id = State_code.state_code_id
    INNER JOIN Roles ON Employee.role_id = Roles.role_id
    ORDER BY Employee.last_name
    """ 
    employee_results = execute_read_query(conn, sql)

    sql = """
    SELECT * FROM Login_information
    """ 
    logins = execute_read_query(conn, sql) # Fetch reqest for login information from DB

    sql = "SELECT employee_id FROM Employee"
    employee_dropdown = execute_read_query(conn, sql)

    return jsonify(states_results, role_results, employee_results, logins,employee_dropdown)

# Add new employee
@app.route('/admin/addemployee', methods = ['POST'])
def add_employee():
    request_data = request.get_json()
    first_name = request_data['first_name']
    last_name = request_data['last_name']  
    employee_status = request_data['employee_status']
    role_list = request_data['role_list']      
    emp_phone = request_data['emp_phone']    
    emp_email = request_data['emp_email']
    emp_street = request_data['emp_street']
    emp_city = request_data['emp_city']   
    states = request_data['states']     
    emp_zipcode = request_data['emp_zipcode']  

    
    sql = """
    INSERT INTO Employee_Contact_Info (emp_phone, emp_email, emp_street, emp_city, state_code_id, emp_zipcode) 
    VALUES ('%s', '%s', '%s','%s', '%s', %s)
    """%(emp_phone, emp_email, emp_street, emp_city, states, emp_zipcode)
    execute_query(conn, sql)

    # gets the customer id from the above execution
    sql = 'SELECT * FROM Employee_Contact_Info WHERE emp_cnt_id= SCOPE_IDENTITY()' 
    emp_cnt_id = execute_read_query(conn, sql)
    emp_cnt_id = emp_cnt_id[0]['emp_cnt_id']
    # Stores Customer Contacts Information 
    
    sql = """
    INSERT INTO Employee (employee_status, first_name, last_name, role_id, emp_cnt_id)  
    VALUES ('%s', '%s', '%s', %s, %s);
    """ %(employee_status, first_name,last_name, role_list[0], emp_cnt_id)
    execute_query(conn, sql)

    return "Added New Employee"

# Employee Update Form 
@app.route('/employee/info', methods = ['POST'])
def employeeupdate_info():
    request_data = request.get_json()
    # custoemr first and last name
    emp_cnt_id = request_data['emp_cnt_id']

    sql = """SELECT Employee.employee_id, Employee_Contact_Info.emp_cnt_id, Employee.first_name, Employee.last_name, Employee.employee_status, 
    Roles.role_name, Roles.role_id,
    Employee_Contact_Info.emp_phone, Employee_Contact_Info.emp_email, Employee_Contact_Info.emp_street, Employee_Contact_Info.emp_city, 
    State_code.state_name, Employee_Contact_Info.emp_zipcode
    FROM Employee
    INNER JOIN Employee_Contact_Info ON Employee.emp_cnt_id = Employee_Contact_Info.emp_cnt_id
    INNER JOIN State_code ON Employee_Contact_Info.state_code_id = State_code.state_code_id
    INNER JOIN Roles ON Employee.role_id = Roles.role_id
    WHERE Employee_Contact_Info.emp_cnt_id = %s """ %(emp_cnt_id)
    employee_info = execute_read_query(conn, sql)
    
    sql = "SELECT * FROM Roles"
    roles_info = execute_read_query(conn,sql)

    sql = "SELECT * FROM State_code"
    states = execute_read_query(conn, sql)

    return jsonify(employee_info, roles_info, states)

# Employee Update
@app.route('/employee/update', methods = ['PUT'])
def update_employee():
    request_data = request.get_json()
    emp_cnt_id = request_data['emp_cnt_id']
    first_name = request_data['first_name']
    last_name = request_data['last_name']
    employee_status = request_data['employee_status']
    role_id = request_data['role_id']
    emp_phone = request_data['emp_phone']           
    emp_email = request_data['emp_email']
    emp_street = request_data['emp_street']
    emp_city = request_data['emp_city']   
    states = request_data['states']     
    emp_zipcode = request_data['emp_zipcode']  
    
    sql = """
    UPDATE Employee   
    SET employee_status = '%s', first_name = '%s', last_name = '%s', role_id = %s
    WHERE emp_cnt_id = %s
    """ %(employee_status, first_name, last_name, role_id, emp_cnt_id)
    execute_query(conn, sql)
    # Stores Customer Contacts Information 
    sql = """
    UPDATE Employee_Contact_Info
    SET emp_phone = '%s', emp_email = '%s', emp_street = '%s', emp_city = '%s', state_code_id = '%s', emp_zipcode = %s
    WHERE emp_cnt_id = %s  
    """%(emp_phone, emp_email, emp_street, emp_city, states, emp_zipcode, emp_cnt_id)
    execute_query(conn, sql)
    return "Updated Employee Information"

# Employee Soft Delete
@app.route('/employee/delete', methods = ['PUT'])
def del_employee():
    request_data = request.get_json()
    employee_id = request_data['employee_id']

    sql = """
    UPDATE Employee
    SET employee_status = 'Terminated'
    WHERE employee_id = %s
    """ %(employee_id)
    execute_query(conn, sql)

    return 'Set Employee Status to Terminated'

# Employee Hard delete
@app.route('/employee/truedelete', methods = ['PUT'])
def fdel_employee():
    request_data = request.get_json()
    employee_id = request_data['employee_id']

    sql = """
    DELETE Employee
    WHERE employee_id = %s
    """ %(employee_id)
    execute_query(conn, sql)

    return 'Removed Employee Data'



#--------------------------------------------------------------------
#--------------------------- ACCOUNT API ----------------------------
#--------------------------------------------------------------------
# Main Page for Accounts
@app.route('/employee/admin/security_information', methods = ['GET'])
def security_information():

    sql = """
    SELECT * FROM Employee
    """
    employee_results = execute_read_query(conn,sql)

    sql = """
    SELECT * FROM System_privileges"""
    sytempriv_results = execute_read_query(conn,sql)

    sql = """  
    SELECT Login_information.account_id, Employee.first_name, Employee.last_name, Login_information.username, Login_information.user_password, System_privileges.privilege_name, System_privileges.privelege_description  
    FROM Employee
    INNER JOIN Login_information ON Login_information.account_id = Employee.account_id
    INNER JOIN System_privileges ON Login_information.privilege_id = System_privileges.privilege_id"""

    security_results = execute_read_query(conn, sql)

    return jsonify(employee_results, sytempriv_results, security_results)

# Add new Account
@app.route('/admin/addsyspriv', methods = ['POST'])
def add_security():
    request_data = request.get_json()
    employee_list = request_data['employee_list'] 
    systempriv_list = request_data['systempriv_list']   
    username = request_data['username']
    user_password = request_data['user_password']
   

    sql = "INSERT INTO Login_information (username, user_password, privilege_id) VALUES ('%s', '%s', %s)" % (username, user_password, systempriv_list) 
    execute_query(conn, sql)

    sql = 'SELECT * FROM Login_Information WHERE account_id = SCOPE_IDENTITY()' 
    account_id = execute_read_query(conn, sql)
    account_id = account_id[0]['account_id']


    sql = "UPDATE Employee SET account_id = '%s' WHERE employee_id='%s'" % (account_id, employee_list)
    execute_query(conn, sql)

    return "Added New Account Information"

# Account Update form
@app.route('/system_privilege/info', methods = ['POST'])
def systemprivilege_info():
    request_data = request.get_json()
    # custoemr first and last name
    account_id = request_data['account_id']

    sql = """  
    SELECT Login_information.account_id, Employee.employee_id, System_privileges.privilege_id, Employee.first_name, Employee.last_name, Login_information.username, Login_information.user_password, System_privileges.privilege_name, System_privileges.privelege_description  
    FROM Employee
    INNER JOIN Login_information ON Login_information.account_id = Employee.account_id
    INNER JOIN System_privileges ON Login_information.privilege_id = System_privileges.privilege_id
    WHERE Login_Information.account_id = %s """ %(account_id)
    account_info = execute_read_query(conn, sql)
    
    sql = "SELECT * FROM System_privileges"
    syspriv = execute_read_query(conn,sql)

    return jsonify(account_info, syspriv)

# Account Update
@app.route('/system_privilege/update', methods = ['PUT'])
def update_systemprivilege():
    request_data = request.get_json()
    account_id = request_data['account_id']
    username = request_data['username']
    user_password = request_data['user_password']
    privilege_id = request_data['privilege_id']       
    
    sql = """
    UPDATE Login_information 
    SET username ='%s', user_password ='%s', privilege_id = %s 
    WHERE account_id = %s
    """ %(username, user_password, privilege_id, account_id)
    execute_query(conn, sql)

    return 'Updated Account Information'

# Account Delete   
@app.route('/admin/delsyspriv', methods = ['PUT'])
def del_security():
    request_data = request.get_json()
    account_id = request_data['account_id']

    sql = """
    UPDATE Employee
    SET account_id = null
    WHERE account_id = %s
    """ %(account_id)
    execute_query(conn, sql)

    sql = "DELETE FROM Login_Information WHERE account_id = %s" %(account_id)
    execute_query(conn, sql)

    return "Deleted Employee Login Information"



#--------------------------------------------------------------------
#------------------------ INVOICE PAGE API --------------------------
#--------------------------------------------------------------------
# Main Invoice Page 
@app.route('/invoice', methods = ['GET'])
def invoice():

    sql = "SELECT quote_id FROM Quote"
    quote_results = execute_read_query(conn, sql)
    sql = """
    SELECT Invoice.invoice_id, Customer.first_name, Customer.last_name, Invoice.due_date, Invoice.comments, Invoice.actual_total, Invoice.invoice_status
    FROM Invoice
    INNER JOIN Scheduled_Jobs ON Invoice.invoice_id = Scheduled_Jobs.invoice_id
    INNER JOIN Customer ON Scheduled_Jobs.customer_id = Customer.customer_id
    """ 
    invoice_results = execute_read_query(conn, sql)
    # Isolates just the date from the datetime
    for row in invoice_results:
        rawdatetime = row["due_date"]
        if rawdatetime != None:
            feedback_date = rawdatetime.strftime("%Y-%m-%d")
            row["due_date"] = feedback_date
    sql = "SELECT invoice_id FROM Invoice"
    invoice_id_dropdown = execute_read_query(conn,sql)
        
    return jsonify(quote_results, invoice_results, invoice_id_dropdown)

# Invoice Update form 
@app.route('/invoice/info', methods = ['POST'])
def invoice_info():
    try: 
        token = current_tokens[curuser.get_current_user()]
    except:
        return 'No Active User Detected'
    # checks if the time token is still valid/the date on the token has not passed yet
    if float(token) > time.time():
        request_data = request.get_json()
        invoice_id = request_data['invoice_id']
        sql = "SELECT * FROM Invoice WHERE invoice_id=%s " %(invoice_id)
        results = execute_read_query(conn, sql)
        try:
            # Isolates just the date from the datetime 
            rawdatetime = results[0]["due_date"]
            feedback_date = rawdatetime.strftime("%Y-%m-%d")
            results[0]["due_date"] = feedback_date
        except:
            pass
        sql = "SELECT quote_id, total_cost FROM Quote"
        quotes_dropdown = execute_read_query(conn,sql)
        return jsonify(results, quotes_dropdown)
    else: 
        return 'Session Timed Out! Please Log Back in'

# update invoice
@app.route('/invoice/update', methods = ['PUT'])
def update_invoice():
    try: 
        token = current_tokens[curuser.get_current_user()]
    except:
        return 'No Active User Detected'
    if float(token) > time.time():
        request_data = request.get_json()
        invoice_id = request_data['invoice_id']
        quote_id = request_data['quote_id']
        invoice_status = request_data['invoice_status']            
        comments = request_data['comments']               
        actual_total = request_data['actual_total']
        due_date = request_data['due_date']  

        sql = """
        UPDATE Invoice 
        SET quote_id = %s, invoice_status = '%s' , comments = '%s' , actual_total = %s, due_date = '%s'
        WHERE invoice_id = %s
        """ % (quote_id, invoice_status, comments, actual_total, due_date, invoice_id) 
        execute_query(conn, sql)
        return "Updated Invoice"
    else: 
        return 'Session Timed Out! Please Log Back in'
    
# Delele an invoice 
@app.route('/invoice/delete', methods = ['PUT'])
def delete_invoice():
    try: 
        token = current_tokens[curuser.get_current_user()]
    except:
        return 'No Active User Detected'
    if float(token) > time.time():
        request_data = request.get_json()
        invoice_id = request_data['invoice_id']

        sql = """
        UPDATE Scheduled_Jobs
        SET invoice_id = null
        WHERE invoice_id = %s
        """ %(invoice_id)
        execute_query(conn, sql)

        sql = """
        DELETE Invoice 
        WHERE invoice_id = %s
        """ % (invoice_id) 
        execute_query(conn, sql)
        return "Deleted Invoice %s" %(invoice_id)
    else: 
        return 'Session Timed Out! Please Log Back in'



#--------------------------------------------------------------------
#------------------------ QUOTE PAGE API --------------------------
#--------------------------------------------------------------------
# Quote Main Page    
@app.route('/sales/quote', methods = ['GET'])
def quote():

    sql = "SELECT * FROM Services_Offered"
    results_services = execute_read_query(conn, sql)

    sql = """
    SELECT q.quote_id, c.first_name, c.last_name, sc.app_date, s.service_name, q.comments, q.total_cost
    FROM Quote q
    INNER JOIN Invoice ON invoice.quote_id = q.quote_id
    INNER JOIN Services_Offered s ON s.service_id = q.service_id
    INNER JOIN Scheduled_Jobs sc ON  sc.invoice_id = Invoice.invoice_id
    INNER JOIN Customer c ON c.customer_id = sc.customer_id
    """ 
    results_quote = execute_read_query(conn, sql)
    return jsonify(results_quote, results_services)

# Info for quote update form 
@app.route('/quote/info', methods = ['POST'])
def quote_info():
    try: 
        token = current_tokens[curuser.get_current_user()]
    except:
        return 'No Active User Detected'
    # checks if the time token is still valid/the date on the token has not passed yet
    if float(token) > time.time():
        request_data = request.get_json()
        quote_id = request_data['quote_id']
        sql = """
        SELECT Quote.quote_id, Quote.comments, Quote.service_id, Services_Offered.service_name, Quote.total_cost
        FROM Quote
        LEFT JOIN Services_Offered on Services_Offered.service_id = Quote.service_id
        WHERE quote_id = %s 
        """ %(quote_id)
        results = execute_read_query(conn, sql)
        # services offered drop down 
        sql = "SELECT * FROM Services_Offered;"
        services = execute_read_query(conn, sql)
        return jsonify(results,services)
    else: 
        return 'Session Timed Out! Please Log Back in'

# Update quote
@app.route('/quote/update', methods = ['PUT'])
def update_quote():
    try: 
        token = current_tokens[curuser.get_current_user()]
    except:
        return 'No Active User Detected'
    if float(token) > time.time():
        request_data = request.get_json()
        service_id = request_data['service_list'] 
        quote_id = request_data['quote_id']
        total_cost = request_data['total_cost'] 
        comments = request_data['comments']

        sql = """
        UPDATE Quote
        SET comments = '%s', service_id = %s , total_cost = '%s'
        WHERE quote_id = %s
        """ % (comments, service_id, total_cost, quote_id) 
        execute_query(conn, sql)
        return "Updated Quote"
    else: 
        return 'Session Timed Out! Please Log Back in'

# Deletes a quote 
@app.route('/quote/delete', methods = ['PUT'])
def delete_quote():
    request_data = request.get_json()
    quote_id = request_data['quote_id']

    sql = """
    UPDATE Invoice
    SET quote_id = null
    WHERE quote_id = %s
    """ %(quote_id)
    execute_query(conn, sql)

    sql = "DELETE FROM Quote WHERE quote_id = %s" %(quote_id)
    execute_query(conn, sql)

    return "Deleted Quote"
 

# Insert refernce codes here 
# how to get a dictionary from the pyodc connector 
    # https://www.codegrepper.com/code-examples/python/pyodbc+cursor+create+list+of+dictionaries 
# token based authentication 
    # https://realpython.com/token-based-authentication-with-flask/ 
# Get most recent addded id 
    # https://stackoverflow.com/questions/7917695/sql-server-return-value-after-insert
# If app.run() is not here, the API will just end
app.run()
