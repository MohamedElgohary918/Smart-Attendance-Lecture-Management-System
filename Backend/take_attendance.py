from database_service import DatabaseService
from ai_module.facerecognition_service import FaceRecognitionService
import cv2
import os

def take_attendance(image_path, threshold=0.6):
    """
    Take attendance from an image - detect faces and match with database
    """
    db = DatabaseService()
    face_rec = FaceRecognitionService()
    
    if not db.connect():
        return []
    
    try:
        # Check if image exists
        if not os.path.exists(image_path):
            print(f"Image not found: {image_path}")
            return []
        
        # Load and process image
        image = cv2.imread(image_path)
        if image is None:
            print(f"Could not load image: {image_path}")
            return []
            
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Detect all faces in the image
        embeddings = face_rec.get_embeddings_multi(image_rgb)
        
        if not embeddings:
            print("No faces detected in the image")
            return []
        
        print(f"Found {len(embeddings)} faces")
        
        # Match each face with database
        present_students = []
        
        for embedding in embeddings:
            matches = db.find_similar_faces(embedding, threshold=threshold, limit=1)
            
            if matches and matches[0]['similarity'] > threshold:
                student = matches[0]
                present_students.append({
                    'user_id': student['user_id'],
                    'name': student['full_name'],
                    'email': student['university_email'],
                    'confidence': student['similarity']
                })
                print(f"Recognized: {student['full_name']} ({student['similarity']:.3f})")
        
        return present_students
        
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        db.disconnect()

