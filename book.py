
import streamlit as st
import mysql.connector
from datetime import datetime

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

class Patient:
    def __init__(self, patient_id, roll_number=None):
        self.patient_id = patient_id
        self.roll_number = roll_number

    def is_student_eligible(self, db: Database):
        query = "SELECT * FROM Patients WHERE SRN = %s"
        cursor = db.execute(query, (self.roll_number,))
        result = cursor.fetchone()
        return result is not None

class Doctor:
    @staticmethod
    def get_doctors(db: Database):
        query = "SELECT DoctorID, Name FROM Doctors"
        cursor = db.execute(query)
        return cursor.fetchall()

    @staticmethod
    def get_doctor_id_by_name(db: Database, name):
        query = "SELECT DoctorID FROM Doctors WHERE Name = %s"
        cursor = db.execute(query, (name,))
        doctor_row = cursor.fetchone()
        return doctor_row["DoctorID"] if doctor_row else None

class Appointment:
    @staticmethod
    def is_slot_available(db: Database, doctor_id, appointment_date, appointment_time):
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
        cursor = db.execute(query, (doctor_id, appointment_date, appointment_time, doctor_id, appointment_date, appointment_time, appointment_time))
        result = cursor.fetchone()
        return result and result.get('Slot_Status') == 'Available'

    @staticmethod
    def book(db: Database, patient_id, doctor_name, appointment_date, appointment_time, specialization):
        doctor_id = Doctor.get_doctor_id_by_name(db, doctor_name) if doctor_name else None
        if doctor_name and not doctor_id:
            st.error(f"Doctor {doctor_name} not found in the database.")
            return
        if Appointment.is_slot_available(db, doctor_id, appointment_date, appointment_time):
            query = """
            INSERT INTO Appointments (PatientID, DoctorID, AppointmentDate, AppointmentTime)
            VALUES (%s, %s, %s, %s)
            """
            db.execute(query, (patient_id, doctor_id, appointment_date, appointment_time))
            st.success("Appointment booked successfully!")
        else:
            query = """
            INSERT INTO Waitlist (PatientID, DoctorID, AppointmentDate, AppointmentTime, Status)
            VALUES (%s, %s, %s, %s, 'Waiting')
            """
            db.execute(query, (patient_id, doctor_id, appointment_date, appointment_time))
            st.warning("No slots available. Added to waitlist.")
        db.commit()

    @staticmethod
    def cancel(db: Database, appointment_id):
        query = "SELECT DoctorID, AppointmentDate, AppointmentTime FROM Appointments WHERE AppointmentID = %s"
        cursor = db.execute(query, (appointment_id,))
        appointment = cursor.fetchone()
        if appointment:
            doctor_id = appointment["DoctorID"]
            appointment_date = appointment["AppointmentDate"]
            appointment_time = appointment["AppointmentTime"]
            update_query = """
            UPDATE Appointments
            SET AppointmentDate = NULL, AppointmentTime = NULL
            WHERE AppointmentID = %s
            """
            db.execute(update_query, (appointment_id,))
            schedule_query = """
            INSERT INTO Schedule (DoctorID, AvailableDate, StartTime, EndTime)
            VALUES (%s, %s, %s, %s)
            """
            db.execute(schedule_query, (doctor_id, appointment_date, appointment_time, appointment_time))
            db.commit()
            st.success(f"Appointment {appointment_id} has been successfully canceled and the slot is returned to the schedule.")
        else:
            st.error("Appointment ID not found or already canceled.")

class Feedback:
    @staticmethod
    def collect(db: Database, patient_id, appointment_id):
        query = "SELECT * FROM Feedback WHERE AppointmentID = %s AND PatientID = %s"
        cursor = db.execute(query, (appointment_id, patient_id))
        feedback = cursor.fetchone()
        if feedback:
            st.info("Feedback has already been provided for this appointment.")
        else:
            st.subheader(f"Please provide your feedback for Appointment ID: {appointment_id}")
            rating = st.slider("Rating (1 to 5)", 1, 5, 3)
            comments = st.text_area("Comments", "")
            if st.button("Submit Feedback"):
                feedback_query = """
                INSERT INTO Feedback (PatientID, AppointmentID, Rating, Comments)
                VALUES (%s, %s, %s, %s)
                """
                db.execute(feedback_query, (patient_id, appointment_id, rating, comments))
                db.commit()
                st.success("Thank you for your feedback! Your feedback has been submitted.")

# Streamlit UI
st.header("Book an Appointment, Provide Feedback, or Cancel an Appointment")
db = Database()

# Booking
patient_id = st.text_input("Enter Patient ID")
doctor_name_list = Doctor.get_doctors(db)
doctor_names = [doctor["Name"] for doctor in doctor_name_list]
doctor_name = st.selectbox("Choose Doctor (optional)", doctor_names + ["None"])
specializations = ["Cardiology", "Orthopedics", "Pediatrics", "Neurology"]
specialization = st.selectbox("Choose Specialization", specializations)
appointment_date = st.date_input("Select Appointment Date")
appointment_time = st.time_input("Select Appointment Time")
roll_number = st.text_input("Enter Roll Number if you are a student (for free consultation)")

if roll_number:
    patient = Patient(patient_id, roll_number)
    if patient.is_student_eligible(db):
        st.write("Student eligible for free consultation.")
    else:
        st.write("Consultation fee applies.")

if st.button("Book Appointment"):
    if patient_id and specialization and appointment_date and appointment_time:
        Appointment.book(db, patient_id, doctor_name if doctor_name != "None" else None, appointment_date, appointment_time, specialization)
    else:
        st.error("Please fill in all fields to book an appointment.")

# Feedback
st.subheader("Provide Feedback for an Appointment")
feedback_patient_id = st.text_input("Enter Patient ID for feedback")
feedback_appointment_id = st.text_input("Enter Appointment ID to provide feedback")
if st.button("Submit Feedback"):
    if feedback_patient_id and feedback_appointment_id:
        Feedback.collect(db, feedback_patient_id, feedback_appointment_id)
    else:
        st.error("Please enter both Patient ID and Appointment ID to provide feedback.")

# Cancel Appointment
st.subheader("Cancel an Appointment")
cancel_appointment_id = st.text_input("Enter Appointment ID to cancel")
if st.button("Cancel Appointment"):
    if cancel_appointment_id:
        Appointment.cancel(db, cancel_appointment_id)
    else:
        st.error("Please enter a valid Appointment ID to cancel.")

db.close()
