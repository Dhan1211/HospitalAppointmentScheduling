import streamlit as st
import mysql.connector
import logging

# Logger setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('hospital_app.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Dhan",
            database="hospitaldb"
        )
        self.cursor = self.conn.cursor(dictionary=True)

    def execute(self, query, params=None):
        self.cursor.execute(query, params or ())
        return self.cursor

    def commit(self):
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()

class User:
    def __init__(self, username, password, role=None):
        self.username = username
        self.password = password
        self.role = role
        self.user_id = None

    def verify(self, db: Database):
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor = db.execute(query, (self.username, self.password))
        user = cursor.fetchone()
        if user:
            logger.info(f"Successful login attempt by {self.username}")
            self.role = user["role"]
            self.user_id = user["user_id"]
        else:
            logger.warning(f"Failed login attempt by {self.username}")
        return user

class AccountManager:
    @staticmethod
    def create_account(db: Database, username, password, role, additional_info):
        cursor = db.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            st.error("Username already exists. Please choose another one.")
            return
        query = "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)"
        db.execute(query, (username, password, role))
        user_id = db.cursor.lastrowid
        
        if role == "patient":
            query = """INSERT INTO Patients (PatientID, Name, EmailID, Address, Date_Of_Birth, PhoneNo, Gender, Password, IsPESStudent, SRN) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            db.execute(query, (user_id, additional_info['name'], additional_info['email'], additional_info['address'], 
                              additional_info['dob'], additional_info['phone'], additional_info['gender'], 
                              password, additional_info['is_pes_student'], additional_info['srn']))
        elif role == "doctor":
            query = """INSERT INTO Doctors (DoctorID, Name, Email, Specialization, PhoneNo, Password) 
                       VALUES (%s, %s, %s, %s, %s, %s)"""
            db.execute(query, (user_id, additional_info['name'], additional_info['email'], 
                              additional_info['specialization'], additional_info['phone'], password))
        elif role == "admin":
            query = """INSERT INTO Admins (AdminID, Name, Email, Password) VALUES (%s, %s, %s, %s)"""
            db.execute(query, (user_id, additional_info['name'], additional_info['email'], password))
        
        db.commit()
        st.success(f"Account created successfully as {role.capitalize()}. You can now log in!")
        logger.info(f"Account created for {username} as {role}")

class Feedback:
    @staticmethod
    def submit(db: Database, patient_id, appointment_id, rating, comments):
        query = """INSERT INTO Feedback (PatientID, AppointmentID, Rating, Comments) 
                   VALUES (%s, %s, %s, %s)"""
        db.execute(query, (patient_id, appointment_id, rating, comments))
        db.commit()
        st.success("Feedback submitted successfully.")
        logger.info(f"Feedback submitted for appointment {appointment_id}")

class Appointment:
    @staticmethod
    def view_patient_appointments(db: Database, patient_id):
        query = "SELECT * FROM Appointments WHERE PatientID = %s"
        cursor = db.execute(query, (patient_id,))
        appointments = cursor.fetchall()
        return appointments

    @staticmethod
    def view_doctor_appointments(db: Database, doctor_id):
        query = """SELECT a.AppointmentID, p.Name as PatientName, a.AppointmentDate, a.AppointmentTime 
                   FROM Appointments a 
                   JOIN Patients p ON a.PatientID = p.PatientID 
                   WHERE a.DoctorID = %s 
                   ORDER BY a.AppointmentDate, a.AppointmentTime"""
        cursor = db.execute(query, (doctor_id,))
        appointments = cursor.fetchall()
        return appointments

# UI Functions
def login(db: Database):
    st.title("PES HOSPITAL")
    st.subheader("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    role = st.selectbox("Login as", ["patient", "doctor", "admin"], key="login_role")
    
    if st.button("Login"):
        user = User(username, password, role)
        user_data = user.verify(db)
        if user_data and user_data["role"] == role:
            st.session_state["logged_in"] = True
            st.session_state["role"] = role
            st.session_state["user_id"] = user_data["user_id"]
            st.success(f"Logged in as {role.capitalize()}")
            st.rerun()
        else:
            st.error("Invalid username, password, or role")

def create_account_form(db: Database):
    st.title("Create Account")
    role = st.selectbox("Choose role", ["patient", "doctor", "admin"], key="create_account_role")
    username = st.text_input("Username", key="create_account_username")
    password = st.text_input("Password", type="password", key="create_account_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="create_account_confirm_password")
    
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
            AccountManager.create_account(db, username, password, role, additional_info)
    else:
        st.error("Passwords do not match.")

def patient_dashboard(db: Database, patient_id):
    st.subheader("Patient Dashboard")
    st.write("Welcome, Patient!")
    
    tab1, tab2, tab3 = st.tabs(["Book Appointment", "View Appointments", "Give Feedback"])
    
    with tab1:
        st.write("Navigate to book.py to book an appointment.")
    
    with tab2:
        st.write("My Appointments:")
        appointments = Appointment.view_patient_appointments(db, patient_id)
        if appointments:
            for appointment in appointments:
                st.write(f"**Appointment ID:** {appointment['AppointmentID']}")
                st.write(f"**Doctor ID:** {appointment['DoctorID']}")
                st.write(f"**Date:** {appointment['AppointmentDate']}")
                st.write(f"**Time:** {appointment['AppointmentTime']}")
                st.divider()
        else:
            st.write("No appointments found.")
    
    with tab3:
        st.write("Provide Feedback for an Appointment")
        feedback_appointment_id = st.text_input("Enter Appointment ID", key="feedback_appt_id")
        rating = st.slider("Rate your experience (1 to 5)", 1, 5, 3)
        comments = st.text_area("Additional Comments", "")
        
        if st.button("Submit Feedback"):
            if feedback_appointment_id:
                Feedback.submit(db, patient_id, feedback_appointment_id, rating, comments)
            else:
                st.error("Please enter a valid Appointment ID.")

def doctor_dashboard(db: Database, doctor_id):
    st.subheader("Doctor Dashboard")
    st.write("Welcome, Doctor!")
    st.write(f"**Your Doctor ID:** {doctor_id}")
    
    tab1, tab2 = st.tabs(["View Schedule", "View Appointments"])
    
    with tab1:
        st.write("Navigate to doc.py to view your schedule.")
    
    with tab2:
        st.write("My Appointments:")
        appointments = Appointment.view_doctor_appointments(db, doctor_id)
        if appointments:
            for appointment in appointments:
                st.write(f"**Appointment ID:** {appointment['AppointmentID']}")
                st.write(f"**Patient Name:** {appointment['PatientName']}")
                st.write(f"**Date:** {appointment['AppointmentDate']}")
                st.write(f"**Time:** {appointment['AppointmentTime']}")
                st.divider()
        else:
            st.write("No appointments found.")

def admin_dashboard(db: Database):
    st.subheader("Admin Dashboard")
    st.write("Welcome, Admin!")
    
    tab1 = st.tabs(["Manage Waitlist"])[0]
    
    with tab1:
        st.write("Navigate to waitlist.py to manage the waitlist.")

# Main App
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

db = Database()

if not st.session_state["logged_in"]:
    if "create_account" not in st.session_state:
        st.session_state["create_account"] = False
    
    if st.session_state["create_account"]:
        create_account_form(db)
        if st.button("Back to Login"):
            st.session_state["create_account"] = False
            st.rerun()
    else:
        login(db)
        if st.sidebar.button("Create Account"):
            st.session_state["create_account"] = True
            st.rerun()
else:
    role = st.session_state["role"]
    user_id = st.session_state["user_id"]
    
    st.title("PES HOSPITAL")
    if st.button("Logout", key="logout_button"):
        st.session_state["logged_in"] = False
        st.session_state["role"] = None
        st.session_state["user_id"] = None
        st.session_state["create_account"] = False
        st.rerun()
    
    st.divider()
    
    if role == "patient":
        patient_dashboard(db, user_id)
    elif role == "doctor":
        doctor_dashboard(db, user_id)
    elif role == "admin":
        admin_dashboard(db)

db.close()
