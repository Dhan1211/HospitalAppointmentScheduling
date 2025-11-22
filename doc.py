
import streamlit as st
import mysql.connector

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

    def close(self):
        self.cursor.close()
        self.conn.close()

class Doctor:
    @staticmethod
    def get_doctors(db: Database):
        query = "SELECT DoctorID, Name FROM Doctors"
        cursor = db.execute(query)
        return cursor.fetchall()

    @staticmethod
    def show_schedule(db: Database, doctor_id):
        query = "SELECT AvailableDate, StartTime, EndTime FROM Schedule WHERE DoctorID = %s"
        cursor = db.execute(query, (doctor_id,))
        schedule = cursor.fetchall()
        st.subheader("Doctor's Schedule")
        if schedule:
            for entry in schedule:
                st.write(f"Date: {entry['AvailableDate']}, Start: {entry['StartTime']}, End: {entry['EndTime']}")
        else:
            st.write("No available schedule for this doctor.")

# Streamlit interface
st.title("Hospital Appointment System")
db = Database()
doctor_list = Doctor.get_doctors(db)
doctor_names = [doctor['Name'] for doctor in doctor_list]
doctor_ids = {doctor['Name']: doctor['DoctorID'] for doctor in doctor_list}
doctor_name = st.selectbox("Select Doctor", doctor_names)

if doctor_name:
    doctor_id = doctor_ids[doctor_name]
    Doctor.show_schedule(db, doctor_id)

db.close()
