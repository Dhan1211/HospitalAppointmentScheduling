-- Table for Users
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,  
    role ENUM('patient', 'doctor', 'admin') NOT NULL
);

-- Table for Doctors
CREATE TABLE Doctors (
    DoctorID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(100) NOT NULL,
    Specialization VARCHAR(100),
    PhoneNo VARCHAR(15),
    Password VARCHAR(255) NOT NULL  
);

-- Table for Patients
CREATE TABLE Patients (
    PatientID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100) NOT NULL,
    EmailID VARCHAR(100) NOT NULL,
    Address VARCHAR(255),
    Date_Of_Birth DATE,
    PhoneNo VARCHAR(15),
    Gender CHAR(1),
    Password VARCHAR(100),
    IsPESStudent BOOLEAN,
    SRN VARCHAR(50)
);

-- Table for Schedule (Doctor's Availability)
CREATE TABLE Schedule (
    ScheduleID INT PRIMARY KEY AUTO_INCREMENT,
    DoctorID INT,
    AvailableDate DATE,
    StartTime TIME,
    EndTime TIME,
    FOREIGN KEY (DoctorID) REFERENCES Doctors(DoctorID)
);

-- Table for Appointments (main appointment table)
CREATE TABLE Appointments (
    AppointmentID INT PRIMARY KEY AUTO_INCREMENT,
    PatientID INT,
    DoctorID INT,
    AppointmentDate DATE,
    AppointmentTime TIME,
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID),
    FOREIGN KEY (DoctorID) REFERENCES Doctors(DoctorID)
);

-- Table for Appointment Details
CREATE TABLE AppointmentDetails (
    AppointmentID INT PRIMARY KEY AUTO_INCREMENT,
    PatientID INT,
    DoctorID INT,
    MedicationDetails TEXT,
    PrescriptionDetails TEXT,
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID),
    FOREIGN KEY (DoctorID) REFERENCES Doctors(DoctorID)
);

-- Table for Admins
CREATE TABLE Admins (
    AdminID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(100) NOT NULL,
    Password VARCHAR(100) NOT NULL
);

-- Table for Feedback (from Patients)
CREATE TABLE Feedback (
    FeedbackID INT PRIMARY KEY AUTO_INCREMENT,
    PatientID INT,
    AppointmentID INT,
    Rating INT,
    Comments TEXT,
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID),
    FOREIGN KEY (AppointmentID) REFERENCES Appointments(AppointmentID)
);

-- Table for Waitlist (for appointment requests)
CREATE TABLE Waitlist (
    WaitlistID INT PRIMARY KEY AUTO_INCREMENT,
    PatientID INT,
    DoctorID INT,
    AppointmentDate DATE,
    AppointmentTime TIME,
    Status VARCHAR(50),
    RequestTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID),
    FOREIGN KEY (DoctorID) REFERENCES Doctors(DoctorID)
);

-- Insert dummy data into Users
INSERT INTO users (username, password, role) VALUES
('John Doe', '123', 'patient'),
('Jane Smith', '456', 'patient'),
('Alice Williams', '789', 'patient'),
('Dr Robert Brown', '101', 'doctor'),
('Dr Emily White', '202', 'doctor'),
('Dr Michael Green', '303', 'doctor'),
('AdminJohn', '123', 'admin'),
('AdminJane', '456', 'admin'),
('Dr Paul Grey', '404', 'doctor'),
('Mike', '555', 'patient');

-- Insert data into Doctors first
INSERT INTO Doctors (Name, Email, Specialization, PhoneNo, Password) VALUES
('Dr. Robert Brown', 'robert.brown@example.com', 'Orthopedics', '345-678-9012', '101'),
('Dr. Emily White', 'emily.white@example.com', 'Pediatrics', '456-789-0123', '202'),
('Dr. Michael Green', 'michael.green@example.com', 'Dermatology', '567-890-1234', '303'),
('Dr. Sarah Johnson', 'sarah.johnson@example.com', 'Cardiology', '678-901-2345', '678'),
('Dr. James Black', 'james.black@example.com', 'Neurology', '789-012-3456', '789'),
('Dr. Laura King', 'laura.king@example.com', 'General Surgery', '890-123-4567', '890'),
('Dr. Paul Grey', 'paul.grey@example.com', 'Oncology', '901-234-5678', '404'),
('Dr. Anna Bell', 'anna.bell@example.com', 'Gastroenterology', '012-345-6789', '012'),
('Dr. Mark Lee', 'mark.lee@example.com', 'Urology', '123-456-7890', '123'),
('Dr. Rachel Adams', 'rachel.adams@example.com', 'Psychiatry', '234-567-8901', '234');

-- Insert data into Patients table
INSERT INTO Patients (Name, EmailID, Address, Date_Of_Birth, PhoneNo, Gender, Password, IsPESStudent, SRN) VALUES
('John Doe', 'john.doe@example.com', '123 Main St, Anytown', '1990-06-15', '555-1234', 'M', '123', FALSE, NULL),
('Jane Smith', 'jane.smith@example.com', '456 Oak St, Somecity', '1985-12-20', '555-5678', 'F', '456', TRUE, 'PES2UG22CS345'),
('Alice Williams', 'alice.williams@example.com', '789 Pine St, Elsewhere', '1993-04-12', '555-9101', 'F', '789', FALSE, NULL),
('Bob Johnson', 'bob.johnson@example.com', '101 Elm St, Townsville', '1992-08-03', '555-2345', 'M', '234', TRUE, 'PES2UG23CS123'),
('Charlie Brown', 'charlie.brown@example.com', '222 Birch St, Big City', '1991-02-25', '555-3456', 'M', '345', FALSE, NULL),
('Diana Prince', 'diana.prince@example.com', '333 Cedar St, Metropolis', '1988-03-14', '555-4567', 'F', '456', TRUE, 'PES2UG24CS678'),
('Eve Stone', 'eve.stone@example.com', '444 Maple St, Smalltown', '1995-05-20', '555-5678', 'F', '567', FALSE, NULL),
('Frank Miller', 'frank.miller@example.com', '555 Spruce St, Hilltop', '1990-11-11', '555-6789', 'M', '678', TRUE, 'PES2UG25CS789'),
('Grace Hopper', 'grace.hopper@example.com', '666 Willow St, Riverside', '1984-07-25', '555-7890', 'F', '789', FALSE, NULL),
('Henry Ford', 'henry.ford@example.com', '777 Aspen St, Lakeside', '1987-09-10', '555-8901', 'M', '890', TRUE, 'PES2UG26CS890');

-- Insert data into Schedule table
INSERT INTO Schedule (DoctorID, AvailableDate, StartTime, EndTime) VALUES
(1, '2024-11-15', '09:00:00', '12:00:00'),
(2, '2024-11-16', '10:00:00', '13:00:00'),
(3, '2024-11-17', '08:00:00', '11:00:00'),
(4, '2024-11-18', '14:00:00', '17:00:00'),
(5, '2024-11-19', '15:00:00', '18:00:00'),
(6, '2024-11-20', '09:00:00', '12:00:00'),
(7, '2024-11-21', '11:00:00', '14:00:00'),
(8, '2024-11-22', '08:00:00', '11:00:00'),
(9, '2024-11-23', '10:00:00', '13:00:00'),
(10, '2024-11-24', '14:00:00', '17:00:00');

-- Insert data into Appointments table
INSERT INTO Appointments (PatientID, DoctorID, AppointmentDate, AppointmentTime) VALUES
(1, 1, '2024-11-15', '09:30:00'),
(2, 2, '2024-11-16', '10:30:00'),
(3, 3, '2024-11-17', '08:15:00'),
(4, 4, '2024-11-18', '14:45:00'),
(5, 5, '2024-11-19', '15:30:00'),
(6, 6, '2024-11-20', '09:15:00'),
(7, 7, '2024-11-21', '11:30:00'),
(8, 8, '2024-11-22', '08:45:00'),
(9, 9, '2024-11-23', '10:00:00'),
(10, 10, '2024-11-24', '14:15:00');

-- Insert data into AppointmentDetails table
INSERT INTO AppointmentDetails (PatientID, DoctorID, MedicationDetails, PrescriptionDetails) VALUES
(1, 1, 'Paracetamol 500mg', 'Take one tablet every 8 hours for 3 days'),
(2, 2, 'Amoxicillin 250mg', 'Take one capsule every 6 hours for 5 days'),
(3, 3, 'Ibuprofen 200mg', 'Take one tablet every 12 hours as needed for pain'),
(4, 4, 'Metformin 500mg', 'Take one tablet twice a day before meals'),
(5, 5, 'Aspirin 75mg', 'Take one tablet daily after breakfast'),
(6, 6, 'Ciprofloxacin 500mg', 'Take one tablet every 12 hours for 7 days'),
(7, 7, 'Vitamin D 1000 IU', 'Take one capsule daily'),
(8, 8, 'Cetirizine 10mg', 'Take one tablet once a day for allergy relief'),
(9, 9, 'Loratadine 10mg', 'Take one tablet once a day for 5 days'),
(10, 10, 'Metoprolol 50mg', 'Take one tablet twice a day');

-- Insert data into Feedback table
INSERT INTO Feedback (PatientID, AppointmentID, Rating, Comments) VALUES
(1, 1, 5, 'Excellent service and very professional.'),
(2, 2, 4, 'Good experience but had to wait a bit.'),
(3, 3, 3, 'Satisfactory service but room for improvement.'),
(4, 4, 5, 'Doctor was very thorough and kind.'),
(5, 5, 4, 'Good overall, helpful advice.'),
(6, 6, 5, 'Great experience, would recommend.'),
(7, 7, 3, 'It was okay, not too bad.'),
(8, 8, 4, 'Doctor was friendly and helpful.'),
(9, 9, 2, 'Long wait time, but doctor was good.'),
(10, 10, 5, 'Fantastic service and great doctor.');

-- Insert data into Waitlist table
INSERT INTO Waitlist (PatientID, DoctorID, AppointmentDate, AppointmentTime, Status) VALUES
(1, 1, '2024-11-25', '10:00:00', 'Pending'),
(2, 2, '2024-11-26', '11:00:00', 'Confirmed'),
(3, 3, '2024-11-27', '12:30:00', 'Pending'),
(4, 4, '2024-11-28', '14:00:00', 'Confirmed'),
(5, 5, '2024-11-29', '15:30:00', 'Pending'),
(6, 6, '2024-11-30', '08:45:00', 'Confirmed'),
(7, 7, '2024-12-01', '09:30:00', 'Pending'),
(8, 8, '2024-12-02', '10:15:00', 'Confirmed'),
(9, 9, '2024-12-03', '11:00:00', 'Pending'),
(10, 10, '2024-12-04', '12:00:00', 'Confirmed');
