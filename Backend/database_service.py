import psycopg2
import numpy as np
from psycopg2.extras import RealDictCursor
from config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        self.conn_params = {
            'host': settings.POSTGRES_SERVER,
            'port': settings.POSTGRES_PORT,
            'user': settings.POSTGRES_USER,
            'password': settings.POSTGRES_PASSWORD,
            'database': settings.POSTGRES_DB
        }
        self.conn = None
    
    def connect(self):
        try:
            self.conn = psycopg2.connect(**self.conn_params)
            logger.info("✅ Database connected successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            return False
    
    def disconnect(self):
        if self.conn:
            self.conn.close()
            logger.info("✅ Database connection closed")
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = False):
        """Execute a SQL query with proper cursor handling"""
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                if fetch:
                    result = cursor.fetchall()
                    return result
                else:
                    # For write operations, we'll commit separately
                    return cursor.rowcount
        except Exception as e:
            logger.error(f"❌ Query execution failed: {e}")
            raise e
    
    def commit(self):
        """Commit the current transaction"""
        if self.conn:
            self.conn.commit()
            logger.info("✅ Transaction committed")
    
    def rollback(self):
        """Rollback the current transaction"""
        if self.conn:
            self.conn.rollback()
            logger.warning("🔄 Transaction rolled back")
    
    def create_user(self, email: str, full_name: str, user_type: str, password_hash: str) -> int:
        """Create a new user and return user_id"""
        query = """
        INSERT INTO users (university_email, full_name, user_type, password_hash)
        VALUES (%s, %s, %s, %s)
        RETURNING user_id
        """
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, (email, full_name, user_type, password_hash))
                result = cursor.fetchone()
                self.conn.commit()  # Commit after successful execution
                user_id = result['user_id']
                logger.info(f"✅ User created with ID: {user_id}")
                return user_id
        except Exception as e:
            logger.error(f"❌ Failed to create user: {e}")
            self.conn.rollback()
            return None
    
    def store_embedding(self, user_id: int, embedding: np.ndarray) -> int:
        """Store a face embedding for a user"""
        embedding_list = embedding.tolist()
        
        query = """
        INSERT INTO embeddings (user_id, embedding_vector)
        VALUES (%s, %s::vector(512))
        RETURNING embedding_id
        """
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, (user_id, embedding_list))
                result = cursor.fetchone()
                self.conn.commit()  # Commit after successful execution
                embedding_id = result['embedding_id']
                logger.info(f"✅ Embedding stored for user_id {user_id}")
                return embedding_id
        except Exception as e:
            logger.error(f"❌ Failed to store embedding: {e}")
            self.conn.rollback()
            return None
    
    def user_exists(self, email: str) -> bool:
        """Check if a user with the given email already exists"""
        query = "SELECT 1 FROM users WHERE university_email = %s"
        try:
            result = self.execute_query(query, (email,), fetch=True)
            return bool(result)
        except Exception as e:
            logger.error(f"❌ Error checking user existence: {e}")
            return False
    
    def get_user_embeddings(self, user_id: int):
        """Get all embeddings for a specific user"""
        query = "SELECT embedding_vector FROM embeddings WHERE user_id = %s"
        try:
            result = self.execute_query(query, (user_id,), fetch=True)
            if result:
                embeddings = [np.array(row['embedding_vector']) for row in result]
                return embeddings
            return []
        except Exception as e:
            logger.error(f"❌ Error getting user embeddings: {e}")
            return []
    
    def find_similar_faces(self, query_embedding: np.ndarray, threshold: float = 0.6, limit: int = 5):
        """Find similar faces using cosine similarity"""
        query_embedding_list = query_embedding.tolist()
        
        query = """
        SELECT 
            u.user_id,
            u.full_name,
            u.university_email,
            (1 - (e.embedding_vector <=> %s::vector(512)) / 2) as similarity
        FROM embeddings e
        JOIN users u ON e.user_id = u.user_id
        WHERE (1 - (e.embedding_vector <=> %s::vector(512)) / 2) > %s
        ORDER BY similarity DESC
        LIMIT %s
        """
        try:
            result = self.execute_query(query, (query_embedding_list, query_embedding_list, threshold, limit), fetch=True)
            return result if result else []
        except Exception as e:
            logger.error(f"❌ Error finding similar faces: {e}")
            return []