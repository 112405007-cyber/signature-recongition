import pytest
import numpy as np
from unittest.mock import Mock, patch
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

from app.services.signature_analyzer import SignatureAnalyzer
from app.services.image_processor import ImageProcessor
from app.services.feature_extractor import FeatureExtractor

class TestSignatureAnalyzer:
    """Test cases for SignatureAnalyzer"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.analyzer = SignatureAnalyzer()
        self.image_processor = ImageProcessor()
        self.feature_extractor = FeatureExtractor()
    
    def test_analyzer_initialization(self):
        """Test analyzer initialization"""
        assert self.analyzer is not None
        assert self.analyzer.feature_extractor is not None
        assert self.analyzer.image_processor is not None
    
    def test_features_to_array(self):
        """Test feature conversion to array"""
        features = {
            'aspect_ratio': 1.5,
            'density': 0.3,
            'centroid_x': 0.5,
            'centroid_y': 0.5,
            'compactness': 2.0,
            'eccentricity': 0.7,
            'solidity': 0.8,
            'convexity': 0.9,
            'stroke_width_mean': 3.0,
            'stroke_width_std': 0.5,
            'stroke_direction': 1.2,
            'curvature_mean': 0.1,
            'curvature_std': 0.05,
            'pressure_variation': 0.2,
            'pen_lifts': 2,
            'writing_speed': 0.8,
            'acceleration': 0.3
        }
        
        feature_array = self.analyzer._features_to_array(features)
        assert len(feature_array) == len(self.feature_extractor.feature_names)
        assert feature_array[0] == 1.5  # aspect_ratio
        assert feature_array[1] == 0.3  # density
    
    def test_rule_based_analysis(self):
        """Test rule-based analysis"""
        feature_array = np.array([1.5, 0.3, 0.5, 0.5, 1.2, 0.7, 0.8, 0.9, 3.0, 0.5, 1.2, 0.1, 0.05, 0.2, 2, 0.8, 0.3])
        
        score, confidence = self.analyzer._rule_based_analysis(feature_array)
        
        assert 0 <= score <= 1
        assert 0 <= confidence <= 1
        assert confidence <= score  # Confidence should be lower than score for rule-based
    
    def test_compare_with_template(self):
        """Test template comparison"""
        features = {
            'aspect_ratio': 1.5,
            'density': 0.3,
            'centroid_x': 0.5,
            'centroid_y': 0.5,
            'compactness': 2.0,
            'eccentricity': 0.7,
            'solidity': 0.8,
            'convexity': 0.9,
            'stroke_width_mean': 3.0
        }
        
        template_features = {
            'aspect_ratio': 1.4,
            'density': 0.32,
            'centroid_x': 0.48,
            'centroid_y': 0.52,
            'compactness': 1.9,
            'eccentricity': 0.68,
            'solidity': 0.82,
            'convexity': 0.88,
            'stroke_width_mean': 2.9
        }
        
        score, confidence = self.analyzer._compare_with_template(features, template_features)
        
        assert 0 <= score <= 1
        assert 0 <= confidence <= 1
        assert score > 0.5  # Should be high similarity for similar features
    
    @patch('app.services.signature_analyzer.time.time')
    def test_analyze_signature_mock(self, mock_time):
        """Test signature analysis with mocked dependencies"""
        mock_time.side_effect = [0, 1.5]  # Start time, end time
        
        # Mock image data
        mock_image_data = b'fake_image_data'
        
        # Mock image processor
        with patch.object(self.analyzer.image_processor, 'load_image') as mock_load, \
             patch.object(self.analyzer.image_processor, 'preprocess_image') as mock_preprocess, \
             patch.object(self.analyzer.feature_extractor, 'extract_all_features') as mock_extract:
            
            mock_load.return_value = np.random.rand(100, 100)
            mock_preprocess.return_value = np.random.rand(100, 100)
            mock_extract.return_value = {
                'aspect_ratio': 1.5,
                'density': 0.3,
                'centroid_x': 0.5,
                'centroid_y': 0.5,
                'compactness': 2.0,
                'eccentricity': 0.7,
                'solidity': 0.8,
                'convexity': 0.9,
                'stroke_width_mean': 3.0,
                'stroke_width_std': 0.5,
                'stroke_direction': 1.2,
                'curvature_mean': 0.1,
                'curvature_std': 0.05,
                'pressure_variation': 0.2,
                'pen_lifts': 2,
                'writing_speed': 0.8,
                'acceleration': 0.3
            }
            
            result = self.analyzer.analyze_signature(mock_image_data)
            
            assert 'authenticity_score' in result
            assert 'confidence_level' in result
            assert 'is_authentic' in result
            assert 'analysis_details' in result
            assert 'processing_time' in result
            assert 'extracted_features' in result
            
            assert 0 <= result['authenticity_score'] <= 1
            assert 0 <= result['confidence_level'] <= 1
            assert isinstance(result['is_authentic'], bool)
            assert result['processing_time'] == 1.5

class TestImageProcessor:
    """Test cases for ImageProcessor"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.processor = ImageProcessor()
    
    def test_processor_initialization(self):
        """Test processor initialization"""
        assert self.processor is not None
        assert self.processor.target_size == (224, 224)
    
    def test_get_image_properties(self):
        """Test image properties extraction"""
        # Create a test image
        test_image = np.random.rand(100, 100)
        test_image[30:70, 30:70] = 0.2  # Dark region (signature)
        
        properties = self.processor.get_image_properties(test_image)
        
        assert 'height' in properties
        assert 'width' in properties
        assert 'density' in properties
        assert 'aspect_ratio' in properties
        assert 'total_pixels' in properties
        assert 'signature_pixels' in properties
        
        assert properties['height'] == 100
        assert properties['width'] == 100
        assert properties['aspect_ratio'] == 1.0
        assert properties['total_pixels'] == 10000
        assert properties['density'] > 0

class TestFeatureExtractor:
    """Test cases for FeatureExtractor"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.extractor = FeatureExtractor()
    
    def test_extractor_initialization(self):
        """Test extractor initialization"""
        assert self.extractor is not None
        assert len(self.extractor.feature_names) > 0
    
    def test_extract_geometric_features(self):
        """Test geometric feature extraction"""
        # Create a test binary image with a simple shape
        test_image = np.zeros((100, 100))
        test_image[30:70, 30:70] = 0.2  # Rectangle shape
        
        features = self.extractor._extract_geometric_features(test_image)
        
        assert 'aspect_ratio' in features
        assert 'density' in features
        assert 'centroid_x' in features
        assert 'centroid_y' in features
        assert 'compactness' in features
        assert 'eccentricity' in features
        assert 'solidity' in features
        assert 'convexity' in features
        
        # Check reasonable values
        assert features['aspect_ratio'] > 0
        assert 0 <= features['density'] <= 1
        assert 0 <= features['centroid_x'] <= 1
        assert 0 <= features['centroid_y'] <= 1
    
    def test_features_to_json(self):
        """Test feature serialization"""
        features = {
            'aspect_ratio': 1.5,
            'density': 0.3,
            'centroid_x': 0.5
        }
        
        json_str = self.extractor.features_to_json(features)
        assert isinstance(json_str, str)
        assert 'aspect_ratio' in json_str
        assert '1.5' in json_str
    
    def test_features_from_json(self):
        """Test feature deserialization"""
        features = {
            'aspect_ratio': 1.5,
            'density': 0.3,
            'centroid_x': 0.5
        }
        
        json_str = self.extractor.features_to_json(features)
        restored_features = self.extractor.features_from_json(json_str)
        
        assert restored_features == features

if __name__ == "__main__":
    pytest.main([__file__])
