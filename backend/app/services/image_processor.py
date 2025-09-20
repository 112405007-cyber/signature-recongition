import cv2
import numpy as np
from PIL import Image
import io
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Handles image preprocessing for signature analysis"""
    
    def __init__(self, target_size: Tuple[int, int] = (224, 224)):
        self.target_size = target_size
    
    def load_image(self, image_data: bytes) -> np.ndarray:
        """Load image from bytes"""
        try:
            image = Image.open(io.BytesIO(image_data))
            return np.array(image)
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            raise ValueError("Invalid image format")
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Apply preprocessing steps to the image"""
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Apply noise reduction
            image = cv2.medianBlur(image, 3)
            
            # Apply adaptive thresholding
            image = cv2.adaptiveThreshold(
                image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Resize to target size
            image = cv2.resize(image, self.target_size)
            
            # Normalize
            image = image.astype(np.float32) / 255.0
            
            return image
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            raise ValueError("Image preprocessing failed")
    
    def extract_contours(self, image: np.ndarray) -> list:
        """Extract contours from the image"""
        try:
            # Convert to binary if needed
            if image.dtype != np.uint8:
                image = (image * 255).astype(np.uint8)
            
            # Find contours
            contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            return contours
        except Exception as e:
            logger.error(f"Error extracting contours: {e}")
            return []
    
    def get_image_properties(self, image: np.ndarray) -> dict:
        """Get basic properties of the image"""
        try:
            height, width = image.shape[:2]
            
            # Calculate signature density
            signature_pixels = np.sum(image < 0.5)  # Assuming dark pixels are signature
            total_pixels = height * width
            density = signature_pixels / total_pixels if total_pixels > 0 else 0
            
            # Calculate aspect ratio
            aspect_ratio = width / height if height > 0 else 0
            
            return {
                "height": height,
                "width": width,
                "density": density,
                "aspect_ratio": aspect_ratio,
                "total_pixels": total_pixels,
                "signature_pixels": signature_pixels
            }
        except Exception as e:
            logger.error(f"Error getting image properties: {e}")
            return {}
    
    def enhance_image(self, image: np.ndarray) -> np.ndarray:
        """Enhance image quality for better analysis"""
        try:
            # Apply morphological operations
            kernel = np.ones((2, 2), np.uint8)
            image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
            image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
            
            # Apply Gaussian blur for smoothing
            image = cv2.GaussianBlur(image, (3, 3), 0)
            
            return image
        except Exception as e:
            logger.error(f"Error enhancing image: {e}")
            return image
    
    def save_processed_image(self, image: np.ndarray, filepath: str) -> bool:
        """Save processed image to file"""
        try:
            # Convert back to uint8 if needed
            if image.dtype != np.uint8:
                image = (image * 255).astype(np.uint8)
            
            cv2.imwrite(filepath, image)
            return True
        except Exception as e:
            logger.error(f"Error saving image: {e}")
            return False
