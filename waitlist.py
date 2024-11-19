import streamlit as st
import mysql.connector
from datetime import datetime

# Database connection setup
def create_connection():
    conn = mysql.connector.connect(
        host="localhost",  # Replace with your database host
        user="root",       # Replace with your database user
        password="Dhan",       # Replace with your database password
        database="hospitaldb"  # Replace with your database name
    )
    return conn

# Function to check if a student is eligible for a free consultation
def is_student_eligible(roll_number):
    conn = create_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM students WHERE roll_number = %s"
    cursor.execute(query, (roll_number,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

# Booking an appointment with waitlist functionality
def book_appointment(patient_id, doctor_id, appointment_date):
    conn = create_connection()
    cursor = conn.cursor()
    
    # Check if slot is available
    query = """
    SELECT COUNT(*) FROM appointments 
    WHERE DoctorID = %s AND AppointmentDate = %s
    """
    cursor.execute(query, (doctor_id, appointment_date))
    slots = cursor.fetchone()[0]
    
    if slots < 5:  # Assuming 5 is the max slots per doctor per day
        # Book the appointment
        query = "INSERT INTO appointments (patient_id, doctor_id, appointment_date) VALUES (%s, %s, %s)"
        cursor.execute(query, (patient_id, doctor_id, appointment_date))
        st.success("Appointment booked successfully!")
    else:
        # Add to waitlist
        query = "INSERT INTO waitlist (patient_id, doctor_id, appointment_date) VALUES (%s, %s, %s)"
        cursor.execute(query, (patient_id, doctor_id, appointment_date))
        st.warning("No slots available. Added to waitlist.")
    
    conn.commit()
    conn.close()

# Function to display the waitlist
def display_waitlist():
    conn = create_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM waitlist ORDER BY DoctorID, AppointmentDate"
    cursor.execute(query)
    waitlist = cursor.fetchall()
    
    if waitlist:
        st.write("### Current Waitlist:")
        for item in waitlist:
            patient_id, doctor_id, appointment_date, waitlist_time = item
            st.write(f"Patient ID: {patient_id}, Doctor ID: {doctor_id}, Appointment Date: {appointment_date}, Waitlisted At: {waitlist_time}")
    else:
        st.write("No patients are currently on the waitlist.")
    
    conn.close()

# Main Streamlit application
st.title("PES HOSPITAL")

# Navigation menu
page = st.radio("Select a Page", ("Book an Appointment", "View Waitlist"))

if page == "Book an Appointment":
    # Patient interface
    st.header("Book an Appointment")

    patient_id = st.text_input("Enter Patient ID")
    doctor_id = st.selectbox("Choose Doctor ID", [1, 2, 3])  # Populate with doctor IDs
    appointment_date = st.date_input("Select Appointment Date")
    roll_number = st.text_input("Enter Roll Number if you are a student (for free consultation)")

    # Check if student is eligible for free consultation
    if roll_number:
        if is_student_eligible(roll_number):
            st.write("Student eligible for free consultation.")
        else:
            st.write("Consultation fee applies.")

    if st.button("Book Appointment"):
        if patient_id and doctor_id and appointment_date:
            book_appointment(patient_id, doctor_id, appointment_date)
        else:
            st.error("Please fill in all fields to book an appointment.")

elif page == "View Waitlist":
    # Waitlist page interface
    st.header("View Waitlist")
    display_waitlist()

# Admin interface
st.header("Admin: Manage Waitlist and Notifications")

if st.button("Notify Waitlisted Patients for Open Slots"):
    # Logic to check for cancellations and notify waitlisted patients
    conn = create_connection()
    cursor = conn.cursor()
    # Fetch cancelled appointments
    query = "SELECT * FROM cancellations"  # This would depend on how you log cancellations
    cursor.execute(query)
    cancellations = cursor.fetchall()
    
    for cancel in cancellations:
        doctor_id, appointment_date = cancel[1], cancel[2]
        # Notify first patient on waitlist for this slot
        query = """
        SELECT * FROM waitlist 
        WHERE doctor_id = %s AND appointment_date = %s
        ORDER BY waitlist_time LIMIT 1
        """
        cursor.execute(query, (doctor_id, appointment_date))
        waitlisted_patient = cursor.fetchone()
        
        if waitlisted_patient:
            # Move from waitlist to appointments
            patient_id = waitlisted_patient[0]
            book_appointment(patient_id, doctor_id, appointment_date)
            st.write(f"Patient {patient_id} has been notified and booked for an open slot.")
    
    conn.commit()
    conn.close()
