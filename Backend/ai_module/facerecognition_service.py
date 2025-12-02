import numpy as np
import logging
from typing import List, Optional, Tuple, Union
from insightface.app import FaceAnalysis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FaceRecognitionService:
    """
    A flexible, production-ready class for InsightFace operations.
    Supports multiple models, CPU/GPU execution, and comprehensive error handling.
    """
    
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(FaceRecognitionService, cls).__new__(cls)
        return cls._instance

    def __init__(self,
                 model_name: str = "buffalo_sc",
                 provider: str = "CPU",
                 det_size: Tuple[int, int] = (640, 640),
                 ctx_id: int = 0):
        """
        Initialize the Face Recognition service.
        
        Args:
            model_name: InsightFace model name ('buffalo_sc', 'buffalo_l', etc.)
            provider: 'CPU' or 'GPU'
            det_size: Detection size as (width, height)
            ctx_id: GPU context ID (for GPU provider)
        """
        
        # Avoid reinitialization
        if hasattr(self, "initialized") and self.initialized:
            logger.info("FaceRecognitionService already initialized")
            return

        self.model_name = model_name
        self.provider = provider.upper()
        self.det_size = det_size
        self.ctx_id = ctx_id
        
        # Configure providers
        if self.provider == "GPU":
            self.providers = ["CUDAExecutionProvider"]
        else:
            self.providers = ["CPUExecutionProvider"]

        try:
            logger.info(f"Loading model {model_name} with {self.provider} provider")
            
            self.app = FaceAnalysis(
                name=model_name,
                providers=self.providers
            )
            self.app.prepare(ctx_id=ctx_id, det_size=det_size)
            
            self.initialized = True
            logger.info("FaceRecognitionService initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize FaceRecognitionService: {e}")
            raise

    # -----------------------------------------------------
    # ----------------- CORE METHODS ----------------------
    # -----------------------------------------------------

    def detect_faces(self, image: np.ndarray) -> List:
        """
        Detect all faces in the image.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            List of detected face objects
        """
        try:
            faces = self.app.get(image)
            logger.debug(f"Detected {len(faces)} faces")
            return faces
        except Exception as e:
            logger.error(f"Error in face detection: {e}")
            return []

    def get_embedding(self, image: np.ndarray, face_index: int = 0) -> Optional[np.ndarray]:
        """
        Get embedding for a single face from the image.
        
        Args:
            image: Input image as numpy array
            face_index: Index of face to get embedding from (default: 0)
            
        Returns:
            Face embedding or None if no face found
        """
        faces = self.detect_faces(image)
        
        if len(faces) == 0:
            logger.warning("No faces detected in image")
            return None
        
        if face_index >= len(faces):
            logger.warning(f"Face index {face_index} out of range. Using first face.")
            face_index = 0
            
        return faces[face_index].embedding

    def get_embeddings_multi(self, image: np.ndarray) -> List[np.ndarray]:
        """
        Get embeddings for all faces in the image.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            List of embeddings for all detected faces
        """
        faces = self.detect_faces(image)
        embeddings = [face.embedding for face in faces]
        logger.debug(f"Extracted {len(embeddings)} embeddings")
        return embeddings

    def get_detailed_faces(self, image: np.ndarray) -> List[dict]:
        """
        Get detailed information for all detected faces.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            List of dictionaries with face details
        """
        faces = self.detect_faces(image)
        detailed_faces = []
        
        for i, face in enumerate(faces):
            face_info = {
                'index': i,
                'embedding': face.embedding,
                'bbox': face.bbox,  # [x1, y1, x2, y2]
                'landmarks': face.kps if hasattr(face, 'kps') else None,
                'det_score': face.det_score,
                'gender': face.sex if hasattr(face, 'sex') else None,
                'age': face.age if hasattr(face, 'age') else None
            }
            detailed_faces.append(face_info)
            
        return detailed_faces

    @staticmethod
    def cosine_similarity(emb1: np.ndarray, emb2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings.
        
        Args:
            emb1: First embedding vector
            emb2: Second embedding vector
            
        Returns:
            Cosine similarity score between 0 and 1
        """
        try:
            emb1 = np.array(emb1).flatten()
            emb2 = np.array(emb2).flatten()
            
            if emb1.shape != emb2.shape:
                raise ValueError(f"Embedding shape mismatch: {emb1.shape} vs {emb2.shape}")
                
            similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error computing cosine similarity: {e}")
            return 0.0

    def match_face(self, query_embedding: np.ndarray, 
                   db_embeddings: List[np.ndarray], 
                   threshold: float = 0.6) -> Tuple[Optional[int], float]:
        """
        Find the best matching face from database embeddings.
        
        Args:
            query_embedding: Embedding to match
            db_embeddings: List of database embeddings to compare against
            threshold: Minimum similarity threshold for a match
            
        Returns:
            Tuple of (best_match_index, best_similarity_score)
        """
        if not db_embeddings:
            return None, 0.0
            
        best_similarity = -1.0
        best_index = None
        
        for i, db_emb in enumerate(db_embeddings):
            similarity = self.cosine_similarity(query_embedding, db_emb)
            
            if similarity > best_similarity and similarity >= threshold:
                best_similarity = similarity
                best_index = i
                
        return best_index, best_similarity

    def get_model_info(self) -> dict:
        """Get information about the loaded model."""
        return {
            'model_name': self.model_name,
            'provider': self.provider,
            'detection_size': self.det_size,
            'initialized': self.initialized
        }