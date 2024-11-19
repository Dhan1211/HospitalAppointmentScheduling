import streamlit as st
import mysql.connector

# Database connection
def create_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Dhan",  # Update password if necessary
        database="hospitaldb"  # Ensure your database is named correctly
    )
    return conn

# Fetch list of doctors for the dropdown
def get_doctors():
    conn = create_connection()
    cursor = conn.cursor()
    query = "SELECT DoctorID, Name FROM Doctors"
    cursor.execute(query)
    doctors = cursor.fetchall()
    conn.close()
    return doctors

# Function to display the schedule for the selected doctor
def show_schedule(doctor_id):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Query to fetch schedule details for the doctor
    query = "SELECT AvailableDate, StartTime, EndTime FROM Schedule WHERE DoctorID = %s"
    cursor.execute(query, (doctor_id,))
    schedule = cursor.fetchall()
    conn.close()

    st.subheader("Doctor's Schedule")
    if schedule:
        # Display each available schedule entry
        for entry in schedule:
            st.write(f"Date: {entry['AvailableDate']}, Start: {entry['StartTime']}, End: {entry['EndTime']}")
    else:
        st.write("No available schedule for this doctor.")

# Streamlit interface for booking an appointment
st.title("Hospital Appointment System")

# Dropdown to select doctor
doctor_list = get_doctors()
doctor_names = [doctor[1] for doctor in doctor_list]  # List of doctor names
doctor_ids = {doctor[1]: doctor[0] for doctor in doctor_list}  # Dictionary of doctor names to IDs
doctor_name = st.selectbox("Select Doctor", doctor_names)

# Display doctor's schedule when a doctor is selected
if doctor_name:
    doctor_id = doctor_ids[doctor_name]
    show_schedule(doctor_id)
