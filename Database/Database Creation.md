```
# Install build dependencies
sudo apt install build-essential postgresql-server-dev-18 git

# Clone pgvector repository
git clone https://github.com/pgvector/pgvector.git
cd pgvector

# Build and install
make
sudo make install

# Clean up
cd ..
rm -rf pgvector
```

Enable pgvector Extension in Your Database
```
sudo -u postgres psql

-- 1. Create the database (if not already created)
CREATE DATABASE smart_attendance_system;

-- 2. Connect to your database
\c smart_attendance_system;

-- 3. Enable the vector extension
CREATE EXTENSION vector;

-- 4. Verify the extension is installed
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';
```
## Create Tables 

### Users table 
```
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(20) CHECK (role IN ('student', 'doctor')) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);
```

###  Embeddings table
```
CREATE TABLE embeddings (
    embedding_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    face_vector vector(512) NOT NULL,
    
    CONSTRAINT fk_embeddings_user
        FOREIGN KEY(user_id) 
        REFERENCES users(user_id)
        ON DELETE CASCADE
);
```

### Courses table
```
CREATE TABLE courses (
    course_id SERIAL PRIMARY KEY,
    course_name VARCHAR(255) NOT NULL,
    doctor_id INTEGER NOT NULL,
    schedule TEXT,
    
    CONSTRAINT fk_courses_doctor
        FOREIGN KEY(doctor_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,
    
    CONSTRAINT chk_doctor_role
        CHECK (EXISTS (
            SELECT 1 FROM users 
            WHERE user_id = doctor_id 
            AND role = 'doctor'
        ))
);
```

### Attendance table
```
CREATE TABLE attendance (
    attendance_id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    lecture_date DATE NOT NULL,
    is_present BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confidence_score FLOAT CHECK (confidence_score >= 0 AND confidence_score <= 1),
    
    CONSTRAINT fk_attendance_student
        FOREIGN KEY(student_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,
    
    CONSTRAINT fk_attendance_course
        FOREIGN KEY(course_id)
        REFERENCES courses(course_id)
        ON DELETE CASCADE,
    
    CONSTRAINT chk_student_role
        CHECK (EXISTS (
            SELECT 1 FROM users 
            WHERE user_id = student_id 
            AND role = 'student'
        )),
    
    -- Ensure unique attendance record per student per course per date
    CONSTRAINT unique_attendance_record 
        UNIQUE(student_id, course_id, lecture_date)
);
```

### Test : Verify tables are created
```
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
```

###  Database Indexes
```

-- Users indexes
CREATE INDEX idx_users_email ON users(email);

-- Embeddings indexes
CREATE INDEX idx_embeddings_user_id ON embeddings(user_id);
CREATE INDEX idx_embeddings_vector ON embeddings USING ivfflat (face_vector vector_cosine_ops);

-- Courses indexes
CREATE INDEX idx_courses_doctor_id ON courses(doctor_id);
CREATE INDEX idx_courses_name ON courses(course_name);

-- Attendance indexes
CREATE INDEX idx_attendance_student_id ON attendance(student_id);
CREATE INDEX idx_attendance_course_id ON attendance(course_id);
CREATE INDEX idx_attendance_student_course ON attendance(student_id, course_id);

-- Composite indexes for common queries
CREATE INDEX idx_attendance_course_date ON attendance(course_id, lecture_date);
CREATE INDEX idx_attendance_student_date ON attendance(student_id, lecture_date);

```

## Explain the Relationship between tables 
### **1. `users` ↔ `embeddings` Relationship**
**Type: One-to-Many (1:N)**
- **One user** can have **multiple face embeddings** (typically 5 per student)
- **Each embedding** belongs to exactly **one user**
### **2. `users` ↔ `courses` Relationship**
**Type: Many-to-Many (N:N)**
- **One doctor** can teach **multiple courses**
- **One student** can enroll in many courses
- **One course** can have many students enrolled
### **3. `users` ↔ `attendance` Relationship**
**Type: One-to-Many (1:N)**
- **One student** can have **multiple attendance records** (one per lecture)
- **Each attendance record** belongs to exactly **one student**
### **4. `courses` ↔ `attendance` Relationship**
**Type: One-to-Many (1:N)**
- **One course** can have **multiple attendance records** (for different dates/students)
- **Each attendance record** is for exactly **one course**