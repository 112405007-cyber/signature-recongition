import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Signature Recognition System"
    VERSION: str = "1.0.0"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./signature_recognition.db")
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}
    UPLOAD_FOLDER: str = "uploads"
    
    # ML Model Settings
    MODEL_PATH: str = "models/trained_models/"
    CONFIDENCE_THRESHOLD: float = 0.7
    
    # Image Processing
    IMAGE_SIZE: tuple = (224, 224)
    PREPROCESSING_STEPS: list = [
        "grayscale",
        "noise_reduction", 
        "normalization",
        "resize"
    ]

settings = Settings()
