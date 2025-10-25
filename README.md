# Smart-Attendance-Lecture-Management-System
## **Overview**

The _Smart Attendance & Lecture Management System_ is a mobile-based solution designed to help **university students** and **professors (doctors)** manage their weekly lectures and attendance seamlessly.  
The system automates the process of **taking attendance using computer vision** by identifying students through facial recognition and synchronizing the data with the university’s lecture schedule.
The project provides two types of accounts:
- **Student Account:** allows students to register, view their weekly schedule, and track attendance history.
- **Doctor Account:** allows professors to register, manage their courses, and automatically receive attendance reports after each lecture.

The main innovation lies in the **AI-based face recognition module**, which automatically detects students’ faces during lectures and sends accurate attendance data to the database without manual input.

---
## **Core Features**

**Student Features**
- Register using university email and personal details.
- Capture 5 facial images (different poses and lighting) to create embeddings for recognition.
- View personal timetable and attendance record.
- Secure login and profile management.

 **Doctor Features**
- Register with name, courses taught, and login credentials.
- Automatically receive attendance reports for each lecture.
- View attendance statistics and student participation.

**AI Module**
- Captures live images from the camera in each lecture hall.    
- Detects and recognizes student faces using a pre-trained face recognition model .
- Generates embeddings for new faces and compares them to existing ones in the PostgreSQL database using the **pgvector** extension.
- Sends attendance data to the backend automatically after each lecture.

---
##  **System Architecture**

**Main Components**

| Component                 | Description                                                                | Technology       |
| ------------------------- | -------------------------------------------------------------------------- | ---------------- |
| **Mobile App**            | Interface for students and professors to manage accounts and schedules.    | Flutter          |
| **Backend API**           | Handles registration, authentication, and communication with the database. | FastAPI (Python) |
| **Database**              | Stores user data, schedules, and embeddings.                               | PostgreSQL       |
| **AI Recognition Module** | Detects faces and performs embedding comparison for attendance marking.    | Python           |

---
## **Data Flow**

1. **Registration:**

    - Student or doctor signs up via the mobile app.        
    - The app sends data (name, email, password, etc.) and 5 face images to the backend.
    - The backend generates embeddings and stores them in PostgreSQL.
        
2. **Lecture Time:**
    
    - The camera in the lecture hall captures student faces.
    - The AI module generates embeddings for detected faces.
    - It compares these embeddings with those in PostgreSQL using cosine similarity .
    - Matches are marked as “present” and attendance is updated.
        
3. **Post-Lecture:**
    
    - Attendance data is sent to the backend and linked to the respective course and doctor.
    - Students and professors can view attendance summaries in the app.

---
##  **Technologies Used**

| Layer            | Technology                      | Purpose                           |
| ---------------- | ------------------------------- | --------------------------------- |
| Frontend         | Flutter                         | Cross-platform mobile app         |
| Backend          | FastAPI                         | API and business logic            |
| Database         | PostgreSQL + pgvector           | Store user data + embeddings      |
| AI Module        | OpenCV, face_recognition, NumPy | Facial detection and comparison   |
| ORM              | SQLAlchemy                      | Database interaction              |
| Authentication   | JWT                             | Secure login                      |
| Local Deployment | Docker (optional)               | Containerized testing environment |

---
## **Team Roles and Responsibilities**

 **1. Mohamed — Computer Vision Engineer**
 **2. Mina — Computer Vision Engineer**
**Main Focus:**
- Facial recognition system and attendance automation
- Camera integration and data collection
 **3. Mark — Mobile App Developer**
 **4. Ahmed — Mobile App Developer**
**Main Focus:**
- Student & Doctor mobile app interface
- App functionality and backend integration
 **5. Mina Naseh — Backend Engineer**
**6. AIad — Backend Engineer**
**Main Focus:**
- Database and API development
- System integration and communication logic
---
##  **Prototype Goals (Local Demo Version)**

The first version will be **locally deployed** to test the workflow:
- Simple Flutter interface for registration and attendance view.
- Local FastAPI backend connecting to PostgreSQL.
- Pre-trained face recognition model for embeddg generation and comparison.
- Small dataset (e.g., 10–20 students, 2–3 courses) to validate the idea.

---
##  **Future Enhancements**

- Cloud deployment .    
- Real-time camera feed integration.
- Attendance statistics dashboard for professors.
-  Chat bot to answer student questions.
- Push notifications for absences or updates.

---
## project timeline

|**Week**|**Task**|**Description**|
|---|---|---|
|Week 1|Research Technologies|Search for and choose the most suitable tools and frameworks for the project.|
|Week 2|Learn Essential Tools|Each member learns the basics of the selected technologies (Flutter, FastAPI, PostgreSQL, etc.).|
|Week 3|Database Design|Build the database schema using PostgreSQL and test it locally.|
|Week 4|Backend API Development|Develop and test APIs using FastAPI to connect with the database.|
|Week 5–6|Mobile App Development|Build the Flutter frontend and connect it to backend APIs.|
|Week 6–7|Computer Vision Integration|Develop and integrate the AI model for face recognition with backend and database.

	
