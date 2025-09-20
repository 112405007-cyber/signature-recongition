import cv2
import numpy as np
from typing import Dict, List, Tuple
import logging
from scipy import ndimage
from skimage import measure, feature
import json

logger = logging.getLogger(__name__)

class FeatureExtractor:
    """Extract features from signature images for analysis"""
    
    def __init__(self):
        self.feature_names = [
            'aspect_ratio', 'density', 'centroid_x', 'centroid_y',
            'compactness', 'eccentricity', 'solidity', 'convexity',
            'stroke_width_mean', 'stroke_width_std', 'stroke_direction',
            'curvature_mean', 'curvature_std', 'pressure_variation',
            'pen_lifts', 'writing_speed', 'acceleration'
        ]
    
    def extract_all_features(self, image: np.ndarray) -> Dict[str, float]:
        """Extract all features from the signature image"""
        try:
            features = {}
            
            # Basic geometric features
            features.update(self._extract_geometric_features(image))
            
            # Stroke features
            features.update(self._extract_stroke_features(image))
            
            # Texture features
            features.update(self._extract_texture_features(image))
            
            # Dynamic features (simulated)
            features.update(self._extract_dynamic_features(image))
            
            return features
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            return {}
    
    def _extract_geometric_features(self, image: np.ndarray) -> Dict[str, float]:
        """Extract geometric features from the image"""
        try:
            # Convert to binary
            binary_image = (image < 0.5).astype(np.uint8)
            
            # Find contours
            contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return {}
            
            # Get the largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Calculate geometric features
            area = cv2.contourArea(largest_contour)
            perimeter = cv2.arcLength(largest_contour, True)
            
            # Bounding rectangle
            x, y, w, h = cv2.boundingRect(largest_contour)
            aspect_ratio = w / h if h > 0 else 0
            
            # Centroid
            moments = cv2.moments(largest_contour)
            if moments['m00'] != 0:
                centroid_x = moments['m10'] / moments['m00']
                centroid_y = moments['m01'] / moments['m00']
            else:
                centroid_x = centroid_y = 0
            
            # Compactness
            compactness = (perimeter ** 2) / area if area > 0 else 0
            
            # Ellipse fitting
            if len(largest_contour) >= 5:
                ellipse = cv2.fitEllipse(largest_contour)
                (center, axes, orientation) = ellipse
                major_axis = max(axes)
                minor_axis = min(axes)
                eccentricity = np.sqrt(1 - (minor_axis / major_axis) ** 2) if major_axis > 0 else 0
            else:
                eccentricity = 0
            
            # Convex hull
            hull = cv2.convexHull(largest_contour)
            hull_area = cv2.contourArea(hull)
            solidity = area / hull_area if hull_area > 0 else 0
            
            # Convexity
            convexity = cv2.arcLength(hull, True) / perimeter if perimeter > 0 else 0
            
            return {
                'aspect_ratio': aspect_ratio,
                'density': area / (image.shape[0] * image.shape[1]),
                'centroid_x': centroid_x / image.shape[1],  # Normalized
                'centroid_y': centroid_y / image.shape[0],  # Normalized
                'compactness': compactness,
                'eccentricity': eccentricity,
                'solidity': solidity,
                'convexity': convexity
            }
        except Exception as e:
            logger.error(f"Error extracting geometric features: {e}")
            return {}
    
    def _extract_stroke_features(self, image: np.ndarray) -> Dict[str, float]:
        """Extract stroke-related features"""
        try:
            # Convert to binary
            binary_image = (image < 0.5).astype(np.uint8)
            
            # Skeletonization
            skeleton = self._skeletonize(binary_image)
            
            # Calculate stroke width
            stroke_widths = self._calculate_stroke_width(binary_image)
            
            # Calculate stroke direction
            stroke_direction = self._calculate_stroke_direction(skeleton)
            
            return {
                'stroke_width_mean': np.mean(stroke_widths) if stroke_widths else 0,
                'stroke_width_std': np.std(stroke_widths) if stroke_widths else 0,
                'stroke_direction': stroke_direction
            }
        except Exception as e:
            logger.error(f"Error extracting stroke features: {e}")
            return {}
    
    def _extract_texture_features(self, image: np.ndarray) -> Dict[str, float]:
        """Extract texture features"""
        try:
            # Convert to uint8
            if image.dtype != np.float32:
                image = (image * 255).astype(np.uint8)
            
            # Calculate Local Binary Pattern
            lbp = feature.local_binary_pattern(image, 8, 1, method='uniform')
            
            # Calculate texture statistics
            texture_mean = np.mean(lbp)
            texture_std = np.std(lbp)
            
            # Calculate gradient features
            grad_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            return {
                'texture_mean': texture_mean,
                'texture_std': texture_std,
                'gradient_mean': np.mean(gradient_magnitude),
                'gradient_std': np.std(gradient_magnitude)
            }
        except Exception as e:
            logger.error(f"Error extracting texture features: {e}")
            return {}
    
    def _extract_dynamic_features(self, image: np.ndarray) -> Dict[str, float]:
        """Extract dynamic features (simulated based on image characteristics)"""
        try:
            # These are simulated features since we don't have temporal data
            # In a real system, these would come from pressure-sensitive devices
            
            # Simulate pressure variation based on stroke thickness
            binary_image = (image < 0.5).astype(np.uint8)
            stroke_widths = self._calculate_stroke_width(binary_image)
            
            pressure_variation = np.std(stroke_widths) if stroke_widths else 0
            
            # Simulate pen lifts based on disconnected components
            num_labels, labels = cv2.connectedComponents(binary_image)
            pen_lifts = max(0, num_labels - 1)
            
            # Simulate writing speed based on stroke complexity
            skeleton = self._skeletonize(binary_image)
            skeleton_length = np.sum(skeleton)
            writing_speed = skeleton_length / (image.shape[0] * image.shape[1])
            
            # Simulate acceleration based on curvature
            curvature = self._calculate_curvature(skeleton)
            acceleration = np.std(curvature) if curvature else 0
            
            return {
                'pressure_variation': pressure_variation,
                'pen_lifts': pen_lifts,
                'writing_speed': writing_speed,
                'acceleration': acceleration,
                'curvature_mean': np.mean(curvature) if curvature else 0,
                'curvature_std': np.std(curvature) if curvature else 0
            }
        except Exception as e:
            logger.error(f"Error extracting dynamic features: {e}")
            return {}
    
    def _skeletonize(self, image: np.ndarray) -> np.ndarray:
        """Skeletonize the binary image"""
        try:
            from skimage.morphology import skeletonize
            return skeletonize(image).astype(np.uint8)
        except ImportError:
            # Fallback to OpenCV-based skeletonization
            kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
            skeleton = np.zeros_like(image)
            while True:
                eroded = cv2.erode(image, kernel)
                temp = cv2.dilate(eroded, kernel)
                temp = cv2.subtract(image, temp)
                skeleton = cv2.bitwise_or(skeleton, temp)
                image = eroded.copy()
                if cv2.countNonZero(image) == 0:
                    break
            return skeleton
    
    def _calculate_stroke_width(self, binary_image: np.ndarray) -> List[float]:
        """Calculate stroke width at various points"""
        try:
            # Use distance transform
            dist_transform = cv2.distanceTransform(binary_image, cv2.DIST_L2, 5)
            
            # Get stroke widths
            stroke_widths = dist_transform[dist_transform > 0] * 2  # Multiply by 2 for diameter
            
            return stroke_widths.tolist()
        except Exception as e:
            logger.error(f"Error calculating stroke width: {e}")
            return []
    
    def _calculate_stroke_direction(self, skeleton: np.ndarray) -> float:
        """Calculate dominant stroke direction"""
        try:
            # Use Hough line transform
            lines = cv2.HoughLines(skeleton, 1, np.pi/180, threshold=50)
            
            if lines is not None:
                angles = []
                for line in lines:
                    rho, theta = line[0]
                    angles.append(theta)
                
                # Calculate mean direction
                mean_angle = np.mean(angles)
                return mean_angle
            else:
                return 0
        except Exception as e:
            logger.error(f"Error calculating stroke direction: {e}")
            return 0
    
    def _calculate_curvature(self, skeleton: np.ndarray) -> List[float]:
        """Calculate curvature along the skeleton"""
        try:
            # Find skeleton points
            points = np.column_stack(np.where(skeleton > 0))
            
            if len(points) < 3:
                return []
            
            # Calculate curvature using finite differences
            curvatures = []
            for i in range(1, len(points) - 1):
                p1, p2, p3 = points[i-1], points[i], points[i+1]
                
                # Calculate curvature
                v1 = p2 - p1
                v2 = p3 - p2
                
                # Cross product magnitude
                cross_product = np.abs(np.cross(v1, v2))
                
                # Vector magnitudes
                v1_mag = np.linalg.norm(v1)
                v2_mag = np.linalg.norm(v2)
                
                if v1_mag > 0 and v2_mag > 0:
                    curvature = cross_product / (v1_mag * v2_mag)
                    curvatures.append(curvature)
            
            return curvatures
        except Exception as e:
            logger.error(f"Error calculating curvature: {e}")
            return []
    
    def features_to_json(self, features: Dict[str, float]) -> str:
        """Convert features dictionary to JSON string"""
        try:
            return json.dumps(features, indent=2)
        except Exception as e:
            logger.error(f"Error converting features to JSON: {e}")
            return "{}"
    
    def features_from_json(self, features_json: str) -> Dict[str, float]:
        """Convert JSON string to features dictionary"""
        try:
            return json.loads(features_json)
        except Exception as e:
            logger.error(f"Error converting JSON to features: {e}")
            return {}
