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
        if token != AUTH_TOKEN:
            raise HTTPException(status_code=401, detail="Invalid authorization token")
        
        image_data = base64.b64decode(data.image.split(",")[1])
        image_bytes = BytesIO(image_data)
        image = Image.open(image_bytes)
        responses = analyze_image(image, dict_of_vars=data.dict_of_vars)
        print('responses: ', responses)
        data = []
        for response in responses:
            data.append(response)
        
        print('responses in route: ', responses)
        return {"message": "Image processed", "data": data, "status": "success"}
    
    except HTTPException as he:
        # Re-raise HTTP exceptions
        raise he
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return {"message": "Error processing image", "data": [], "status": "error", "error": str(e)}
