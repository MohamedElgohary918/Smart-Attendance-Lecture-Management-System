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
```
--  Users table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    university_email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    user_type VARCHAR(20) CHECK (user_type IN ('student', 'doctor')) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

--  Embeddings table
CREATE TABLE embeddings (
    embedding_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    embedding_vector vector(512) NOT NULL,
    -- Foreign key constraint
    CONSTRAINT fk_user
        FOREIGN KEY(user_id) 
        REFERENCES users(user_id)
        ON DELETE CASCADE
);

-- Indexes for better performance
CREATE INDEX idx_embeddings_user_id ON embeddings(user_id);
CREATE INDEX idx_embeddings_vector ON embeddings USING ivfflat (embedding_vector vector_cosine_ops);
CREATE INDEX idx_users_email ON users(university_email);
CREATE INDEX idx_users_type ON users(user_type);


-- Test : Verify tables are created
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

```
