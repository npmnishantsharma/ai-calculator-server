from pydantic import BaseModel

class ImageData(BaseModel):
    image: str
    dict_of_vars: dict

class QuizRequest(BaseModel):
    topic: str
    concepts: str
    number_of_questions: int = 15
