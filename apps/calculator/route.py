from fastapi import APIRouter
import base64
from io import BytesIO
from apps.calculator.utils import analyze_image
from schema import ImageData
from PIL import Image
from constants import AUTH_TOKEN
router = APIRouter()

@router.post('')
async def run(data: ImageData):
    try:
        #check headers
        if data.headers.get("Authorization") != f'Bearer {AUTH_TOKEN}':
            return {"message": "Unauthorized", "data": [], "status": "error"}
        
        image_data = base64.b64decode(data.image.split(",")[1])  # Assumes data:image/png;base64,<data>
        image_bytes = BytesIO(image_data)
        image = Image.open(image_bytes)
        responses = analyze_image(image, dict_of_vars=data.dict_of_vars)
        print('responses: ', responses)
        data = []
        for response in responses:
            data.append(response)
        
        print('responses in route: ', responses)
        return {"message": "Image processed", "data": data, "status": "success"}
    
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return {"message": "Error processing image", "data": [], "status": "error", "error": str(e)}
