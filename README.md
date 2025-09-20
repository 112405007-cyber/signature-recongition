# Signature Recognition System

A comprehensive signature verification system that can detect whether a signature is original or fake using machine learning and computer vision techniques.

## Project Structure

```
signature-recognition/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── signature_model.py
│   │   │   └── database.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── image_processor.py
│   │   │   ├── feature_extractor.py
│   │   │   └── signature_analyzer.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   └── signature.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── helpers.py
│   ├── requirements.txt
│   └── config.py
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── main.js
│   │   └── signature-scanner.js
│   └── assets/
│       └── images/
├── data/
│   ├── templates/
│   └── test_signatures/
├── models/
│   └── trained_models/
└── tests/
    ├── test_backend/
    └── test_frontend/
```

## Features

- **Image Upload & Processing**: Upload signature images for analysis
- **Feature Extraction**: Extract key features from signatures
- **Machine Learning Analysis**: Use trained models to verify authenticity
- **Real-time Results**: Get instant feedback on signature authenticity
- **Template Matching**: Compare against known signature templates
- **User Authentication**: Secure access to the system

## Installation

1. Clone the repository
2. Install backend dependencies: `pip install -r backend/requirements.txt`
3. Run the backend server: `python backend/app/main.py`
4. Open `frontend/index.html` in your browser

## Usage

1. Upload a signature image
2. The system will analyze the signature
3. Get results showing authenticity score and confidence level
4. View detailed analysis of signature features

## Technology Stack

- **Backend**: Python, FastAPI, OpenCV, scikit-learn, SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript
- **ML/AI**: TensorFlow, OpenCV, NumPy, Pandas
- **Database**: SQLite (development), PostgreSQL (production)
