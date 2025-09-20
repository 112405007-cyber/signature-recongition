from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
import os
import uuid
from datetime import datetime
import logging

from ..models.database import get_db
from ..models.signature_model import User, SignatureTemplate, VerificationResult
from ..services.signature_analyzer import SignatureAnalyzer
from ..services.image_processor import ImageProcessor
from ..services.feature_extractor import FeatureExtractor
from ..routes.auth import get_current_active_user
from config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize services
signature_analyzer = SignatureAnalyzer()
image_processor = ImageProcessor()
feature_extractor = FeatureExtractor()

@router.post("/upload")
async def upload_signature(
    file: UploadFile = File(...),
    template_name: Optional[str] = Form(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload and analyze a signature image"""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"File type not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
            )
        
        # Check file size
        file_content = await file.read()
        if len(file_content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE} bytes"
            )
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(settings.UPLOAD_FOLDER, unique_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        # Analyze signature
        analysis_result = signature_analyzer.analyze_signature(file_content)
        
        # Save verification result to database
        verification_result = VerificationResult(
            user_id=current_user.id,
            input_image_path=file_path,
            authenticity_score=analysis_result["authenticity_score"],
            confidence_level=analysis_result["confidence_level"],
            is_authentic=analysis_result["is_authentic"],
            analysis_details=analysis_result["analysis_details"],
            processing_time=analysis_result["processing_time"]
        )
        
        db.add(verification_result)
        db.commit()
        db.refresh(verification_result)
        
        # If template_name provided, save as template
        template_id = None
        if template_name:
            template = SignatureTemplate(
                user_id=current_user.id,
                template_name=template_name,
                image_path=file_path,
                features_json=feature_extractor.features_to_json(analysis_result["extracted_features"]),
                is_verified=True
            )
            db.add(template)
            db.commit()
            db.refresh(template)
            template_id = template.id
        
        return {
            "message": "Signature analyzed successfully",
            "verification_id": verification_result.id,
            "template_id": template_id,
            "analysis_result": analysis_result,
            "file_path": f"/static/{unique_filename}"
        }
        
    except Exception as e:
        logger.error(f"Error uploading signature: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.post("/verify")
async def verify_signature(
    file: UploadFile = File(...),
    template_id: Optional[str] = Form(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Verify signature against a template"""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_content = await file.read()
        
        # Get template if provided
        template_features = None
        if template_id:
            try:
                template_id_int = int(template_id)
                template = db.query(SignatureTemplate).filter(
                    SignatureTemplate.id == template_id_int,
                    SignatureTemplate.user_id == current_user.id
                ).first()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid template_id format")
            
            if not template:
                raise HTTPException(status_code=404, detail="Template not found")
            
            template_features = feature_extractor.features_from_json(template.features_json)
        
        # Analyze signature
        analysis_result = signature_analyzer.analyze_signature(file_content, template_features)
        
        # Save verification result
        verification_result = VerificationResult(
            user_id=current_user.id,
            template_id=int(template_id) if template_id else None,
            input_image_path="",  # Don't save file for verification
            authenticity_score=analysis_result["authenticity_score"],
            confidence_level=analysis_result["confidence_level"],
            is_authentic=analysis_result["is_authentic"],
            analysis_details=analysis_result["analysis_details"],
            processing_time=analysis_result["processing_time"]
        )
        
        db.add(verification_result)
        db.commit()
        db.refresh(verification_result)
        
        return {
            "message": "Signature verification completed",
            "verification_id": verification_result.id,
            "analysis_result": analysis_result
        }
        
    except Exception as e:
        logger.error(f"Error verifying signature: {e}")
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")

@router.get("/templates")
async def get_templates(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's signature templates"""
    try:
        templates = db.query(SignatureTemplate).filter(
            SignatureTemplate.user_id == current_user.id
        ).all()
        
        return {
            "templates": [
                {
                    "id": template.id,
                    "template_name": template.template_name,
                    "image_path": template.image_path,
                    "is_verified": template.is_verified,
                    "created_at": template.created_at
                }
                for template in templates
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve templates")

@router.get("/history")
async def get_verification_history(
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's verification history"""
    try:
        results = db.query(VerificationResult).filter(
            VerificationResult.user_id == current_user.id
        ).order_by(VerificationResult.created_at.desc()).limit(limit).all()
        
        return {
            "verification_history": [
                {
                    "id": result.id,
                    "authenticity_score": result.authenticity_score,
                    "confidence_level": result.confidence_level,
                    "is_authentic": result.is_authentic,
                    "processing_time": result.processing_time,
                    "created_at": result.created_at
                }
                for result in results
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting verification history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve verification history")

@router.delete("/templates/{template_id}")
async def delete_template(
    template_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a signature template"""
    try:
        template = db.query(SignatureTemplate).filter(
            SignatureTemplate.id == template_id,
            SignatureTemplate.user_id == current_user.id
        ).first()
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Delete associated file
        if os.path.exists(template.image_path):
            os.remove(template.image_path)
        
        db.delete(template)
        db.commit()
        
        return {"message": "Template deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting template: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete template")

@router.get("/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user statistics"""
    try:
        # Count templates
        template_count = db.query(SignatureTemplate).filter(
            SignatureTemplate.user_id == current_user.id
        ).count()
        
        # Count verifications
        verification_count = db.query(VerificationResult).filter(
            VerificationResult.user_id == current_user.id
        ).count()
        
        # Count authentic signatures
        authentic_count = db.query(VerificationResult).filter(
            VerificationResult.user_id == current_user.id,
            VerificationResult.is_authentic == True
        ).count()
        
        # Average authenticity score
        avg_score = db.query(VerificationResult).filter(
            VerificationResult.user_id == current_user.id
        ).with_entities(VerificationResult.authenticity_score).all()
        
        avg_authenticity = sum([score[0] for score in avg_score]) / len(avg_score) if avg_score else 0
        
        return {
            "template_count": template_count,
            "verification_count": verification_count,
            "authentic_count": authentic_count,
            "average_authenticity_score": round(avg_authenticity, 3)
        }
        
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")
