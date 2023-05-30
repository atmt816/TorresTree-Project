// load the things we need
var express = require('express');
var app = express();
const bodyParser  = require('body-parser');
// required module to make calls to a REST API
const axios = require('axios');
const { response } = require('express');
const req = require('express/lib/request');
var selectedID = "";
app.use(bodyParser.urlencoded());
// set the view engine to ejs
app.set('view engine', 'ejs');


//--------------------------------------------------------------------
//------------------------------- LOGIN PAGE -------------------------
//--------------------------------------------------------------------
app.get('/', function(req, res) {
    var flag = 0;
    res.render('pages/login', {flag: flag
    });
});

app.post('/login', function(req, res){
    axios.get('http://127.0.0.1:5000/api/authenticate', {
        data:
        {
            username: req.body.username,
            password: req.body.password
        }
    }).then((response)=>
        {   
            if (response.data == "Successfully Logged in") {
                res.render('redirects/loggedin', {body: req.body})
            }
            else {
                var flag = 1;
                var response = response.data
                res.render('pages/login', {body: req.body, flag: flag, response: response})
            }
        }
    )
});

//--------------------------------------------------------------------
// -------------------------- LOGIN OUT PAGE -------------------------
//--------------------------------------------------------------------
app.get('/logout', function(req, res){
    axios.get('http://127.0.0.1:5000/api/logout')
    .then((response)=>{
    });
    res.render('redirects/loggedout');
});


//--------------------------------------------------------------------
// ------------------- Index/Home/Appointments Routes ---------------
//--------------------------------------------------------------------
// Main page   
app.get('/home', function(req, res){
    //*Schedules Table*
    axios.get('http://127.0.0.1:5000/home') 
    .then((response)=>{
        var appointment_data = response.data
        if (appointment_data == "No Active User Detected" || appointment_data == "Session Timed Out! Please Log Back in") {
            var flag = 1;
            var response = appointment_data
            res.render('pages/login', {flag: flag, response: response})
        }
        else {
            res.render('pages/index', {
            appointments: appointment_data[1], 
            states: appointment_data[0],
            employee: appointment_data[2],
            services: appointment_data[3],
            customers: appointment_data[4],
            update_dropdown: appointment_data[5], 
            });
        }
    });
});

// Add Appointment With existing Customer
app.post('/home/new/existing', function(req, res) {
    axios.post('http://127.0.0.1:5000/home/existing',{
        data: {
        customer_id: req.body.customer_id,

        services: req.body.services,
        quote_comment : req.body.quotecomment,
        quote_total : req.body.quote,

        employeelist : req.body.employee,

        app_status : req.body.app_status,
        app_date : req.body.date,
        app_time : req.body.time
        }
    })
    .then((response)=>{
        var message = response.data
        if (message == "No Active User Detected" || message == "Session Timed Out! Please Log Back in") {
            var flag = 1;
            var response = message
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
        res.render('redirects/redirecthome', {message : message});
        }
    });
});

// Add Appointment with New Customer 
app.post('/home/new', function(req, res) {
    axios.post('http://127.0.0.1:5000/home',{
        data: {
        first_name: req.body.firstname,
        last_name : req.body.lastname,
        phone : req.body.phone,
        email : req.body.email,
        street : req.body.street,
        city : req.body.city,
        state : req.body.state,
        zipcode: req.body.zipcode,

        services: req.body.services,
        quote_comment : req.body.quotecomment,
        quote_total : req.body.quote,

        employeelist : req.body.employee,

        app_status : req.body.app_status,
        app_date : req.body.date,
        app_time : req.body.time
        }
    })
    .then((response)=>{
        var message = response.data
        if (message == "No Active User Detected" || message == "Session Timed Out! Please Log Back in") {
            var flag = 1;
            var response = message
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
        res.render('redirects/redirecthome', {message : message});
        }
    });
});

// Redirects to an update form based on selecte Appointment ID 
app.post('/home/update', function(req, res) {
    axios.post('http://127.0.0.1:5000/home/form', 
    {
        job_id : req.body.job_id
    }
    
)
    .then((response)=>{
        var message = response.data
        var states_info = response.data[0]
        var change_appoint_id = response.data[1]
        var emp_names = response.data[2]
        var services = response.data[3]
        var appoint_date = response.data[4]
        var appoint_time = response.data[5]
        var curremp = response.data[6]
        var info = change_appoint_id
        if (message == "No Active User Detected" || message == "Session Timed Out! Please Log Back in") {
            var flag = 1;
            var response = message
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
        res.render('updates/updateform', {
            states : states_info,
            dataout : info[0],
            employee : emp_names,
            services : services,
            appoint_date: appoint_date,
            appoint_time: appoint_time,
            curremp: curremp,
            job_id : req.body.job_id
            });
        }
    });
});

// Updates the Information in the Database for Appointment
app.post('/home/update/submit', function(req, res) {
    axios.put('http://127.0.0.1:5000/home', 
    {
        customer_id: req.body.customer_id,
        invoice_id : req.body.invoice_id,
        job_id : req.body.job_id,
        quote_id: req.body.quote_id,
        first_name: req.body.firstname,
        last_name : req.body.lastname,
        phone : req.body.phone,
        email : req.body.email,
        street : req.body.street,
        city : req.body.city,
        state : req.body.state,
        zipcode: req.body.zipcode,

        services: req.body.services,
        quote_comment : req.body.quotecomment,
        quote_total : req.body.quote,

        employeelist : req.body.employee,

        app_status : req.body.app_status,
        app_date : req.body.date,
        app_time : req.body.time
    }
    
)
    .then((response)=>{
        var message = response.data
        if (message == "No Active User Detected" || message == "Session Timed Out! Please Log Back in") {
            var flag = 1;
            var response = message
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
        res.render('redirects/redirecthome', {message : message});
        }
    });

});

// Deletes the Selected Appoointment ID 
app.post('/home/delete', function(req, res) {
    axios.delete('http://127.0.0.1:5000/home',{
        data:{
            job_id: req.body.job_id
        }
    }
)
    .then((response)=>{
        var message = response.data
        if (message == "No Active User Detected" || message == "Session Timed Out! Please Log Back in") {
            var flag = 1;
            var response = message
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
        res.render('redirects/redirecthome', {message : message});
        }
    });
});

//--------------------------------------------------------------------
// ----------------------- SERVICE PAGE ROUTES -----------------------
//--------------------------------------------------------------------
// Main Page for Services
app.get('/services', function(req, res) {
    axios.get('http://127.0.0.1:5000/table/all/Services_Offered') 
    .then((response)=>{
        var service_data = response.data
        if (service_data == "Session Timed Out! Please Log Back in" || service_data =="No Active User Detected"){
            var flag = 1;
            var response = service_data
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
            res.render('pages/services', {services_list: service_data});
        }
        });
});

// Add a new service
app.post('/service/add', function(req, res) {
    axios.post('http://127.0.0.1:5000/services/addservice',
        {           
            service_name: req.body.service,
            service_description: req.body.description, 
            recommended_service_cost: req.body.cost         
        }
    ) 
    .then((response)=>{
        var service_data = response.data
        if (service_data == "Session Timed Out! Please Log Back in" || service_data =="No Active User Detected"){
            var flag = 1;
            var response = service_data
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
            var message = response.data
            res.render('redirects/redirectservices', {message : message});
        }
        });
});

// Gets the update form for the selected Service ID
app.post('/service/update/info', function(req, res){
    axios.post('http://127.0.0.1:5000/services/info', 
    {
        service_id : req.body.service_id
    }
    
)
    .then((response)=>{
        var current_service_data = response.data[0]
        var service_data = response.data
        if (service_data == "Session Timed Out! Please Log Back in" || service_data =="No Active User Detected"){
            var flag = 1;
            var response = service_data
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
            res.render('updates/updateformservice', {
                service_id : req.body.service_id,
                recommended_service_cost : current_service_data['recommended_service_cost'],
                service_description : current_service_data['service_description'],
                service_name : current_service_data['service_name']
            });
        }
    });
});

// Pushes the update to the database
app.post('/service/update', function(req, res) {
    axios.put('http://127.0.0.1:5000/services/update',
        {           
            service_id : req.body.service_id,
            service_name: req.body.service_name,
            service_description: req.body.service_description,
            recommended_service_cost: req.body.recommended_service_cost       
        }
    ) 
    .then((response)=>{
        var service_data = response.data
        if (service_data == "Session Timed Out! Please Log Back in" || service_data =="No Active User Detected"){
            var flag = 1;
            var response = service_data
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
            var message = response.data
            res.render('redirects/redirectservices', {message : message});
        }
        });
});

// Deletes a selected service based on ID
app.post('/service/delete', function(req, res) {
    axios.delete('http://127.0.0.1:5000/services/delete',
        {data:{           
            service_id : req.body.service_id,      
        }
        }
    ) 
    .then((response)=>{
        var service_data = response.data
        if (service_data == "Session Timed Out! Please Log Back in" || service_data =="No Active User Detected"){
            var flag = 1;
            var response = service_data
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
            var message = response.data
            res.render('redirects/redirectservices', {message : message});
        }
        });
});

//--------------------------------------------------------------------
// ----------------------- Customers Page Section --------------------
//--------------------------------------------------------------------
// Main Page of Cusotmers tab 
app.get('/customers', function(req, res){
    axios.get('http://127.0.0.1:5000/customers/customer_contacts')
    .then((response)=>{
        var customer_data = response.data
        if (customer_data == "Session Timed Out! Please Log Back in" || customer_data =="No Active User Detected"){
            var flag = 1;
            var response = customer_data
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
        res.render('pages/customers', {customer_list: customer_data[1], states: customer_data[0], customer_id: customer_data[2]});
        }
    });
});

// Adds a new customer with contact information
app.post('/customers/new', function(req, res)
{
    axios.post('http://127.0.0.1:5000/customer/add',
    {           
        first_name: req.body.firstname,
        last_name: req.body.lastname, 
        phone: req.body.phone,         
        email: req.body.email,
        street: req.body.street, 
        city: req.body.city,
        state_code_id: req.body.state,
        zipcode: req.body.zipcode    
    })
    .then((response)=>{
        customer_data = response.data
        if (customer_data == "Session Timed Out! Please Log Back in" || customer_data =="No Active User Detected"){
            var flag = 1;
            var response = customer_data
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
            var message = response.data
            res.render('redirects/redirectcustomers', {message : message});
        }
    });  
});

// Redirects to a form for updating info
app.post('/customer/update/info', function(req, res){ 
    axios.post('http://127.0.0.1:5000/customer/info', 
    {
        customer_id : req.body.customer_id
    }
    
)
    .then((response)=>{
        var customer_data = response.data
        var current_customer_name = customer_data[0]
        var current_customer_contacts = customer_data[1]
        var states = customer_data[2]
        if (customer_data == "Session Timed Out! Please Log Back in" || customer_data =="No Active User Detected"){
            var flag = 1;
            var response = customer_data
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
            res.render('updates/updateformcustomer', {
            customer_id : req.body.customer_id,
            first_name : current_customer_name['first_name'],
            last_name : current_customer_name['last_name'],
            phone : current_customer_contacts['phone'],
            email : current_customer_contacts['email'],
            street : current_customer_contacts['street'],
            city : current_customer_contacts['city'],
            state : current_customer_contacts['state_code_id'],
            zipcode : current_customer_contacts['zipcode'],
            states: states
        });
        }
    });
});

// Pushes updated information to database
app.post('/customer/update', function(req, res) {
    axios.put('http://127.0.0.1:5000/customer/update',
        {   
            customer_id: req.body.customer_id,         
            first_name: req.body.firstname,
            last_name: req.body.lastname, 
            phone: req.body.phone,         
            email: req.body.email,
            street: req.body.street, 
            city: req.body.city,
            state_code_id: req.body.state,
            zipcode: req.body.zipcode   
        }) 
    .then((response)=>{
        var customer_data = response.data
        if (customer_data == "Session Timed Out! Please Log Back in" || customer_data =="No Active User Detected"){
            var flag = 1;
            var response = customer_data
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
            var message = response.data
            res.render('redirects/redirectcustomers', {message : message});
        }
        });
});

// Deletes a customer
app.post('/customer/delete', function(req, res)
{
    axios.delete('http://127.0.0.1:5000/services/delcustomer', {
        data: {
            customer_id: req.body.cussid
        }
    })
    .then((response)=>{
        var customer_data = response.data
        if (customer_data == "Session Timed Out! Please Log Back in" || customer_data =="No Active User Detected"){
            var flag = 1;
            var response = customer_data
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
            res.render('redirects/redirectcustomers', {message : customer_data});
        };
    });
});

//--------------------------------------------------------------------
// ----------------------- Commercial Customer Page ------------------
//--------------------------------------------------------------------
// Main Page of Commercial Customers
app.get('/customers/commercial', function(req, res){
    axios.get('http://127.0.0.1:5000/customers/commercial')
    .then((response)=>{
        var commcustomer_data = response.data
        if (commcustomer_data == "Session Timed Out! Please Log Back in" || commcustomer_data =="No Active User Detected"){
            var flag = 1;
            var response = commcustomer_data
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
        res.render('pages/commcustomers', {
            states: commcustomer_data[0],
            commcustomer_list: commcustomer_data[1], 
            id_dropdown: commcustomer_data[2]
            });
        }
    });
});

// Add a new commercial customer
app.post('/customers/commercial/new', function(req, res)
{
    axios.post('http://127.0.0.1:5000/customers/commercial/add',
    {           
        business_name: req.body.businessname,
        business_hrs: req.body.businesshrs, 
        phone: req.body.phone,         
        email: req.body.email,
        street: req.body.street, 
        city: req.body.city,
        state_code_id: req.body.state,
        zipcode: req.body.zipcode    
    })
    .then((response)=>{
        var message = response.data
        if (message == "Session Timed Out! Please Log Back in" || message =="No Active User Detected"){
            var flag = 1;
            var response = message
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
        res.render('redirects/redirectcommcustomers', {message : message});
        }    
    });  
});

// Gets the form for updating commerical customer information 
app.post('/customers/commercial/update/info', function(req, res){ 
    axios.post('http://127.0.0.1:5000/customers/commercial/info', 
    {
        customer_id : req.body.customer_id
    }
    
)
    .then((response)=>{
        comm_cust_data = response.data
        var current_comm_cust_name = comm_cust_data[0]
        var current_comm_cust_contacts = comm_cust_data[1]
        var states = comm_cust_data[2]
        if (comm_cust_data == "Session Timed Out! Please Log Back in" || comm_cust_data =="No Active User Detected"){
            var flag = 1;
            var response = comm_cust_data
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
        res.render('updates/updateformcommcustomer', {
            customer_id : req.body.customer_id,
            business_name : current_comm_cust_name['business_name'],
            business_hrs : current_comm_cust_name['business_hrs'],
            phone : current_comm_cust_contacts['phone'],
            email : current_comm_cust_contacts['email'],
            street : current_comm_cust_contacts['street'],
            city : current_comm_cust_contacts['city'],
            state : current_comm_cust_contacts['state_code_id'],
            zipcode : current_comm_cust_contacts['zipcode'],
            states: states
            });
        }
    });
});

// Route that pushes the update to the Database
app.post('/customers/commercial/update', function(req, res){ 
    axios.post('http://127.0.0.1:5000/customers/commercial/update', 
    {
        customer_id : req.body.customer_id,
        business_name: req.body.business_name,
        business_hrs: req.body.business_hours, 
        phone: req.body.phone,         
        email: req.body.email,
        street: req.body.street, 
        city: req.body.city,
        state_code_id: req.body.state,
        zipcode: req.body.zipcode  
    }
    )
    .then((response)=>{
    var customer_data = response.data
    if (customer_data == "Session Timed Out! Please Log Back in" || customer_data =="No Active User Detected"){
        var flag = 1;
        var response = customer_data
        res.render('pages/login', {flag: flag, response: response})
    }
    else{
        var message = response.data
        res.render('redirects/redirectcommcustomers', {message : message});
    }
    });
});


// Deletes a Commercial Customer
app.post('/customers/commercial/delete', function(req, res)
{
    axios.delete('http://127.0.0.1:5000/customers/commercial/delete', {
        data: {
            customer_id: req.body.customer_id
        }
    })
    .then((response)=>{
        var message = response.data
        if (message == "Session Timed Out! Please Log Back in" || message =="No Active User Detected"){
            var flag = 1;
            var response = message
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
        res.render('redirects/redirectcommcustomers', {message: message});
        }
    });
});

//--------------------------------------------------------------------
// --------------------------- FEEDBACK PAGE -------------------------
//--------------------------------------------------------------------
// Main Page
app.get('/customers/feedback', function(req, res){
    axios.get('http://127.0.0.1:5000/feedback')
    .then((response)=>{
        var feedback_data = response.data
        if (feedback_data == "Session Timed Out! Please Log Back in" || feedback_data =="No Active User Detected"){
            var flag = 1;
            var response = feedback_data
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
            res.render('pages/feedback', {
            customer: feedback_data[0], 
            feedback_list: feedback_data[1],
            feedback_id_dropdown: feedback_data[2],
            feedback_date : feedback_data[3]
        });
        };
    });
});

// Add new customer feedback
app.post('/customers/feedback/new', function(req, res)
{
    axios.post('http://127.0.0.1:5000/feedback/add',
    {           
        customer: req.body.customer,
        customer_comments: req.body.feedback,
        feedback_date: req.body.feedbackdate         
    })
    .then((response)=>{
        var message = response.data
        if (message == "Session Timed Out! Please Log Back in" || message =="No Active User Detected"){
            var flag = 1;
            var response = message
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
            res.render('redirects/redirectfeedback', {message : message
        });
        }
    });  
});

// Redirects to customer update form 
app.post('/customers/feedback/update/info', function(req, res){
    axios.post('http://127.0.0.1:5000/feedback/info', 
    {
        feedback_id : req.body.feedid
    }
    
)
    .then((response)=>{
        message = response.data
        var current_feedback_data = message[0][0]
        var customer_name = message[1][0]
        var feedback_date = message[2]
        var customer_drop = message[3]
        if (message == "Session Timed Out! Please Log Back in" || message =="No Active User Detected"){
            var flag = 1;
            var response = message
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
        res.render('updates/updateformfeedback', {
            feedback_id : req.body.feedid,
            customer_id: current_feedback_data["customer_id"],
            customer_fname : customer_name["first_name"],
            customer_lname: customer_name["last_name"],
            customer: customer_drop,
            customer_comments : current_feedback_data['customer_comments'],
            feedback_date : feedback_date,

        });
        }
    });
});

// Pushes updates to the database from the forms
app.post('/customers/feedback/update', function(req, res) {
    axios.put('http://127.0.0.1:5000/feedback/update',
        {           
            feedback_id : req.body.feedback_id,
            customer : req.body.customer,
            customer_comments: req.body.customer_comments,
            feedback_date: req.body.feedback_date       
        }
    ) 
    .then((response)=>{
        var feedback_data = response.data
        if (feedback_data == "Session Timed Out! Please Log Back in" || feedback_data =="No Active User Detected"){
            var flag = 1;
            var response = feedback_data
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
            var message = response.data
            res.render('redirects/redirectfeedback', {message : message});
        }
        });
});

// Deletes a customer feedback based on feedback_id
app.post('/customers/feedback/delete', function(req, res)
{
    axios.delete('http://127.0.0.1:5000/feedback/delete', {
        data: {
            feedback_id: req.body.feedid
        }
    })
    .then((response)=>{
        var message = response.data
        if (message == "Session Timed Out! Please Log Back in" || message =="No Active User Detected"){
            var flag = 1;
            var response = message
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
        res.render('redirects/redirectfeedback', {message: message
            });
        }
    });
});

//--------------------------------------------------------------------
// ------- TOOL/CHEM/TOOL MAINTAIN/LICENSES INVENTORY PAGE -----------
//--------------------------------------------------------------------
// Main page
app.get('/inventory', function(req, res)
{
    axios.get('http://127.0.0.1:5000/inventory')
    .then((response)=>{
        var message = response.data
        if (message == "Session Timed Out! Please Log Back in" || message =="No Active User Detected"){
            var flag = 1;
            var response = message
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
            var tool_data = response.data[0]
            var chemical_data = response.data[1]
            var repair_data = response.data[2]
            var license_data = response.data[3]
            var equipment_data = response.data[4]
            var suppliers = response.data[5]
            res.render('pages/inventory', {
            tool_list: tool_data, 
            chemical_list: chemical_data, 
            repair_list: repair_data, 
            license_list: license_data, 
            equipment_list: equipment_data,
            suppliers_list: suppliers
        });
        }
    });

});


// ***** Tools Subsection **
// Adds a new tool 
app.post('/tool/new', function(req, res) {
    try
    {
        axios.post('http://127.0.0.1:5000/inventory/tools/add',
        {           
            equipment_name: req.body.toolname,
            equipment_type: req.body.tooltype, 
            quality: req.body.quality,
            supplier_id: req.body.supplier_id
        })
        .then((response)=>{
            var message = response.data
            if (message == "Session Timed Out! Please Log Back in" || message =="No Active User Detected"){
                var flag = 1;
                var response = message
                res.render('pages/login', {flag: flag, response: response})
            }
            else{
            res.render('redirects/redirectinventory', {message : message});
            }
        });  
    }
    catch(error)
    {
        console.log(error)
    }
        
});

// Redirects to the chemicla update form NOT DONE
app.post('/tools/update/info', function(req, res){
    axios.post('http://127.0.0.1:5000/inventory/tools/info', 
    {
        equipment_id : req.body.tool_list
    }
    
)
    .then((response)=>{
        var message = response.data
        if (message == "Session Timed Out! Please Log Back in" || message =="No Active User Detected"){
            var flag = 1;
            var response = message
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
            console.log(response.data[0])
            var current_tool_data = response.data[0][0]
            var suppliers_list = response.data[1]
            res.render('updates/updateformtools', {
                suppliers_list: suppliers_list,
                current_tool_data: current_tool_data
               
            });
        }
    });
});

// Pushes updated information to the database NOT DONE
app.post('/tools/update', function(req, res) {
    axios.put('http://127.0.0.1:5000/inventory/tools/update',
        {           
            equipment_id : req.body.equipment_id,
            equipment_name: req.body.toolname,
            equipment_type: req.body.tooltype,
            quality: req.body.quality,
            supplier_id: req.body.supplier_id       
        }
    ) 
    .then((response)=>{
        var service_data = response.data
        if (service_data == "Session Timed Out! Please Log Back in" || service_data =="No Active User Detected"){
            var flag = 1;
            var response = service_data
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
            var message = response.data
            res.render('redirects/redirectinventory', {message : message});
        }
        });
});

// "Deletes" a tool from the inventory
app.post('/tool/delete', function(req, res)
{
    axios.put('http://127.0.0.1:5000/inventory/tools/delete', {
        equipment_id: req.body.tool_list
    })
    .then((response)=>{
        var message = response.data
        res.render('redirects/redirectinventory', {message: message})
    });
    //res.render('redirects/loggedin')
});


// ***** Chemcial Subsection ** 
// Adds a new chemcial 
app.post('/chemical/new', function(req, res){
    try
    {
        axios.post('http://127.0.0.1:5000/inventory/chemcials/add',
        {           
            chemical_name: req.body.chemicalname,
            chemcial_type: req.body.chemcialtype, 
            supplier_id: req.body.supplier_id,
            license_id: req.body.license_id
        })
        .then((response)=>{
            var message = response.data
            res.render('redirects/redirectinventory', {message : message});
        });  
    }
    catch(error)
    {
        console.log(error)
    }
        
});

// Redirects to the chemicla update form
app.post('/chemical/update/info', function(req, res){
    axios.post('http://127.0.0.1:5000//inventory/chemical/info', 
    {
        chemical_id : req.body.chemical_id
    }
    
)
    .then((response)=>{
        var current_chemical_data = response.data[0]
        var suppliers_list = response.data[1]
        var license_list = response.data[2]
        res.render('updates/updateformchemical', {
            chemical_id : req.body.chemical_id,
            current_chemical_data: current_chemical_data[0],
            suppliers_list: suppliers_list,
            license_list: license_list
           
        });
    });
});

// Pushes updated information to the database 
app.post('/chemical/update', function(req, res) {
    axios.put('http://127.0.0.1:5000/inventory/chemical/update',
        {   
            chemical_id: req.body.chemical_id,        
            chemical_name: req.body.chemicalname,
            chemcial_type: req.body.chemcialtype, 
            supplier_id: req.body.supplier_id,
            license_id: req.body.licenses_id       
        }
    ) 
    .then((response)=>{
        var service_data = response.data
        if (service_data == "Session Timed Out! Please Log Back in" || service_data =="No Active User Detected"){
            var flag = 1;
            var response = service_data
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
            var message = response.data
            res.render('redirects/redirectinventory', {message : message});
        }
        });
});

// Deletes a chemcial based on the chemcial_id
app.post('/chemicals/delete', function(req, res)
{
    axios.put('http://127.0.0.1:5000/inventory/chemical/delete', {
        chemical_id: req.body.chemical_list
    })
    .then((response)=>{
        var message = response.data
        res.render('redirects/redirectinventory', {message: message})
    });
});

// ***** Tool Maintenance Subsection **
// Add new tool maintenance information
app.post('/repair/new', function(req, res){
    try
    {
        axios.post('http://127.0.0.1:5000/inventory/repair/add',
        {           
            equipment_list: req.body.equipment_list,
            repair_status: req.body.repairstatus,
            date_repair_start: req.body.daterepairstart,
            repair_comments: req.body.repaircomments
        })
        .then((response)=>{
            var message = response.data
            res.render('redirects/redirectinventory', {message : message});
        });  
    }
    catch(error)
    {
        console.log(error)
    }
    
});

// Redirects to the chemicla update form
app.post('/repair/update/info', function(req, res){
    console.log()
    axios.post('http://127.0.0.1:5000/inventory/repair/info', 
    {
        repair_id : req.body.repair_list
    }
    
)
    .then((response)=>{
        repair_data = response.data
        var current_repair_data = repair_data[0]
        var repair_date = repair_data[1]
        
        res.render('updates/updateformrepair', {
            repair_id: current_repair_data['repair_id'],
            repair_status: current_repair_data['repair_status'],
            date_repair_start: repair_date,
            repair_comments: current_repair_data['repair_comments'],
            
        });
    });
});

app.post('/repair/update', function(req, res) {
    axios.put('http://127.0.0.1:5000/inventory/repair/update',
        {           
            repair_id : req.body.repair_list,
            repair_status: req.body.repair_status,
            date_repair_start: req.body.date_repair_start,   
            repair_comments: req.body.repair_comments      
        }
    ) 
    .then((response)=>{
        var service_data = response.data
        if (service_data == "Session Timed Out! Please Log Back in" || service_data =="No Active User Detected"){
            var flag = 1;
            var response = service_data
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
            var message = response.data
            res.render('redirects/redirectinventory', {message : message});
        }
        });
});

// Deletes Tool Maintence Information
app.post('/repair/delete', function(req, res)
{
    //axios
    axios.put('http://127.0.0.1:5000/inventory/repair/delete', {
        repair_id: req.body.repair_list
    })
    .then((response)=>{
        var message = response.data
        res.render('redirects/redirectinventory', {message: message})
    });
});


// ***** Licenses Subsection **
// adds a new license
app.post('/license/add', function(req, res){
    try
{
    axios.post('http://127.0.0.1:5000/inventory/license/add',
    {           
        license_name: req.body.license_name,
        license_description: req.body.license_description, 
        license_expiration_date: req.body.license_expiration_date       
    })
    .then((response)=>{
        var message = response.data
        res.render('redirects/redirectinventory', {message : message});
    });  
}
catch(error)
{
    console.log(error)
}
    
});

// Redirect to Update form for licenses information
app.post('/license/update/info', function(req, res){
    axios.post('http://127.0.0.1:5000/inventory/license/info', 
    {
        license_id : req.body.license_list
    }
    
)
    .then((response)=>{
        var current_license_data = response.data[0]

        res.render('updates/updateformlicense', {
            current_license_data: current_license_data
        });
    });
});

// Push for updated information of licenses 
app.post('/license/update', function(req, res) {
    axios.put('http://127.0.0.1:5000/inventory/license/update',
        {           
            license_id : req.body.license_id,
            license_name: req.body.license_name,
            license_description: req.body.license_description,
            license_expiration_date: req.body.license_expiration_date       
        }
    ) 
    .then((response)=>{
        var service_data = response.data
        if (service_data == "Session Timed Out! Please Log Back in" || service_data =="No Active User Detected"){
            var flag = 1;
            var response = service_data
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
            var message = response.data
            res.render('redirects/redirectinventory', {message : message});
        }
        });
});

// Delete a license based on the License_id
app.post('/license/delete', function(req, res)
{
    //axios
    axios.put('http://127.0.0.1:5000/inventory/license/delete', {
        license_id: req.body.license_list
    })
    .then((response)=>{
        var message = response.data
        res.render('redirects/redirectinventory', {message: message})
    });
});



//--------------------------------------------------------------------
// ------------------- VEHICLE INVENTORY PAGE ------------------------
//--------------------------------------------------------------------
// Main Page
app.get('/vehicles', function(req, res){
    axios.get('http://127.0.0.1:5000/inventory/vehicle')
    .then((response)=>{
        var vehicle_data = response.data
        res.render('pages/vehicles', {

            vehicle_list: vehicle_data[0],
            vehicle_main: vehicle_data[1],
            employees: vehicle_data[2],
            car_list: vehicle_data[3],
            vehicleivt: vehicle_data[4]
        })
        
    });
});

// ***** Vehicles Subsection **
app.post('/vehicle/new', function(req, res){
    try
    {
        axios.post('http://127.0.0.1:5000/inventory/vehicle/add',
        {           
            vehicle_name: req.body.vehicle,
            vehicle_vin: req.body.vin, 
            vehicle_license: req.body.license,   
            vehicle_status: req.body.vehiclestatus
        })
        .then((response)=>{
            var message = response.data
            res.render('redirects/redirectvehicles', {message : message});
        });  
    }
    catch(error)
    {
        console.log(error)
    }
        
    });

// Redirects to the chemicla update form
app.post('/vehicle/update/info', function(req, res){
    console.log()
    axios.post('http://127.0.0.1:5000/inventory/vehicle/info', 
    {
        vehicle_id : req.body.vehicle_list
    }
    
)
    .then((response)=>{
        vehicle_data = response.data
        var current_vehicle_data = vehicle_data
        res.render('updates/updateformvehicle', {
            current_vehicle_data: current_vehicle_data[0]
            
        });
    });
});

app.post('/vehicle/update', function(req, res) {
    axios.put('http://127.0.0.1:5000/inventory/vehicle/update',
        {           
            vehicle_id : req.body.vehicle_id,
            vehicle_name: req.body.vehicle_name,
            vehicle_vin: req.body.vehicle_vin,   
            vehicle_license: req.body.vehicle_license,
            vehicle_status: req.body.vehicle_status      
        }
    ) 
    .then((response)=>{
        var service_data = response.data
        if (service_data == "Session Timed Out! Please Log Back in" || service_data =="No Active User Detected"){
            var flag = 1;
            var response = service_data
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
            var message = response.data
            res.render('redirects/redirectvehicles', {message : message});
        }
        });
});

// Deactivates a vehicle 
app.post('/vehicle/deactivate', function(req, res)
{
    axios.put('http://127.0.0.1:5000/inventory/vehicle/delete',
    {
        vehicle_id : req.body.vehicle_id
    })
    .then((response)=>{
        var message = response.data
        res.render('redirects/redirectvehicles', {message: message})
    });
});

// ***** Vehicle Information Subsection **
app.post('/vehicle/information/new', function(req, res){
    try
    {
        axios.post('http://127.0.0.1:5000/inventory/vehicle/info/add',
        {           
            car_list: req.body.car_list,
            insurance_info : req.body.insuranceinfo,
            next_inspection_date: req.body.nextinspectdate,
            
        })
        .then((response)=>{
            var message = response.data
            res.render('redirects/redirectvehicles', {message : message});
        });  
    }
    catch(error)
    {
        console.log(error)
    }

    });

// Redirects to the vehicle information update form
app.post('/vehicle/information/update/info', function(req, res){
    axios.post('http://127.0.0.1:5000/inventory/vehicle/info/update/info', 
{
    vehicle_info_id : req.body.vehicle_list
}

)
.then((response)=>{ 
    var current_vehicleinfo_data = response.data[0]
    var vehicle_dropdown = response.data[1]

    res.render('updates/updateformvehicleinformation', {
        current_vehicleinfo_data: current_vehicleinfo_data[0],
        car_list: vehicle_dropdown
        
    });
});
});

app.post('/vehicle/information/update', function(req, res) {
    axios.put('http://127.0.0.1:5000/inventory/vehicle/info/update',
        {           
            vehicle_info_id : req.body.vehicle_info_id,
            insurance_info: req.body.insurance_info,
            next_inspection_date: req.body.next_inspection_date,

        }
    ) 
    .then((response)=>{
        var service_data = response.data
        if (service_data == "Session Timed Out! Please Log Back in" || service_data =="No Active User Detected"){
            var flag = 1;
            var response = service_data
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
            var message = response.data
            res.render('redirects/redirectvehicles', {message : message});
        }
        });
});

// Pushes updated vehicle information to the DB
app.post('/vehicle/information/delete', function(req, res){
    axios.put('http://127.0.0.1:5000/inventory/vehicle/info/delete',{
        vehicle_info_id: req.body.vehicleinfoid
    })
    .then((response)=>{
        var message = response.data
        res.render('redirects/redirectvehicles', {message: message})    
    });


});

// ** Vehicle maintenance Subsection **
// Adds new vehicle maintenance Inforamtion
app.post('/vehicle/maintenance/new', function(req, res){
    try
    {
        axios.post('http://127.0.0.1:5000/inventory/vehicles/maintenance/add',
        {           
            car_list: req.body.car_list,
            employees: req.body.employees,
            service_date: req.body.servicedate,
            maintenance_comments: req.body.maintcomment
        })
        .then((response)=>{
            var message = response.data
            res.render('redirects/redirectvehicles', {message : message});
        });  
    }
    catch(error)
    {
        console.log(error)
    }

    });

// Update form for vehicle maintenance
app.post('/vehicle/maintenance/update/info', function(req, res){
    axios.post('http://127.0.0.1:5000/inventory/vehicles/maintenance/info', 
    {
        maintenance_id : req.body.vehicle_main
    }

    )
    .then((response)=>{
        maintenance_data = response.data
        var current_maintenance_data = maintenance_data[0]
        var current_car_data = maintenance_data[1]
        var current_employee_data = maintenance_data[2]
        res.render('updates/updateformmaintenance', {
            current_maintenance_data: current_maintenance_data[0],
            vehicle_id: current_car_data,
            employee_list: current_employee_data
            
        });
    });
    });

// Update push for vehicle maintenance
app.post('/vehicle/maintenance/update', function(req, res) {
    axios.put('http://127.0.0.1:5000/inventory/vehicles/maintenance/update',
        {           
            maintenance_id : req.body.maintenance_id,
            service_date: req.body.service_date,   
            employee_id: req.body.employee_id,
            maintenance_comments: req.body.maintenance_comments

        }
    ) 
    .then((response)=>{
        var service_data = response.data
        if (service_data == "Session Timed Out! Please Log Back in" || service_data =="No Active User Detected"){
            var flag = 1;
            var response = service_data
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
            var message = response.data
            res.render('redirects/redirectvehicles', {message : message});
        }
        });
});

// Deletes vehicle maintenance information 
app.post('/vehicle/maintenance/delete', function(req, res){
    axios.put('http://127.0.0.1:5000/inventory/vehicles/maintenance/delete',{
        maintenance_id: req.body.maintenance_id
    })
    .then((response)=>{
        var message = response.data
        res.render('redirects/redirectvehicles', {message: message})    
    });



});



//--------------------------------------------------------------------
// --------------------------- SUPPLIER PAGE -------------------------
//--------------------------------------------------------------------
// Main Page
app.get('/supply', function(req, res){
    axios.get('http://127.0.0.1:5000/supliers')
    .then((response)=>{
        var supply_data = response.data
        res.render('pages/supply', {
            equipment_list: supply_data[0],
            states: supply_data[1],
            supplier_list: supply_data[2]
        })
        
    });
});

// Adds a new supply
app.post('/supply/add', function(req, res){
    try
    {
        axios.post('http://127.0.0.1:5000/supliers/add',
        {           
            supplier_name: req.body.suppliername,
            phone : req.body.phone,
            email : req.body.email,
            street : req.body.street,
            city : req.body.city,
            states : req.body.states,
            zipcode: req.body.zipcode
        })
        .then((response)=>{
            var message = response.data
            res.render('redirects/redirectsupply', {message : message});
        });  
    }
    catch(error)
    {
        console.log(error)
    }

    });

// Redirects to the Suppliers update form 
app.post('/supplier/update/info', function(req, res){
    axios.post('http://127.0.0.1:5000/suppliers/update/info', 
    {
        sup_contact_id : req.body.supplier_list
    }

    )
    .then((response)=>{
        supplier_data = response.data
        var current_supplier_data = supplier_data[0]
        var current_states_data = supplier_data[1]
        res.render('updates/updateformsupplier', {
            current_supplier_data: current_supplier_data[0],
            states: current_states_data
            
        });
    });
    });

// Pushes the Updated Information
app.post('/supplier/update', function(req, res) {
    axios.put('http://127.0.0.1:5000/suppliers/update',
        {           
            sup_contact_id : req.body.sup_contact_id,
            supplier_name: req.body.supplier_name,
            phone: req.body.phone,   
            email: req.body.email,
            street: req.body.street,
            city: req.body.city,
            states: req.body.states,
            zipcode: req.body.zipcode

        }
    ) 
    .then((response)=>{
        var service_data = response.data
        if (service_data == "Session Timed Out! Please Log Back in" || service_data =="No Active User Detected"){
            var flag = 1;
            var response = service_data
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
            var message = response.data
            res.render('redirects/redirectsupply', {message : message});
        }
        });
});

// Deletes suppliers
app.post('/supply/delete', function(req, res){
    axios.put('http://127.0.0.1:5000/suppliers/delete',
        {
            supplier_id: req.body.supplier_id
        }
    )
    .then((response)=>{
    var service_data = response.data
    if (service_data == "Session Timed Out! Please Log Back in" || service_data =="No Active User Detected"){
        var flag = 1;
        var response = service_data
        res.render('pages/login', {flag: flag, response: response})
    }
    else{
        var message = response.data
        res.render('redirects/redirectsupply', {message : message
            });
        }
    });
});



//--------------------------------------------------------------------
// ----------------- EQUIPMENT DEPLOYMENT PAGE -----------------------
//--------------------------------------------------------------------
// Main page
app.get('/equipdeploy', function(req, res){
    axios.get('http://127.0.0.1:5000/jobs/equipment_deployment')
    .then((response)=>{
        var table = response.data[0]
        var deploy_id_dropdown = response.data[1]
        var tools = response.data[2]
        var chemicals = response.data[3]
        var vehicles = response.data[4]
        var appoint_dates = response.data[5]
        res.render('pages/equipdeploy', {
            equip_table: table,
            deploy_id_dropdown: deploy_id_dropdown,
            tools: tools,
            chemicals: chemicals,
            vehicles: vehicles,
            appoint_dates:  appoint_dates  
        });
    });
});

app.post('/equipdeploy/add', function(req, res) {
    // var add_scheddate = req.body.add_scheddate;
    var chemical = req.body.chemical_id;
    var tool = req.body.equipment_id;
    var vehicle = req.body.vehicle_id;
    var equip_status = req.body.equip_status;
    var add_scheddate = req.body.add_scheddate

        axios.post('http://127.0.0.1:5000/jobs/equipment_deployment/add', {
            // add_scheddate: add_scheddate,
            chemical: chemical,
            tool: tool,
            vehicle: vehicle,
            equip_status: equip_status,
            add_scheddate: add_scheddate
    })
    .then((response)=>{
        var message = response.data
        res.render('redirects/redirectequipdeploy', {message: message});
    });

});

// Redirects to the equipment Deployemnt update form ** NOT DONE **
app.post('/equipdeploy/update/info', function(req, res)
{
    axios.post('http://127.0.0.1:5000/jobs/equipment_deployment/update/info', {deployid: req.body.deployid})
    .then((response)=>{
    var current_info = response.data[0]
    var equip_table = response.data[1]
    var chemicals = response.data[2]
    var vehicles = response.data[3]
    var tools = response.data[4]
    var appoints_list = response.data[5]
    res.render('updates/updateformequipdeploy', {
        current_info: current_info[0],
        equip_table: equip_table,
        tools: tools,
        chemicals: chemicals,
        vehicles: vehicles,
        appoints_list: appoints_list   
    });
});
    
});

// Pushes updated equipment Deployment Information to the DB ** NOT DONE ** 
app.post('/equipdeploy/update', function(req, res)
{
    axios.put('http://127.0.0.1:5000/jobs/equipment_deployment/update',{
        deploy_id : req.body.deploy_id,
        chemical_id: req.body.chemical_id,
        equipment_id : req.body.equipment_id,
        vehicle_id: req.body.vehicle_id,
        equip_status: req.body.equip_status
    })
    .then((response)=>{
    var message = response.data
    if (message == "Session Timed Out! Please Log Back in" || message =="No Active User Detected"){
        var flag = 1;
        var response = message
        res.render('pages/login', {flag: flag, response: response})
    }
    else{
        
        res.render('redirects/redirectequipdeploy', {message : message
            });
        }
    });
    
});

// Deletes an Equipment Deployemnt Entry ** NOT DONE **
app.post('/equipdeploy/delete', function(req, res)
{
    axios.put('http://127.0.0.1:5000/jobs/equipment_deployment/delete',{
        deploy_id : req.body.deploy_id
    })
    .then((response)=>{
    var message = response.data
    if (message == "Session Timed Out! Please Log Back in" || message =="No Active User Detected"){
        var flag = 1;
        var response = message
        res.render('pages/login', {flag: flag, response: response})
    }
    else{
        
        res.render('redirects/redirectequipdeploy', {message : message
            });
        }
    });
});

//--------------------------------------------------------------------
// ------------------- ADMIN SECTION LOGIN PAGE ----------------------
//--------------------------------------------------------------------
app.get('/admin_info', function(req, res) {
    var flag = 0;
    res.render('pages/adminvalidation_empinfo', {flag: flag
    });
});

app.get('/admin_accounts', function(req, res) {
    var flag = 0;
    res.render('pages/adminvalidation_accounts', {flag: flag
    });
})

app.post('/admin_validation_empinfo', function(req, res) {
    axios.get('http://127.0.0.1:5000/admin_validation', {
        data:
        {
            username: req.body.username,
            password: req.body.password
        }
    }).then((response)=>
        {   
            var privilege = response.data[1]
            var message = 'Employee Information'

        
            if (privilege == 1) {
                res.render('pages/valid_empinfo', {body: req.body, message: message})
            }
            else if (privilege == 2) {
                flag = 1
                var not_valid = 'You do not have access to this page'
                res.render('pages/adminvalidation_empinfo', {body: req.body, flag: flag, not_valid: not_valid})
            }
            else {
                var flag = 2;
                var response = response.data
                res.render('pages/adminvalidation_empinfo', {body: req.body, flag: flag, response: response})
            }
        }
    )
});

app.post('/admin_validation_accounts', function(req, res) {
    axios.get('http://127.0.0.1:5000/admin_validation', {
        data:
        {
            username: req.body.username,
            password: req.body.password
        }
    }).then((response)=>
        {   
            var privilege = response.data[1]
            var message = 'Employee Accounts'

        
            if (privilege == 1) {
                res.render('pages/valid_accounts', {body: req.body, message: message})
            }
            else if (privilege == 2) {
                flag = 1
                var not_valid = 'You do not have access to this page'
                res.render('pages/adminvalidation_accounts', {body: req.body, flag: flag, not_valid: not_valid})
            }
            else {
                var flag = 2;
                var response = response.data
                res.render('pages/adminvalidation_accounts', {body: req.body, flag: flag, response: response})
            }
        }
    )
});

//--------------------------------------------------------------------
// ---------------------- ADMIN/EMPLOYEE PAGE ------------------------
//--------------------------------------------------------------------
// Main Page 
app.get('/employees', function(req, res){
    axios.get('http://127.0.0.1:5000/employee')
    .then((response)=>{
        var employee_data = response.data
        res.render('pages/empinfo', 
        {states: employee_data[0],
        role_list: employee_data[1],
        employee_list: employee_data[2],
        login_info: employee_data[3],
        employee_dropdown: employee_data[4]
    })
    });
});
// Adds new employee information
app.post('/employees/new', function(req, res)
{
    axios.post('http://127.0.0.1:5000/admin/addemployee',
    {           

        first_name: req.body.firstname,
        last_name: req.body.lastname,
        employee_status: req.body.empstatus,
        role_list: req.body.role_list,
        emp_phone: req.body.empphone,         
        emp_email: req.body.empemail,
        emp_street: req.body.empstreet, 
        emp_city: req.body.empcity,
        states: req.body.states,
        emp_zipcode: req.body.empzipcode    
    })
    .then((response)=>{
        var message = response.data
        res.render('redirects/redirectemployees', {message : message});
    });  
});

app.post('/employee/update/info', function(req, res){
    axios.post('http://127.0.0.1:5000/employee/info', 
    {
        emp_cnt_id : req.body.employee_list
    }

    )
    .then((response)=>{
        employee_data = response.data
        var current_employee_data = employee_data[0]
        var current_roles_data = employee_data[1]
        var current_states_data = employee_data[2]
        res.render('updates/updateformemployee', {
            current_employee_data: current_employee_data[0],
            role_id: current_roles_data,
            states: current_states_data
            
        });
    });
    });

app.post('/employee/update', function(req, res) {
    axios.put('http://127.0.0.1:5000/employee/update',
        {           
            emp_cnt_id : req.body.emp_cnt_id,
            first_name: req.body.first_name,
            last_name: req.body.last_name,
            employee_status: req.body.employee_status,
            role_id: req.body.role_id,
            emp_phone: req.body.emp_phone,         
            emp_email: req.body.emp_email,
            emp_street: req.body.emp_street, 
            emp_city: req.body.emp_city,
            states: req.body.states,
            emp_zipcode: req.body.emp_zipcode  

        }
    ) 
    .then((response)=>{
        var message = response.data
        if (message == "Session Timed Out! Please Log Back in" || message =="No Active User Detected"){
            var flag = 1;
            var response = message
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
            var message = response.data
            res.render('redirects/redirectemployees', {message : message});
        }
        });
});

// "Deletes" Employee Information 
app.post('/employees/delete', function(req, res)
{
    axios.put('http://127.0.0.1:5000/employee/delete' , {
        employee_id : req.body.employee_id
    })
    .then((response)=>{
    var message = response.data
    if (message == "Session Timed Out! Please Log Back in" || message =="No Active User Detected"){
        var flag = 1;
        var response = message
        res.render('pages/login', {flag: flag, response: response})
    }
    else{
        
        res.render('redirects/redirectemployees', {message : message});
    }
    });
});

// Real Delete Employee Information 
app.post('/employees/delete/true', function(req, res)
{
    axios.put('http://127.0.0.1:5000/employee/truedelete' , {
        employee_id : req.body.employee_id
    })
    .then((response)=>{
    var message = response.data
    if (message == "Session Timed Out! Please Log Back in" || message =="No Active User Detected"){
        var flag = 1;
        var response = message
        res.render('pages/login', {flag: flag, response: response})
    }
    else{
        
        res.render('redirects/redirectemployees', {message : message});
    }
    });
});
//--------------------------------------------------------------------
// ----- SYSTEMS PRIVLAGES/SECURITY INFORMATION PAGE -----------------
//--------------------------------------------------------------------
// Main page
app.get('/accounts', function(req, res){
    axios.get('http://127.0.0.1:5000/employee/admin/security_information')
    .then((response)=>{
        var security_data = response.data
        res.render('pages/systemprivileges', 
        {employee_list: security_data[0],
        systempriv_list: security_data[1],
        security_list: security_data[2]})
    });
});

// Adds a new account
app.post('/account/new', function(req, res)
{
    axios.post('http://127.0.0.1:5000/admin/addsyspriv',
    {           
        employee_list: req.body.employee_list,
        systempriv_list: req.body.systempriv_list,
        username: req.body.username,
        user_password: req.body.user_password         
    })
    .then((response)=>{
        var message = response.data

        res.render('redirects/redirectaccounts', {message : message});
    });  
});

app.post('/account/update/info', function(req, res){
    axios.post('http://127.0.0.1:5000/system_privilege/info', 
    {
        account_id : req.body.security_list
    }

    )
    .then((response)=>{
        account_data = response.data
        var current_account_data = account_data[0]
        var current_privilege_data = account_data[1]
        res.render('updates/updateformaccount', {
            current_account_data: current_account_data[0],
            privilege_id: current_privilege_data
        });
    });
    });

app.post('/acount/update', function(req, res) {
    axios.put('http://127.0.0.1:5000/system_privilege/update',
        {           
            account_id : req.body.account_id,
            username : req.body.username,
            user_password: req.body.user_password,
            privilege_id: req.body.privilege_id
            

        }
    ) 
    .then((response)=>{
        var service_data = response.data
        if (service_data == "Session Timed Out! Please Log Back in" || service_data =="No Active User Detected"){
            var flag = 1;
            var response = service_data
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
            var message = response.data
            res.render('redirects/redirectaccounts', {message : message});
        }
        });
});

app.post('/account/delete', function(req, res)
{
    axios.put('http://127.0.0.1:5000//admin/delsyspriv', {
        account_id: req.body.login_info
    })
    .then((response)=>{
        var message = response.data
        res.render('redirects/redirectaccounts', {message: message})
    });
});

//--------------------------------------------------------------------
// ------------------------ INVOICE PAGE -----------------------------
//--------------------------------------------------------------------
// Invoice Main Page
app.get('/invoice', function(req, res){
    axios.get('http://127.0.0.1:5000/invoice')
    .then((response)=>{
        var invoice_data = response.data
        res.render('pages/invoice', {
            quote_list: invoice_data[0], 
            invoice_list: invoice_data[1], 
            invoice_id_dropdown: invoice_data[2]
        });
    });
});

// Redirect To the Update form for the Invoice Page
app.post('/invoice/update/info', function(req, res){
    axios.post('http://127.0.0.1:5000/invoice/info', 
    {
        invoice_id : req.body.invoice_id
    }
    
)
    .then((response)=>{
        var current_invoice_data = response.data[0]
        var quotes_dropdown = response.data[1]
        res.render('updates/updateforminvoice', {
            invoice_id : req.body.invoice_id,
            invoice_data: current_invoice_data[0],
            quotes_dropdown: quotes_dropdown
        });
    });
});

// Push Updated Information for Invoices to the Database
app.post('/invoice/update', function(req, res) {
    axios.put('http://127.0.0.1:5000/invoice/update',
        {           
            invoice_id : req.body.invoice_id,
            quote_id : req.body.quote_id,
            invoice_status: req.body.invoice_status,
            comments: req.body.comments,
            actual_total: req.body.actual_total,
            due_date: req.body.due_date       
        }
    ) 
    .then((response)=>{
        var invoice_data = response.data
        if (invoice_data == "Session Timed Out! Please Log Back in" || invoice_data =="No Active User Detected"){
            var flag = 1;
            var response = invoice_data
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
            var message = response.data
            res.render('redirects/redirectinvoice', {message : message});
        }
        });
});

// Deletes an invoice based on invoice_id
app.post('/invoice/delete', function(req, res) {
    axios.put('http://127.0.0.1:5000/invoice/delete',
        {           
            invoice_id : req.body.invoice_id      
        }
        
    ) 
    .then((response)=>{
        var service_data = response.data
        if (service_data == "Session Timed Out! Please Log Back in" || service_data =="No Active User Detected"){
            var flag = 1;
            var response = service_data
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
            var message = response.data
            res.render('redirects/redirectinvoice', {message : message});
        }
        });
});


//--------------------------------------------------------------------
// ------------------------- QUOTE PAGE ------------------------------
//--------------------------------------------------------------------
// Main Page 
app.get('/quote', function(req, res){
    //pass
    axios.get('http://127.0.0.1:5000/sales/quote')
    .then((response)=>{
        var quote_data = response.data
        res.render('pages/quote', {quote_list: quote_data[0], service_list: quote_data[1]});
    });
});


// Redirects to the update form for quote information
app.post('/quote/update/info', function(req, res){
    axios.post('http://127.0.0.1:5000/quote/info', 
    {
        quote_id : req.body.quote_list
    }
    
)
    .then((response)=>{
        var current_quote_data = response.data[0]
        var services = response.data[1]
        res.render('updates/updateformquote', {
            quote_id : req.body.quote_list,
            service_list : services,
            current_quote_data: current_quote_data[0]
        });
    });
});

// Pushes updated information for quote to the Database
app.post('/quote/update', function(req, res) {
    axios.put('http://127.0.0.1:5000/quote/update',
        {           
            quote_id : req.body.quote_id,
            service_list: req.body.service_list,
            comments: req.body.comments,
            total_cost: req.body.total_cost     
        }
    ) 
    .then((response)=>{
        var invoice_data = response.data
        if (invoice_data == "Session Timed Out! Please Log Back in" || invoice_data =="No Active User Detected"){
            var flag = 1;
            var response = invoice_data
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
            var message = response.data
            res.render('redirects/redirectquote', {message : message});
        }
        });
});

// Deletes a quote 
app.post('/quote/delete', function(req, res)
{
    axios.put('http://127.0.0.1:5000/quote/delete' ,{
        quote_id : req.body.quote_id   
    })
    .then((response)=>{
        var invoice_data = response.data
        if (invoice_data == "Session Timed Out! Please Log Back in" || invoice_data =="No Active User Detected"){
            var flag = 1;
            var response = invoice_data
            res.render('pages/login', {flag: flag, response: response})
        }
        else{
            var message = response.data
            res.render('redirects/redirectquote', {message : message});
        }
        });
});




app.listen(8080);
console.log('Application now listening on port 8080');
