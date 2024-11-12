from fastapi import APIRouter, HTTPException, Header
import base64
from io import BytesIO
from apps.calculator.utils import analyze_image
from schema import ImageData
from PIL import Image
from constants import AUTH_TOKEN
from typing import Optional

router = APIRouter()

@router.post('')
async def run(data: ImageData, authorization: Optional[str] = Header(None)):
    try:
        # Check authorization header
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header missing")
        
        # Extract token from Bearer format
        token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
        
        # Verify token
        print('token: ', token)
        if token != AUTH_TOKEN:

            raise HTTPException(status_code=401, detail="Invalid authorization token")
        
        image_data = base64.b64decode(data.image.split(",")[1])
        image_bytes = BytesIO(image_data)
        image = Image.open(image_bytes)
        responses = analyze_image(image, dict_of_vars=data.dict_of_vars)
        
        # Ensure responses is a list of dictionaries with all required fields
        if not responses or not isinstance(responses, list):
            responses = [{
                'expr': 'Error processing input',
                'result': 'Unable to analyze',
                'explanation': 'Invalid response format from analysis.',
                'basic_concepts': 'Mathematical problem-solving basics.',
                'practice_questions': ['Can you identify the problem?'],
                'quiz_questions': []
            }]
        
        return {
            "message": "Image processed",
            "data": responses,  # This should now be a list of properly formatted dictionaries
            "status": "success"
        }
    
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return {
            "message": "Error processing image",
            "data": [{
                'expr': 'Error occurred',
                'result': 'Processing failed',
                'explanation': str(e),
                'basic_concepts': 'Error occurred during processing.',
                'practice_questions': ['Please try again.'],
                'quiz_questions': []
            }],
            "status": "error"
        }
