import streamlit as st
import mysql.connector
from datetime import datetime

# Database connection setup
def create_connection():
    conn = mysql.connector.connect(
        host="localhost",  # Replace with your database host
        user="root",       # Replace with your database user
        password="Dhan",   # Replace with your database password
        database="hospitaldb"  # Replace with your database name
    )
    return conn

# Function to check if a student is eligible for a free consultation
def is_student_eligible(roll_number):
    conn = create_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM Patients WHERE SRN = %s"
    cursor.execute(query, (roll_number,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

# Fetch doctors from the database
def get_doctors():
    conn = create_connection()
    cursor = conn.cursor()
    query = "SELECT DoctorID, Name FROM Doctors"  # Fetch DoctorID and Name from Doctors table
    cursor.execute(query)
    doctors = cursor.fetchall()
    conn.close()
    return doctors

# Function to check if a slot is available for booking
def is_slot_available(doctor_id, appointment_date, appointment_time):
    conn = create_connection()
    cursor = conn.cursor()

    query = """
    SELECT 
        CASE 
            WHEN COUNT(*) < max_slots THEN 'Available' 
            ELSE 'Not Available' 
        END AS Slot_Status
    FROM (
        SELECT COUNT(*) AS max_slots
        FROM Appointments
        WHERE DoctorID = %s AND AppointmentDate = %s AND AppointmentTime = %s
    ) AS slot_count
    JOIN (
        SELECT AvailableDate, StartTime, EndTime
        FROM Schedule 
        WHERE DoctorID = %s
        AND AvailableDate = %s 
        AND StartTime <= %s AND EndTime >= %s
    ) AS doctor_schedule ON 1 = 1
    GROUP BY slot_count.max_slots, doctor_schedule.AvailableDate, doctor_schedule.StartTime, doctor_schedule.EndTime
    """
    
    cursor.execute(query, (doctor_id, appointment_date, appointment_time, doctor_id, appointment_date, appointment_time, appointment_time))
    result = cursor.fetchone()
    conn.close()

    if result and result['Slot_Status'] == 'Available':
        return True
    return False

# Booking an appointment with waitlist functionality
def book_appointment(patient_id, doctor_name, appointment_date, appointment_time, specialization):
    conn = create_connection()
    cursor = conn.cursor()
    
    # If a doctor is selected, get the DoctorID based on the doctor's Name
    if doctor_name:
        query = "SELECT DoctorID FROM Doctors WHERE Name = %s"
        cursor.execute(query, (doctor_name,))
        doctor_row = cursor.fetchone()
        
        if doctor_row:
            doctor_id = doctor_row[0]  # Extract DoctorID from the result
        else:
            st.error(f"Doctor {doctor_name} not found in the database.")
            return
    else:
        doctor_id = None  # No doctor selected
    
    # Check if slot is available using the new query
    if is_slot_available(doctor_id, appointment_date, appointment_time):
        # Book the appointment
        query = """
        INSERT INTO Appointments (PatientID, DoctorID, AppointmentDate, AppointmentTime)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (patient_id, doctor_id, appointment_date, appointment_time))
        st.success("Appointment booked successfully!")
    else:
        # Add to waitlist
        query = """
        INSERT INTO Waitlist (PatientID, DoctorID, AppointmentDate, AppointmentTime, Status)
        VALUES (%s, %s, %s, %s, 'Waiting')
        """
        cursor.execute(query, (patient_id, doctor_id, appointment_date, appointment_time))
        st.warning("No slots available. Added to waitlist.")
    
    conn.commit()
    conn.close()

# Function to collect feedback for any appointment ID
def collect_feedback(patient_id, appointment_id):
    conn = create_connection()
    cursor = conn.cursor()

    # Check if the feedback has already been provided for this appointment
    query = "SELECT * FROM Feedback WHERE AppointmentID = %s AND PatientID = %s"
    cursor.execute(query, (appointment_id, patient_id))
    feedback = cursor.fetchone()

    if feedback:
        st.info("Feedback has already been provided for this appointment.")
    else:
        # Provide the feedback form
        st.subheader("Please provide your feedback for Appointment ID: " + appointment_id)
        rating = st.slider("Rating (1 to 5)", 1, 5, 3)  # 1-5 rating scale
        comments = st.text_area("Comments", "")

        if st.button("Submit Feedback"):
            # Insert the feedback into the database
            feedback_query = """
            INSERT INTO Feedback (PatientID, AppointmentID, Rating, Comments)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(feedback_query, (patient_id, appointment_id, rating, comments))
            conn.commit()

            # Optionally, we can log a success message or inform the user that the feedback has been submitted
            st.success("Thank you for your feedback! Your feedback has been submitted.")
    
    conn.close()

# Procedure to cancel an appointment
def cancel_appointment(appointment_id):
    conn = create_connection()
    cursor = conn.cursor()

    # Get the doctor's details and appointment time
    query = "SELECT DoctorID, AppointmentDate, AppointmentTime FROM Appointments WHERE AppointmentID = %s"
    cursor.execute(query, (appointment_id,))
    appointment = cursor.fetchone()

    if appointment:
        doctor_id, appointment_date, appointment_time = appointment
        
        # Update the appointment status to cancelled
        update_query = """
        UPDATE Appointments
        SET AppointmentDate = NULL, AppointmentTime = NULL
        WHERE AppointmentID = %s
        """
        cursor.execute(update_query, (appointment_id,))
        
        # Add the appointment slot back to the doctor's schedule
        schedule_query = """
        INSERT INTO Schedule (DoctorID, AvailableDate, StartTime, EndTime)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(schedule_query, (doctor_id, appointment_date, appointment_time, appointment_time))

        conn.commit()
        st.success(f"Appointment {appointment_id} has been successfully canceled and the slot is returned to the schedule.")
    else:
        st.error("Appointment ID not found or already canceled.")
    
    conn.close()

# Patient interface
st.header("Book an Appointment, Provide Feedback, or Cancel an Appointment")

# User inputs for booking
patient_id = st.text_input("Enter Patient ID")
doctor_name_list = get_doctors()
doctor_names = [doctor[1] for doctor in doctor_name_list]  # Extracting doctor names
doctor_name = st.selectbox("Choose Doctor (optional)", doctor_names + ["None"])

# Specialization is required
specializations = ["Cardiology", "Orthopedics", "Pediatrics", "Neurology"]  # Adjust this list as needed
specialization = st.selectbox("Choose Specialization", specializations)

appointment_date = st.date_input("Select Appointment Date")
appointment_time = st.time_input("Select Appointment Time")
roll_number = st.text_input("Enter Roll Number if you are a student (for free consultation)")

# Check if student is eligible for free consultation
if roll_number:
    if is_student_eligible(roll_number):
        st.write("Student eligible for free consultation.")
    else:
        st.write("Consultation fee applies.")

# Book appointment on button click
if st.button("Book Appointment"):
    if patient_id and specialization and appointment_date and appointment_time:
        # Pass doctor_name (which can be None) and specialization to the booking function
        book_appointment(patient_id, doctor_name if doctor_name != "None" else None, appointment_date, appointment_time, specialization)
    else:
        st.error("Please fill in all fields to book an appointment.")

# Collect feedback for completed appointment
st.subheader("Provide Feedback for an Appointment")

# User inputs for feedback
appointment_id = st.text_input("Enter Appointment ID to provide feedback")

# Collect feedback on button click
if patient_id and appointment_id:
    collect_feedback(patient_id, appointment_id)
else:
    st.error("Please enter both Patient ID and Appointment ID to provide feedback.")

# Cancel an appointment
st.subheader("Cancel an Appointment")

# User inputs for canceling an appointment
cancel_appointment_id = st.text_input("Enter Appointment ID to cancel")

# Cancel appointment on button click
if cancel_appointment_id:
    if st.button("Cancel Appointment"):
        cancel_appointment(cancel_appointment_id)
    else:
        st.error("Please enter a valid Appointment ID to cancel.")
