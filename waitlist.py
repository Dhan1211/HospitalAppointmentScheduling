
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

class Student:
    def __init__(self, roll_number):
        self.roll_number = roll_number

    def is_eligible(self, db: Database):
        query = "SELECT * FROM students WHERE roll_number = %s"
        cursor = db.execute(query, (self.roll_number,))
        result = cursor.fetchone()
        return result is not None

class Appointment:
    @staticmethod
    def book(db: Database, patient_id, doctor_id, appointment_date):
        try:
            query = "SELECT COUNT(*) as slot_count FROM appointments WHERE DoctorID = %s AND AppointmentDate = %s"
            cursor = db.execute(query, (doctor_id, appointment_date))
            result = cursor.fetchone()
            slots = result.get('slot_count', 0) if result else 0
            
            if slots < 5:
                query = "INSERT INTO appointments (patient_id, doctor_id, appointment_date) VALUES (%s, %s, %s)"
                db.execute(query, (patient_id, doctor_id, appointment_date))
                st.success("✓ Appointment booked successfully!")
            else:
                Waitlist.add(db, patient_id, doctor_id, appointment_date)
                st.warning("⚠ No slots available. Added to waitlist.")
            db.commit()
        except Exception as e:
            st.error(f"Error booking appointment: {str(e)}")
            db.close()
            db = Database()

class Waitlist:
    @staticmethod
    def add(db: Database, patient_id, doctor_id, appointment_date):
        query = "INSERT INTO waitlist (patient_id, doctor_id, appointment_date) VALUES (%s, %s, %s)"
        db.execute(query, (patient_id, doctor_id, appointment_date))

    @staticmethod
    def display(db: Database):
        query = "SELECT * FROM waitlist ORDER BY DoctorID, AppointmentDate"
        cursor = db.execute(query)
        waitlist = cursor.fetchall()
        if waitlist:
            st.subheader("Current Waitlist")
            for item in waitlist:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.write(f"**Patient ID:** {item.get('patient_id') or item.get('PatientID', 'N/A')}")
                with col2:
                    st.write(f"**Doctor ID:** {item.get('doctor_id') or item.get('DoctorID', 'N/A')}")
                with col3:
                    st.write(f"**Appointment Date:** {item.get('appointment_date') or item.get('AppointmentDate', 'N/A')}")
                with col4:
                    st.write(f"**Waitlisted At:** {item.get('waitlist_time') or item.get('WaitlistTime', 'N/A')}")
                st.divider()
        else:
            st.info("No patients are currently on the waitlist.")

    @staticmethod
    def notify_for_open_slots(db: Database):
        try:
            query = "SELECT * FROM cancellations"
            cursor = db.execute(query)
            cancellations = cursor.fetchall()
            
            if not cancellations:
                st.info("No cancellations to process.")
                return
            
            notified_count = 0
            for cancel in cancellations:
                doctor_id = cancel.get('doctor_id') or cancel.get('DoctorID')
                appointment_date = cancel.get('appointment_date') or cancel.get('AppointmentDate')
                
                query = "SELECT * FROM waitlist WHERE doctor_id = %s AND appointment_date = %s ORDER BY waitlist_time LIMIT 1"
                cursor2 = db.execute(query, (doctor_id, appointment_date))
                waitlisted_patient = cursor2.fetchone()
                
                if waitlisted_patient:
                    patient_id = waitlisted_patient.get('patient_id') or waitlisted_patient.get('PatientID')
                    Appointment.book(db, patient_id, doctor_id, appointment_date)
                    st.success(f"✓ Patient {patient_id} has been notified and booked for an open slot.")
                    notified_count += 1
            
            db.commit()
            if notified_count == 0:
                st.info("No waitlisted patients to notify.")
            else:
                st.success(f"✓ Notified {notified_count} patient(s).")
        except Exception as e:
            st.error(f"Error notifying patients: {str(e)}")

# UI Functions
def book_appointment_page(db: Database):
    st.header("Book an Appointment")
    patient_id = st.text_input("Enter Patient ID")
    doctor_id = st.selectbox("Choose Doctor ID", [1, 2, 3])
    appointment_date = st.date_input("Select Appointment Date")
    roll_number = st.text_input("Enter Roll Number if you are a student (for free consultation)")
    
    if roll_number:
        student = Student(roll_number)
        if student.is_eligible(db):
            st.success("✓ Student eligible for free consultation.")
        else:
            st.info("Consultation fee applies.")
    
    if st.button("Book Appointment"):
        if patient_id and doctor_id and appointment_date:
            Appointment.book(db, patient_id, doctor_id, appointment_date)
        else:
            st.error("Please fill in all fields to book an appointment.")

def view_waitlist_page(db: Database):
    st.header("View Waitlist")
    Waitlist.display(db)

def admin_notifications_page(db: Database):
    st.header("Admin: Manage Waitlist and Notifications")
    if st.button("Notify Waitlisted Patients for Open Slots"):
        Waitlist.notify_for_open_slots(db)

# Main Streamlit application
st.title("PES HOSPITAL")
db = Database()

tab1, tab2, tab3 = st.tabs(["Book Appointment", "View Waitlist", "Admin Notifications"])

with tab1:
    book_appointment_page(db)

with tab2:
    view_waitlist_page(db)

with tab3:
    admin_notifications_page(db)

db.close()
