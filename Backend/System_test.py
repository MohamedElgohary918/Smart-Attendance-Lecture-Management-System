from database_service import DatabaseService
from ai_module.facerecognition_service import FaceRecognitionService
from take_attendance import take_attendance
import cv2
import os

def quick_enroll():
    """Quick enrollment of all people with correct image paths"""
    people = [
        # Students
        {"email": "chris@uni.edu", "name": "Chris Evans", "type": "student", "folder": "student-Chris_Evans", "prefix": "evans", "images": [1,2,3,4,5]},
        {"email": "scarlett@uni.edu", "name": "Scarlett Johansson", "type": "student", "folder": "student-Scarlett Johansson", "prefix": "scarlet", "images": [4,7,10,13,14]},
        # Teachers  
        {"email": "barack@uni.edu", "name": "Barack Obama", "type": "doctor", "folder": "teacher-Barack_Obama", "prefix": "obama", "images": [1,2,3,4,5]},
        {"email": "morgan@uni.edu", "name": "Morgan Freeman", "type": "doctor", "folder": "teacher-Morgan_Freeman", "prefix": "freeman", "images": [1,2,3,4,5]},
    ]
    
    db = DatabaseService()
    face_rec = FaceRecognitionService()
    
    if not db.connect():
        print("❌ Database connection failed")
        return
    
    total_embeddings = 0
    
    for person in people:
        user_id = db.create_user(person["email"], person["name"], person["type"], "hash")
        if user_id:
            print(f"👤 Enrolling: {person['name']}")
            embeddings_stored = 0
            
            for img_num in person["images"]:
                # ✅ CORRECT PATH GENERATION
                img_path = f"Backend/images/{person['folder']}/{person['prefix']}_{img_num}.jpeg"
                
                if os.path.exists(img_path):
                    image = cv2.imread(img_path)
                    if image is not None:
                        embedding = face_rec.get_embedding(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                        if embedding is not None:
                            db.store_embedding(user_id, embedding)
                            embeddings_stored += 1
                            print(f"   ✅ Stored: {os.path.basename(img_path)}")
                        else:
                            print(f"   ❌ No face: {os.path.basename(img_path)}")
                    else:
                        print(f"   ❌ Can't load: {os.path.basename(img_path)}")
                else:
                    print(f"   ❌ Not found: {img_path}")
            
            total_embeddings += embeddings_stored
            print(f"   📊 {embeddings_stored} embeddings stored for {person['name']}\n")
        else:
            print(f"❌ Failed to create user: {person['name']}")
    
    db.disconnect()
    print(f"🎉 Enrollment complete! Total embeddings: {total_embeddings}")
    
# Run everything
if __name__ == "__main__":
    
    print("🚀 Running Complete System Test")
    print("=" * 50)
    
    # Enroll everyone
    quick_enroll()
    
    # Test attendance
    print("\n📷 Testing Attendance...")
    attendance_image = "Backend/images/Chris&Scarlett.jpg"
    
    if os.path.exists(attendance_image):
        results = take_attendance(attendance_image)
        
        print(f"\n📊 ATTENDANCE RESULTS: {len(results)} people present")
        if results:
            for person in results:
                print(f"   ✅ {person['name']} - {person['confidence']:.1%} confidence")
        else:
            print("   ❌ No one recognized")
    else:
        print(f"❌ Attendance image not found: {attendance_image}")