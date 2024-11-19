import streamlit as st
import mysql.connector
import logging

# Database connection
def create_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Dhan",
        database="hospitaldb"
    )
    return conn

# Function to dynamically load book.py for patients
def run_book_script():
    import book  # Assume book.py contains patient-related functionality

# Function to dynamically load doc.py for doctors
def run_doc_script(doctor_id):
    import doc  # Assume doc.py contains doctor-related functionality
    doc.show_schedule(doctor_id)  # Assuming this function shows the doctor's schedule

# Function to dynamically load admin.py for admins
def run_admin_script():
    import admin  # Assume admin.py contains admin-related functionality
    admin.manage_waitlist()  # Assuming this function manages the admin waitlist

# Logger setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('hospital_app.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Verify user credentials
def verify_user(username, password):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM users WHERE username = %s AND password = %s"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        logger.info(f"Successful login attempt by {username}")
    else:
        logger.warning(f"Failed login attempt by {username}")
    return user

# Function to create a new user account with plaintext password
def create_account(username, password, role, additional_info):
    conn = create_connection()
    cursor = conn.cursor()

    # Check if the username already exists
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    existing_user = cursor.fetchone()

    if existing_user:
        st.error("Username already exists. Please choose another one.")
        conn.close()
        return

    # Insert the new user into the `users` table
    query = "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)"
    cursor.execute(query, (username, password, role))
    user_id = cursor.lastrowid  # Get the user ID of the newly inserted user

    # Insert additional info based on role
    if role == "patient":
        query = """INSERT INTO Patients (PatientID, Name, EmailID, Address, Date_Of_Birth, 
                  PhoneNo, Gender, Password, IsPESStudent, SRN) 
                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(query, (user_id, additional_info['name'], additional_info['email'], 
                               additional_info['address'], additional_info['dob'], 
                               additional_info['phone'], additional_info['gender'], 
                               password, additional_info['is_pes_student'], additional_info['srn']))

    elif role == "doctor":
        query = """INSERT INTO Doctors (DoctorID, Name, Email, Specialization, PhoneNo, Password) 
                  VALUES (%s, %s, %s, %s, %s, %s)"""
        cursor.execute(query, (user_id, additional_info['name'], additional_info['email'], 
                               additional_info['specialization'], additional_info['phone'], password))

    elif role == "admin":
        query = """INSERT INTO Admins (AdminID, Name, Email, Password) 
                  VALUES (%s, %s, %s, %s)"""
        cursor.execute(query, (user_id, additional_info['name'], additional_info['email'], password))

    conn.commit()
    conn.close()

    st.success(f"Account created successfully as {role.capitalize()}. You can now log in!")

# Main login function
def login():
    st.title("PES HOSPITAL")
    st.subheader("Login")

    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    role = st.selectbox("Login as", ["patient", "doctor", "admin"], key="login_role")

    if st.button("Login"):
        user = verify_user(username, password)
        if user and user["role"] == role:
            st.session_state["logged_in"] = True
            st.session_state["role"] = role
            st.session_state["user_id"] = user["user_id"]
            st.success(f"Logged in as {role.capitalize()}")
            st.rerun()  # Refresh to show the appropriate dashboard
        else:
            st.error("Invalid username, password, or role")

# Create account form function
def create_account_form():
    st.title("Create Account")

    role = st.selectbox("Choose role", ["patient", "doctor", "admin"], key="create_account_role")
    username = st.text_input("Username", key="create_account_username")
    password = st.text_input("Password", type="password", key="create_account_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="create_account_confirm_password")

    # Collect additional info based on the role
    additional_info = {}

    if role == "patient":
        additional_info["name"] = st.text_input("Full Name", key="patient_name")
        additional_info["email"] = st.text_input("Email ID", key="patient_email")
        additional_info["address"] = st.text_input("Address", key="patient_address")
        additional_info["dob"] = st.date_input("Date of Birth", key="patient_dob")
        additional_info["phone"] = st.text_input("Phone Number", key="patient_phone")
        additional_info["gender"] = st.selectbox("Gender", ["M", "F"], key="patient_gender")
        additional_info["is_pes_student"] = st.checkbox("Are you a PES student?", key="patient_is_pes_student")
        additional_info["srn"] = st.text_input("SRN (if applicable)", key="patient_srn")

    elif role == "doctor":
        additional_info["name"] = st.text_input("Full Name", key="doctor_name")
        additional_info["email"] = st.text_input("Email ID", key="doctor_email")
        additional_info["specialization"] = st.text_input("Specialization", key="doctor_specialization")
        additional_info["phone"] = st.text_input("Phone Number", key="doctor_phone")

    elif role == "admin":
        additional_info["name"] = st.text_input("Full Name", key="admin_name")
        additional_info["email"] = st.text_input("Email ID", key="admin_email")

    if password == confirm_password:
        if st.button("Create Account", key="create_account_button"):
            create_account(username, password, role, additional_info)
    else:
        st.error("Passwords do not match.")

def give_feedback():
    st.subheader("Provide Feedback")

    # Initialize session state for feedback form
    if "appointment_id" not in st.session_state:
        st.session_state.appointment_id = ""  # Default empty value
    if "rating" not in st.session_state:
        st.session_state.rating = 3  # Default value for slider
    if "comments" not in st.session_state:
        st.session_state.comments = ""  # Default empty value for comments

    # Create a form to handle feedback submission
    with st.form(key="feedback_form"):
        # Form components bound to session state
        appointment_id = st.text_input("Enter Appointment ID", value=st.session_state.appointment_id)
        rating = st.slider("Rate your experience (1 to 5)", 1, 5, value=st.session_state.rating)
        comments = st.text_area("Additional Comments", value=st.session_state.comments)

        # Update session state when values change
        st.session_state.appointment_id = appointment_id
        st.session_state.rating = rating
        st.session_state.comments = comments

        # Submit button for the form
        submit_button = st.form_submit_button(label="Submit Feedback")

    # Handle form submission
    if submit_button:
        if appointment_id:  # Ensure an Appointment ID is provided
            # Perform feedback submission to the database
            conn = create_connection()
            cursor = conn.cursor()
            query = """INSERT INTO Feedback (PatientID, AppointmentID, Rating, Comments) 
                       VALUES (%s, %s, %s, %s)"""
            cursor.execute(query, (st.session_state["user_id"], appointment_id, rating, comments))
            conn.commit()
            conn.close()
            st.success("Feedback submitted successfully.")
            logger.info(f"Feedback submitted for appointment {appointment_id}")
        else:
            st.error("Please enter a valid Appointment ID.")



# Dashboard for different user roles
def patient_dashboard():
    st.subheader("Patient Dashboard")
    st.write("Welcome, Patient!")
    if st.button("Book an Appointment"):
        run_book_script()  # Book an appointment functionality for the patient
        logger.info("Appointment booked successfully")
    # Give Feedback button
    if st.button("Give Feedback"):
        give_feedback()  # Function to handle feedback submission
    
    # View Appointments button
    if st.button("View My Appointments"):
        view_appointments() 
        

# Function to view patient's appointments
def view_appointments():
    st.subheader("My Appointments")
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM Appointments WHERE PatientID = %s"
    cursor.execute(query, (st.session_state["user_id"],))
    appointments = cursor.fetchall()
    conn.close()

    if appointments:
        for appointment in appointments:
            st.write(f"Appointment ID: {appointment['AppointmentID']}")
            st.write(f"Doctor ID: {appointment['DoctorID']}")
            st.write(f"Date: {appointment['AppointmentDate']}")
            st.write(f"Time: {appointment['AppointmentTime']}")
            st.write("---")
    else:
        st.write("No appointments found.")

def doctor_dashboard():
    st.subheader("Doctor Dashboard")
    st.write("Welcome, Doctor!")
    doctor_id = st.session_state["user_id"]
    st.write(f"Your Doctor ID is: {doctor_id}")
    if st.button("View Schedule"):
        run_doc_script(doctor_id)
    if st.button("View My Appointments"):
        view_doctor_appointments(doctor_id)  # New function to view doctor's appointments

# Function to view doctor's appointments
def view_doctor_appointments(doctor_id):
    st.subheader("My Appointments")
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch appointments for the logged-in doctor
    query = """SELECT a.AppointmentID, p.Name as PatientName, a.AppointmentDate, a.AppointmentTime 
               FROM Appointments a 
               JOIN Patients p ON a.PatientID = p.PatientID 
               WHERE a.DoctorID = %s 
               ORDER BY a.AppointmentDate, a.AppointmentTime"""
    cursor.execute(query, (doctor_id,))
    appointments = cursor.fetchall()
    conn.close()

    if appointments:
        for appointment in appointments:
            st.write(f"Appointment ID: {appointment['AppointmentID']}")
            st.write(f"Patient Name: {appointment['PatientName']}")
            st.write(f"Date: {appointment['AppointmentDate']}")
            st.write(f"Time: {appointment['AppointmentTime']}")
            st.write("---")
    else:
        st.write("No appointments found.")

def admin_dashboard():
    st.subheader("Admin Dashboard")
    st.write("Welcome, Admin!")
    if st.button("Manage Waitlist"):
        run_admin_script()

# App layout
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# Switch between login, create account, and logged-in dashboards
if not st.session_state["logged_in"]:
    if "create_account" in st.session_state and st.session_state["create_account"]:
        create_account_form()  # Show the create account form
    else:
        login()  # Show the login form
    # Sidebar for creating account if not logged in
    if st.sidebar.button("Create Account"):
        st.session_state["create_account"] = True
else:
    role = st.session_state["role"]
    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["role"] = None
        st.session_state["create_account"] = False  # Reset the create account flag
        st.rerun()

    st.title("PES HOSPITAL")

    # Display different dashboards based on role
    if role == "patient":
        patient_dashboard()
    elif role == "doctor":
        doctor_dashboard()
    elif role == "admin":
        admin_dashboard()
