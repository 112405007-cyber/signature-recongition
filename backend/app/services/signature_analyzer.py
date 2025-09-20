import numpy as np
from typing import Dict, Tuple, List
import logging
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os
from pathlib import Path

from .feature_extractor import FeatureExtractor
from .image_processor import ImageProcessor
from config import settings

logger = logging.getLogger(__name__)

class SignatureAnalyzer:
    """Main class for signature analysis and verification"""
    
    def __init__(self):
        self.feature_extractor = FeatureExtractor()
        self.image_processor = ImageProcessor()
        self.scaler = StandardScaler()
        self.model = None
        self.is_trained = False
        self.model_path = os.path.join(settings.MODEL_PATH, "signature_model.pkl")
        self.scaler_path = os.path.join(settings.MODEL_PATH, "scaler.pkl")
        
        # Load existing model if available
        self._load_model()
    
    def analyze_signature(self, image_data: bytes, template_features: Dict = None) -> Dict:
        """Analyze a signature and return authenticity results"""
        try:
            start_time = time.time()
            
            # Process image
            image = self.image_processor.load_image(image_data)
            processed_image = self.image_processor.preprocess_image(image)
            
            # Extract features
            features = self.feature_extractor.extract_all_features(processed_image)
            
            if not features:
                return {
                    "authenticity_score": 0.0,
                    "confidence_level": 0.0,
                    "is_authentic": False,
                    "analysis_details": "Failed to extract features",
                    "processing_time": 0.0
                }
            
            # Convert features to array
            feature_array = self._features_to_array(features)
            
            # Analyze authenticity
            if template_features:
                # Compare with template
                authenticity_score, confidence = self._compare_with_template(
                    features, template_features
                )
            else:
                # Use ML model
                authenticity_score, confidence = self._predict_authenticity(feature_array)
            
            # Determine if authentic
            is_authentic = authenticity_score >= settings.CONFIDENCE_THRESHOLD
            
            processing_time = time.time() - start_time
            
            return {
                "authenticity_score": float(authenticity_score),
                "confidence_level": float(confidence),
                "is_authentic": is_authentic,
                "analysis_details": self._generate_analysis_details(features, authenticity_score),
                "processing_time": processing_time,
                "extracted_features": features
            }
            
        except Exception as e:
            logger.error(f"Error analyzing signature: {e}")
            return {
                "authenticity_score": 0.0,
                "confidence_level": 0.0,
                "is_authentic": False,
                "analysis_details": f"Analysis failed: {str(e)}",
                "processing_time": 0.0
            }
    
    def _compare_with_template(self, features: Dict, template_features: Dict) -> Tuple[float, float]:
        """Compare signature features with template using improved algorithm"""
        try:
            # Enhanced feature weights for better discrimination
            weights = {
                'aspect_ratio': 0.20,      # Very important for signature shape
                'density': 0.15,           # Important for signature style
                'centroid_x': 0.10,        # Position matters
                'centroid_y': 0.10,        # Position matters
                'compactness': 0.15,       # Shape complexity
                'eccentricity': 0.10,      # Shape orientation
                'solidity': 0.10,          # Shape solidity
                'convexity': 0.10,         # Shape convexity
                'stroke_width_mean': 0.10, # Stroke characteristics
                'stroke_width_std': 0.05,  # Stroke variation
                'curvature_mean': 0.05,    # Writing style
                'curvature_std': 0.05,     # Writing consistency
                'pressure_variation': 0.05, # Writing pressure
                'pen_lifts': 0.05,         # Writing continuity
                'writing_speed': 0.05,     # Writing speed
                'acceleration': 0.05       # Writing dynamics
            }
            
            similarities = []
            total_weight = 0
            
            for feature_name, weight in weights.items():
                if feature_name in features and feature_name in template_features:
                    feature_val = features[feature_name]
                    template_val = template_features[feature_name]
                    
                    # Handle different feature types
                    if feature_name in ['aspect_ratio', 'density', 'compactness', 'eccentricity', 'solidity', 'convexity']:
                        # For ratio-based features, use relative difference
                        if template_val > 0:
                            relative_diff = abs(feature_val - template_val) / template_val
                            similarity = max(0, 1 - relative_diff)
                        else:
                            similarity = 1.0 if abs(feature_val - template_val) < 0.01 else 0.0
                    
                    elif feature_name in ['centroid_x', 'centroid_y']:
                        # For position features, use absolute difference (normalized to 0-1)
                        diff = abs(feature_val - template_val)
                        similarity = max(0, 1 - (diff * 2))  # Scale factor for position
                    
                    elif feature_name in ['stroke_width_mean', 'stroke_width_std', 'curvature_mean', 'curvature_std']:
                        # For stroke features, use relative difference
                        if template_val > 0:
                            relative_diff = abs(feature_val - template_val) / template_val
                            similarity = max(0, 1 - relative_diff)
                        else:
                            similarity = 1.0 if abs(feature_val - template_val) < 0.01 else 0.0
                    
                    elif feature_name in ['pen_lifts']:
                        # For discrete features, use exact match with tolerance
                        diff = abs(feature_val - template_val)
                        similarity = 1.0 if diff <= 1 else max(0, 1 - (diff - 1) * 0.5)
                    
                    else:
                        # For other features, use normalized difference
                        max_val = max(abs(feature_val), abs(template_val), 1e-6)
                        diff = abs(feature_val - template_val)
                        similarity = max(0, 1 - (diff / max_val))
                    
                    similarities.append(similarity * weight)
                    total_weight += weight
            
            # Calculate weighted average
            if similarities and total_weight > 0:
                authenticity_score = sum(similarities) / total_weight
                
                # Apply stricter thresholds for better discrimination
                if authenticity_score >= 0.85:
                    confidence = min(authenticity_score * 1.1, 1.0)
                elif authenticity_score >= 0.70:
                    confidence = authenticity_score * 0.9
                elif authenticity_score >= 0.50:
                    confidence = authenticity_score * 0.7
                else:
                    confidence = authenticity_score * 0.5
                
                # Additional validation: if key features are very different, lower the score
                key_features = ['aspect_ratio', 'density', 'compactness']
                key_differences = []
                
                for key_feature in key_features:
                    if key_feature in features and key_feature in template_features:
                        if template_features[key_feature] > 0:
                            rel_diff = abs(features[key_feature] - template_features[key_feature]) / template_features[key_feature]
                            key_differences.append(rel_diff)
                
                if key_differences and max(key_differences) > 0.5:  # 50% difference in key features
                    authenticity_score *= 0.7  # Reduce score significantly
                    confidence *= 0.8
                
            else:
                authenticity_score = 0.0
                confidence = 0.0
            
            return authenticity_score, confidence
            
        except Exception as e:
            logger.error(f"Error comparing with template: {e}")
            return 0.0, 0.0
    
    def _predict_authenticity(self, feature_array: np.ndarray) -> Tuple[float, float]:
        """Predict authenticity using ML model"""
        try:
            if not self.is_trained:
                # Use rule-based approach if model not trained
                return self._rule_based_analysis(feature_array)
            
            # Normalize features
            feature_array_scaled = self.scaler.transform(feature_array.reshape(1, -1))
            
            # Predict
            prediction = self.model.predict_proba(feature_array_scaled)[0]
            authenticity_score = prediction[1] if len(prediction) > 1 else prediction[0]
            confidence = authenticity_score
            
            return authenticity_score, confidence
            
        except Exception as e:
            logger.error(f"Error predicting authenticity: {e}")
            return self._rule_based_analysis(feature_array)
    
    def _rule_based_analysis(self, feature_array: np.ndarray) -> Tuple[float, float]:
        """Rule-based analysis when ML model is not available"""
        try:
            # Simple rule-based scoring
            score = 0.5  # Base score
            
            # Adjust based on feature values
            if len(feature_array) > 0:
                # Aspect ratio check (reasonable signature proportions)
                if 0.2 < feature_array[0] < 5.0:  # aspect_ratio
                    score += 0.1
                
                # Density check (not too sparse or dense)
                if 0.01 < feature_array[1] < 0.5:  # density
                    score += 0.1
                
                # Centroid position (not too far from center)
                if 0.2 < feature_array[2] < 0.8:  # centroid_x
                    score += 0.05
                if 0.2 < feature_array[3] < 0.8:  # centroid_y
                    score += 0.05
                
                # Compactness (reasonable signature complexity)
                if 0.1 < feature_array[4] < 2.0:  # compactness
                    score += 0.1
            
            # Normalize score
            authenticity_score = min(score, 1.0)
            confidence = authenticity_score * 0.8  # Lower confidence for rule-based
            
            return authenticity_score, confidence
            
        except Exception as e:
            logger.error(f"Error in rule-based analysis: {e}")
            return 0.5, 0.3
    
    def _features_to_array(self, features: Dict) -> np.ndarray:
        """Convert features dictionary to numpy array"""
        try:
            feature_array = []
            for feature_name in self.feature_extractor.feature_names:
                feature_array.append(features.get(feature_name, 0.0))
            return np.array(feature_array)
        except Exception as e:
            logger.error(f"Error converting features to array: {e}")
            return np.zeros(len(self.feature_extractor.feature_names))
    
    def _generate_analysis_details(self, features: Dict, authenticity_score: float) -> str:
        """Generate detailed analysis report"""
        try:
            details = {
                "feature_analysis": {
                    "aspect_ratio": features.get('aspect_ratio', 0),
                    "density": features.get('density', 0),
                    "compactness": features.get('compactness', 0),
                    "eccentricity": features.get('eccentricity', 0)
                },
                "stroke_analysis": {
                    "stroke_width_mean": features.get('stroke_width_mean', 0),
                    "stroke_width_std": features.get('stroke_width_std', 0),
                    "pen_lifts": features.get('pen_lifts', 0)
                },
                "quality_indicators": {
                    "solidity": features.get('solidity', 0),
                    "convexity": features.get('convexity', 0),
                    "pressure_variation": features.get('pressure_variation', 0)
                },
                "overall_score": authenticity_score,
                "recommendation": "Authentic" if authenticity_score >= settings.CONFIDENCE_THRESHOLD else "Suspicious"
            }
            
            return json.dumps(details, indent=2)
            
        except Exception as e:
            logger.error(f"Error generating analysis details: {e}")
            return f"Analysis completed with score: {authenticity_score:.3f}"
    
    def train_model(self, training_data: List[Dict]) -> bool:
        """Train the ML model with provided data"""
        try:
            if not training_data:
                logger.warning("No training data provided")
                return False
            
            # Prepare training data
            X = []
            y = []
            
            for data in training_data:
                features = data.get('features', {})
                label = data.get('label', 0)  # 0: fake, 1: authentic
                
                feature_array = self._features_to_array(features)
                X.append(feature_array)
                y.append(label)
            
            X = np.array(X)
            y = np.array(y)
            
            if len(X) < 10:
                logger.warning("Insufficient training data")
                return False
            
            # Normalize features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.model = RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                max_depth=10
            )
            self.model.fit(X_scaled, y)
            
            # Save model
            self._save_model()
            self.is_trained = True
            
            logger.info("Model trained successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            return False
    
    def _save_model(self):
        """Save trained model and scaler"""
        try:
            os.makedirs(settings.MODEL_PATH, exist_ok=True)
            
            if self.model:
                joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    def _load_model(self):
        """Load existing model and scaler"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                self.is_trained = True
                logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.is_trained = False

# Import time and json at the top
import time
import json
