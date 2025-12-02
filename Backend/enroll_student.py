from database_service import DatabaseService
from ai_module.facerecognition_service import FaceRecognitionService
import cv2
import os

def enroll_student(student_email: str, student_name: str, image_paths: list):
    """
    Simple student enrollment - stores face embeddings in database
    """
    print(f"Enrolling: {student_name} ({student_email})")
    
    # Initialize services
    db = DatabaseService()
    face_rec = FaceRecognitionService()
    
    if not db.connect():
        print("Database connection failed")
        return False
    
    try:
        # Create user
        user_id = db.create_user(
            email=student_email,
            full_name=student_name,
            user_type="student",
            password_hash="temp_hash"
        )
        
        if not user_id:
            print("Failed to create user")
            return False
        
        print(f"User created with ID: {user_id}")
        
        # Process images and store embeddings
        stored_count = 0
        
        for i, image_path in enumerate(image_paths):
            print(f"Processing image {i+1}/{len(image_paths)}: {os.path.basename(image_path)}")
            
            if not os.path.exists(image_path):
                print(f"   ❌ Image not found: {image_path}")
                continue
                
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                print(f"   ❌ Could not load image: {image_path}")
                continue
            
            # Convert to RGB and get embedding
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            embedding = face_rec.get_embedding(image_rgb)
            
            if embedding is not None:
                db.store_embedding(user_id, embedding)
                stored_count += 1
                print(f"   ✅ Embedding stored")
            else:
                print(f"   ❌ No face detected")
        
        print(f"Enrollment completed: {stored_count} embeddings stored")
        return stored_count > 0
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        db.disconnect()


def simple_test():
    """Simple test without verification"""
    print("Simple Enrollment Test")
    
    # ✅ FIXED PATHS - removed duplicate "images"
    test_images = [
        "Backend/images/student-Angelina Jolie/angelina-1.jpeg",
        "Backend/images/student-Angelina Jolie/angelina-2.jpeg", 
        "Backend/images/student-Angelina Jolie/angelina-3.jpeg",
        "Backend/images/student-Angelina Jolie/angelina-4.jpeg", 
        "Backend/images/student-Angelina Jolie/angelina-5.jpeg"
    ]
    
    # Run enrollment
    success = enroll_student(
        student_email="angelina@university.edu",
        student_name="Angelina Jolie", 
        image_paths=test_images
    )
    
    if success:
        print("Test completed successfully")
    else:
        print("Test failed")

if __name__ == "__main__":
    simple_test()