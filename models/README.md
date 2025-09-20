# Models Directory

This directory contains machine learning models and related files for the Signature Recognition System.

## Structure

```
models/
└── trained_models/     # Trained ML models
    ├── signature_model.pkl    # Main signature verification model
    ├── scaler.pkl            # Feature scaler
    └── model_metadata.json   # Model information
```

## Model Files

### signature_model.pkl
- **Type**: Random Forest Classifier
- **Purpose**: Binary classification (authentic vs fake signatures)
- **Features**: 17 signature features including geometric, stroke, and texture features
- **Training**: Uses scikit-learn's RandomForestClassifier

### scaler.pkl
- **Type**: StandardScaler
- **Purpose**: Normalizes feature values for consistent model input
- **Method**: Z-score normalization (mean=0, std=1)

### model_metadata.json
- **Purpose**: Stores model information and performance metrics
- **Contents**:
  - Model version
  - Training date
  - Accuracy scores
  - Feature importance
  - Training data statistics

## Model Training

The signature verification model is trained using:

1. **Feature Extraction**: 17 different signature features
2. **Data Preprocessing**: Normalization and scaling
3. **Model Selection**: Random Forest for robustness
4. **Validation**: Cross-validation for performance assessment

## Features Used

### Geometric Features
- Aspect ratio
- Density
- Centroid position
- Compactness
- Eccentricity
- Solidity
- Convexity

### Stroke Features
- Stroke width (mean, std)
- Stroke direction
- Curvature (mean, std)

### Dynamic Features
- Pressure variation
- Pen lifts
- Writing speed
- Acceleration

### Texture Features
- Local Binary Pattern
- Gradient statistics

## Model Performance

Expected performance metrics:
- **Accuracy**: >85%
- **Precision**: >80%
- **Recall**: >80%
- **F1-Score**: >80%

## Usage

Models are automatically loaded when the SignatureAnalyzer is initialized:

```python
analyzer = SignatureAnalyzer()
# Models are loaded from models/trained_models/
```

## Retraining

To retrain the model with new data:

1. Collect labeled signature data
2. Extract features using FeatureExtractor
3. Train new model using SignatureAnalyzer.train_model()
4. Save updated models

## Security

- Models are stored locally for privacy
- No signature data is sent to external services
- All processing happens on-premises
