import google.generativeai as genai
import ast
import json
from PIL import Image
from constants import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

def analyze_image(img: Image, dict_of_vars: dict):
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    dict_of_vars_str = json.dumps(dict_of_vars, ensure_ascii=False)
    prompt = (
        f"You have been given an image with some mathematical expressions, equations, or graphical problems, and you need to solve them. "
        f"Note: Use the PEMDAS rule for solving mathematical expressions. PEMDAS stands for the Priority Order: Parentheses, Exponents, Multiplication and Division (from left to right), Addition and Subtraction (from left to right). "
        f"1. Simple mathematical expressions like `2 + 2`, `3 * 4`, `5 / 6`, etc.: Solve and return in the format: "
        f"[{{'expr': expression, 'result': answer, 'explanation': detailed explanation in Markdown}}]. "
        f"2. Set of Equations like `x^2 + 2x + 1 = 0`, `3y + 4x = 0`, etc.: Solve for each variable, and return each variable with detailed solution steps using Markdown formatting in 'explanation'. "
        f"3. Variable Assignments like `x = 4`, `y = 5`, etc.: Assign values, return each variable with an explanation using Markdown, e.g., 'Assigning value of 4 to x'. "
        f"4. Graphical Problems: Provide a thorough Markdown-formatted explanation for problems shown in graphical form, such as cars colliding, trigonometric problems, etc. "
        f"5. Abstract Concepts: Analyze and explain concepts shown in drawings, using Markdown for clarity. Return in the format: "
        f"[{{'expr': description, 'result': concept, 'explanation': detailed Markdown explanation}}]. "
        f"Use extra backslashes for escape characters like \\f -> \\\\f, \\n -> \\\\n, etc. "
        f"Here is a dictionary of user-assigned variables. If the given expression has any of these variables, use its actual value: {dict_of_vars_str}. "
    )
    
    response = model.generate_content([prompt, img])
    print(response.text)
    answers = []
    try:
        answers = ast.literal_eval(response.text)
    except Exception as e:
        print(f"Error in parsing response from Gemini API: {e}")
    print('returned answer ', answers)
    for answer in answers:
        if 'assign' in answer:
            answer['assign'] = True
        else:
            answer['assign'] = False
    return answers
